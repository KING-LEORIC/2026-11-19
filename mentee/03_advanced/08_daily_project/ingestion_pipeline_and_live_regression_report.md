# \[Day24 실습 08 Advanced\] 오프라인 준비 및 `--live-db` 통합 실행 보고서

## 1. 개요 및 실행 정보

* **실습 주제:** Day24 실습 08 Advanced · 오프라인 준비 + `--live-db` 실제 통합 실행

* **실행 대상:** `C:\workspace\2026-11-19\mentee\03_advanced\08_daily_project\main.py --live-db`

* **결과 파일:** `C:\workspace\2026-11-19\mentee\03_advanced\08_daily_project\outputs\ingestion_report.json`

* **수행 단계 요약:**

  1. `manifest.json` 검증 및 `doc_id` 기준 정렬 (`read_manifest`)

  2. 문서 파싱·정제·청킹·스팬 검증 및 정상 청크 준비 (`prepare_all`)

  3. E5 인코더 모델 로드 및 청크 배치 임베딩 생성 (`embed_batches`)

  4. PostgreSQL(`d24_adv08`) 스키마 초기화, 문서별 트랜잭션 스테이징 및 `v1` 공개 (`save_and_publish`)

  5. `attendance_v2.md` 기반 `v2` 버전 회귀 테스트(실패 주입/롤백 검증 → 재시도 공개) (`regression_v2`)

  6. `'학사'` 카테고리(`k=3`) 대상 현재 공개 버전 검색 및 인용 메타데이터 집계 (`make_final_report`)

## 2. 원문 및 데이터 출처

### 2.1 매니페스트 구성 (`manifest.json`)

총 **6개 문서**가 등록되어 있으며, 파싱 및 청킹 단계를 거쳐 **4개 문서(`parsed`)**가 준비되었고 **2개 문서(`needs_ocr`, `unsupported`)**는 적재 대상에서 제외되었습니다.

| `doc_id` | 원문 파일 (`file`) | 카테고리 | 초기 버전 | 처리 상태 분류 | 준비 포함 여부 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `DOC-ASSIGN` | `assignment.txt` | 학사 | `v1` | `parsed` | 포함 (`prepared_doc_ids`) |
| `DOC-ATTEND` | `attendance.md` | 학사 | `v1` | `parsed` | 포함 (`prepared_doc_ids`) |
| `DOC-CAREER` | `career.pdf` | 지원 | `v1` | `parsed` | 포함 (`prepared_doc_ids`) |
| `DOC-FACILITY` | `facility.html` | 시설 | `v1` | `parsed` | 포함 (`prepared_doc_ids`) |
| `DOC-SCAN` | `scan.pdf` | 안내 | `v1` | `needs_ocr` | 미포함 (OCR 필요 상태) |
| `DOC-UNSUPPORTED` | `unsupported.xyz` | 기타 | `v1` | `unsupported` | 미포함 (미지원 확장자) |

### 2.2 개정 버전 원문 (`versions/attendance_v2.md`)

`regression_v2` 단계에서 `DOC-ATTEND`의 개정 원문으로 사용된 `attendance_v2.md`는 출석 안내 규정으로 구성되어 있습니다.

* **## 지각과 결석:** 수업 시작 후 15분까지 입실 시 지각, 15분 초과 시 결석 기록(단, 사전 승인 시 운영실 확인)

* **## 출석 문의:** 출석 기록 오류 시 운영실 문의

## 3. 실행 결과 분석 (`ingestion_report.json`)

### 3.1 문서 준비 및 초기 `v1` 공개 결과

* **`source_mode`:** `"e5_pgvector_live"`

* **문서 집계:** 전체 `6`건 중 `parsed: 4`, `needs_ocr: 1`, `unsupported: 1`

* **청크 집계:** 정상 파싱 4개 문서에서 총 `6`개 청크(`prepared_chunk_count: 6`) 생성

* **초기 공개(`live.published`):** `DOC-ASSIGN`, `DOC-ATTEND`, `DOC-CAREER`, `DOC-FACILITY` 4개 문서 모두 `published_version: "v1"`으로 커밋 완료

### 3.2 `v2` 버전 회귀 및 롤백 검증 (`live.revision`)

```json
{
  "before": "v1",
  "after_failure": "v1",
  "after_retry": "v2"
}
```

* 트랜잭션 커밋 직전 의도적 예외(`injected_failure_before_commit`)를 발생시킨 뒤 롤백을 수행한 결과, 공개 포인터가 `"v1"`으로 유지(`after_failure: "v1"`)되어 실패한 변경이 노출되지 않음을 확인했습니다.

* 이후 재시도 트랜잭션에서 스테이징 및 공개가 정상 커밋되어 최종 포인터가 `"v2"`(`after_retry: "v2"`)로 전환되었습니다.

### 3.3 벡터 검색 및 인용 결과 (`live.hits`, 질의: `"출석 기준을 알려 주세요"`, 카테고리: `"학사"`, `k=3`)

1. **1순위 (`citation_id: 10`, `cosine_distance: 0.1241`):** `DOC-ATTEND` (`v2`, `attendance_v2.md#sec-2`) — 출석 기록 오류 문의 안내 청크

2. **2순위 (`citation_id: 9`, `cosine_distance: 0.1493`):** `DOC-ATTEND` (`v2`, `attendance_v2.md#sec-1`) — 15분 지각/초과 결석 기준 청크

3. **3순위 (`citation_id: 1`, `cosine_distance: 0.2043`):** `DOC-ASSIGN` (`v1`, `assignment.txt`) — 과제 보관·제출 기한 안내 청크

* `DOC-ATTEND` 검색 결과가 모두 `source_version: "v2"`로 반환되어, 버전 전환 후 구버전(`v1`) 청크가 현재 검색 결과에 섞이지 않음을 확인했습니다.

## 4. 한계점 및 운영 메모

* **소규모 데이터 및 청크 수:** 전체 6개 문서·6개 청크 규모의 실습 데이터셋을 대상으로 수행되었으므로, 대규모 문서 코퍼스에서의 인덱싱 성능, 다중 청크 분할 경계, 대량 동시 트랜잭션 부하를 대표하지는 못합니다.

* **검색 필터 제한:** 검색 검증이 `category="학사"`, `k=3` 조건으로 수행되어 `'시설'`, `'지원'` 등 다른 카테고리 문서의 검색 랭킹이나 전체 상위 결과 분포는 별도로 검증되지 않았습니다.

* **PDF 파싱 및 환경 경고 로그:**

  * PDF 파싱 과정에서 `incorrect startxref pointer(1)`, `parsing for Object Streams` 경고가 출력되었습니다.

  * Hugging Face Hub 익명 요청 안내(`HF_TOKEN` 미설정) 및 `get_sentence_embedding_dimension` deprecation 경고가 발생했으나 실행 결과 생성에는 영향을 주지 않았습니다.

* **기대 기준 대조 필요:** 최종 제출 전 세부 항목과 스키마 요건은 `expected/EXPECTED.md`와 대조하여 누락 여부를 확인해야 합니다.

## 5. 결론

08 Advanced `--live-db` 실행을 통해 매니페스트 검증부터 오프라인 파싱·청킹·스팬 검증, E5 임베딩 생성, PostgreSQL 트랜잭션 기반 `v1` 공개 및 `v2` 롤백/재시도 전환, 버전 정합성이 유지된 벡터 검색 및 인용(`citation_id`, `source_locator`) 반환까지의 통합 파이프라인 동작을 확인했습니다.