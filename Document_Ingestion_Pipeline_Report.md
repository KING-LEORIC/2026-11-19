# Document Parsing · Chunking · Indexing Pipeline 보고서

## 1. 목적

원본 문서를 AI가 검색할 수 있는 문서 조각(Chunk)과 벡터 데이터로 변환하고, 출처와 원문 위치를 추적할 수 있도록 저장·공개하는 과정을 정리한다.

**전체 데이터 흐름**

`Storage(Raw File) → ParsedUnit → CleanUnit → Chunk → E5 → pgvector → Retriever`

**처리 절차**

`Parsing → Cleaning → Chunking → 검증 → E5 → Staging·Publish → Retrieve`

## 2. 처리 절차

### ① 원본 문서 보관(Storage: Raw File)

먼저 TXT·Markdown·HTML·PDF 등의 원본 파일을 수집해 Raw File로 보관한다. Manifest에 문서 ID(`doc_id`), 버전(`source_version`), 파일 위치와 상태 등을 기록하고, SHA-256으로 원본 파일의 변경 여부를 확인한다. 원본은 이후 처리 결과와 분리해 보존한다.

**결과:** 원본 파일과 문서 관리 정보(Manifest, `raw_sha256`)

### ② Parsing: 원본에서 내용 추출(ParsedUnit)

파일 형식에 맞는 방법으로 내용을 읽는다. TXT는 UTF-8로 디코딩하고, Markdown은 제목과 본문 구조를 보존한다. HTML은 본문 영역과 표를 구분하며, PDF는 페이지별 텍스트를 추출하고 페이지 위치를 기록한다. 이미지로 된 스캔 PDF는 별도 OCR이 필요하므로 일반 텍스트 PDF와 구분한다.

추출한 텍스트는 `raw_text`로 보관하고, 문서 ID·처리 단위·페이지 번호·원문 위치(`source_locator`) 등을 함께 기록해 `ParsedUnit`으로 만든다.

**결과:** 원문에서 추출한 텍스트와 페이지·구조·위치 정보(ParsedUnit)

### ③ Cleaning: 텍스트 정리(CleanUnit)

추출한 텍스트의 줄바꿈과 불필요한 공백을 정리하고 Unicode를 NFC로 정규화한다. 이때 숫자, 부정 표현, 조건, 문단과 제목의 관계 등 원문의 의미와 구조는 유지한다. 정리된 결과는 `clean_text`로 보관하고, 정제 규칙의 버전과 `clean_hash`도 기록한다.

**결과:** 의미와 구조를 보존해 정리한 텍스트(CleanUnit)

### ④ Chunking: 검색 단위로 분할(Chunk)

CleanUnit을 검색에 적합한 크기의 여러 Chunk로 나눈다. 문서의 제목·절·문단 구조를 우선 고려하고, 긴 내용은 문자 구간과 E5 Token 한도를 확인하며 추가로 분할한다. 필요하면 인접 Chunk 사이에 Overlap을 둔다.

각 Chunk에는 본문뿐 아니라 원문에서의 문자 시작·끝 위치(`[start, end)`), 문서 ID, 버전, 절 등의 정보를 연결한다.

**결과:** 검색에 사용할 Chunk와 원문 위치 정보(Span)

### ⑤ Chunk 검증(Validation)

E5로 변환하기 전에 Chunk가 정상적으로 만들어졌는지 확인한다.

- **Span:** Chunk 본문이 기록된 문자 위치의 원문과 일치하는지 확인한다.
- **Token 길이:** `passage:`와 제목 등 실제 임베딩 입력 전체가 E5의 입력 한도를 넘지 않는지 확인한다.
- **Coverage:** 원문에서 빠진 문자 구간이 없는지 확인한다.
- **Duplication:** 의도한 Overlap과 잘못 생성된 중복을 구분한다.
- **Metadata·Embedding 계약:** 문서 출처·버전·위치 정보가 연결되고, 임베딩 결과의 차원 등 저장 조건을 만족하는지 확인한다.

검증을 통과한 Chunk만 다음 임베딩 단계로 보낸다. 실패한 항목은 원인을 기록하고 보류하거나 재분할한다.

**결과:** 검증을 통과한 Chunk와 검증 상태·오류 기록

### ⑥ E5: Chunk를 벡터로 변환

검증된 각 Chunk의 임베딩 입력 앞에 `passage:`를 붙여 E5-small 모델에 전달한다. 모델은 문장 내용을 384차원 벡터로 변환한다. 이 벡터는 문장의 의미를 숫자 배열로 표현한 것으로, 이후 질문과 문서의 의미적 유사도를 검색하는 데 사용한다.

**결과:** 각 Chunk에 대응하는 384차원 Embedding 벡터

### ⑦ Staging·Publish: pgvector에 저장하고 공개

Chunk 본문, Embedding, 출처·버전·원문 위치 정보를 PostgreSQL의 pgvector 테이블에 적재한다. 새 문서 버전은 먼저 `staging` 상태로 준비하고, Chunk 수와 검증 결과 등을 확인한 뒤 `ready`로 표시한다. 검증이 통과하면 Transaction 안에서 현재 공개 버전 포인터를 새 버전으로 변경해 `published` 상태로 공개한다.

이렇게 하면 새 버전 처리에 실패했을 때 기존 공개 버전을 유지할 수 있다.

**결과:** pgvector에 저장되고 현재 검색 대상으로 공개된 Chunk·벡터·출처 정보

### ⑧ Retrieve: 질문과 가까운 Chunk 검색

사용자 질문을 `query:` 접두어와 함께 E5로 임베딩하고, pgvector에서 현재 공개된 문서의 벡터를 대상으로 Top-k 검색을 수행한다. 검색된 Chunk의 본문과 출처, 원문 위치를 확인해 질문과 관련된 근거를 회수한다.

**결과:** 검색된 Chunk의 `citation_id`, `chunk_id`, `body`, `source_locator` 등과 유사도 검색 결과

## 3. 처리 상태 예시

교안의 74쪽은 기본 문서 5건과 지원하지 않는 형식 테스트 1건을 합쳐 총 6건을 처리하는 **가상 시나리오**를 제시한다.

| 처리 상태 | 건수 | 의미 |
|---|---:|---|
| `parsed` | 4 | 정상적으로 Parsing된 문서 |
| `needs_ocr` | 1 | 스캔 PDF로 OCR이 필요한 문서 |
| `unsupported` | 1 | 지원하지 않는 파일 형식 |
| **합계** | **6** | 전체 입력 문서 |

이 수치는 교안의 시뮬레이션 사례이며, 실제 파일이나 PostgreSQL을 실행해 얻은 실험 결과는 아니다. 실제 보고서에는 실행 환경에서 확인한 처리 건수와 공개·검색 결과를 별도로 기록해야 한다.

## 4. 결론

Document Parsing · Chunking · Indexing Pipeline은 원본 파일을 그대로 보관하면서 내용을 추출·정리하고, 검색 가능한 크기로 분할한 뒤 품질을 검증하여 E5 벡터와 함께 pgvector에 저장·공개하는 절차다. 마지막으로 Retriever가 질문과 관련된 Chunk와 출처 위치를 검색한다. 각 단계에서 원문과 Chunk, 벡터, 출처 정보가 끊기지 않고 연결되어야 검색 결과를 확인하고 추적할 수 있다.
