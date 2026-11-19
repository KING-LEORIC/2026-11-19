"""실습 04 Advanced · 구조 우선, 긴 부분 재분할; --live-e5는 모델 길이 측정."""
# 파일 경로 처리 기능 사용
# - Path : 파일 및 디렉터리 경로 관리
from pathlib import Path
# 해시 및 시스템 환경 제어 기능 사용
# - hashlib : 해시 생성 지원
# - sys : 모듈 검색 경로 및 명령행 인자 접근
import hashlib,sys
# 현재 실습 파일 경로 조회
# - 결과 파일 저장 위치 계산
# - 상대 경로 계산 기준
HERE=Path(__file__).resolve().parent
# 상위 디렉터리 모듈 경로 등록
# - coursekit 패키지 import 가능
sys.path.insert(0,str(HERE.parents[1]))
# 결과 저장 및 완료 출력 기능 사용
# - save_json : JSON 파일 저장
# - show_success : 실행 완료 메시지 출력
from coursekit.io import save_json,show_success
# 문서 조회 및 파싱 기능 사용
# - by_doc : 문서 ID 기반 원문 조회
# - parse_one : 문서 파싱 수행
from coursekit.documents import by_doc,parse_one
# 텍스트 정제 및 청킹 유틸리티 기능 사용
# - clean_prose : 본문 텍스트 정제
# - char_windows : 문자 기준 슬라이딩 윈도우 생성
# - build_chunk : 청크 레코드 조립
# - token_len : 모델 토크나이저 기준 토큰 길이 계산
from coursekit.processing import clean_prose,char_windows,build_chunk,token_len

"""문단 구조를 우선 보존하면서 초과 길이 문단을 재분할하고, 임베딩 입력 구성 및 토큰 길이 검증을 수행하는 모듈"""

# 문단 Span 추출 함수
# - 개행 기준 문단 분리 및 공백 문단 건너뛰기
# - 원본 텍스트 내 정확한 시작·종료 오프셋 계산
def paragraph_spans(text:str)->list[dict]:
    # BEGIN D24-04-A01
    # TODO D24-04-A01 : 문단 경계 후보를 찾아 원문 구간을 정확히 추출합니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # TODO를 완성한 뒤 아래 NotImplementedError 줄을 삭제합니다.

    # 결과 목록 및 탐색 커서 초기화
    result = []
    cursor = 0
    # 줄바꿈 기준 문단 순회
    for para in text.split('\n'):
        # 빈 문단 및 공백만 있는 줄 건너뛰기
        # - 커서를 문단 길이와 개행 문자(1자)만큼 전진
        if not para.strip(): cursor += len(para) + 1; continue
        # 현재 커서 이후에서 문단 위치 탐색
        index = text.find(para,cursor)
        # 위치 불일치 방어 처리
        if index < 0: raise ValueError('paragraph position mismatch')
        # 문단 범위 및 텍스트 저장
        result.append({'char_start' : index, 'char_end' : index+len(para), 'text' : para})
        # 다음 탐색을 위해 커서 이동
        cursor = index + len(para) + 1
    # 추출된 문단 Span 목록 반환
    return result
    # raise NotImplementedError("D24-04-A01 TODO 미완성")
    # END D24-04-A01

# 긴 문단 재분할 함수
# - 기준 길이 이하 문단은 그대로 유지
# - 기준 초과 문단은 문자 창(char_windows)으로 분할 후 전체 텍스트 오프셋 환산
def split_long(text:str,spans:list[dict],size=90,overlap=15)->list[dict]:
    # BEGIN D24-04-A02
    # TODO D24-04-A02 : 긴 문단만 문자 창으로 재분할하며 짧은 문단은 그대로 유지합니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # TODO를 완성한 뒤 아래 NotImplementedError 줄을 삭제합니다.

    # 분할 결과 저장 리스트 초기화
    out = []
    # 각 문단 Span 순회
    for s in spans:
        # 기준 길이(size) 이하 문단 유지
        if len(s['text']) <= size:
            out.append(s)
        # 기준 길이 초과 문단 재분할 처리
        else:
            # 문단 텍스트 기준 문자 윈도우 생성
            for w in char_windows(s['text'], size, overlap):
                # 전체 텍스트 기준 시작/종료 인덱스 계산
                a = s['char_start'] + w['char_start']
                b = s['char_start'] + w['char_end']
                # 분할된 구간 레코드 추가
                out.append({'char_start' : a, 'char_end' : b, 'text' : text[a : b]})
    # 최종 Span 목록 반환
    return out
    # raise NotImplementedError("D24-04-A02 TODO 미완성")
    # END D24-04-A02

# 청크 레코드 생성 함수
# - 문서/유닛/정제 텍스트/Span 정보를 결합해 청크 객체 생성
def make_records(doc:dict,unit:dict,clean:str,spans:list[dict])->list[dict]:
    # BEGIN D24-04-A03
    # TODO D24-04-A03 : 각 Span을 doc_id·unit_id·source_locator에 연결해 Chunk를 만듭니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # TODO를 완성한 뒤 아래 NotImplementedError 줄을 삭제합니다.

    # Span별 청크 생성 및 반환
    return [build_chunk(doc, unit, clean, s) for s in spans]
    # raise NotImplementedError("D24-04-A03 TODO 미완성")
    # END D24-04-A03

# 임베딩 입력 문자열 구성 함수
# - 선택적 섹션 제목 결합 여부 판단
# - 'passage: ' 접두사를 붙여 임베딩 입력 생성
def embedding_input(chunk:dict,include_title:bool)->str:
    # BEGIN D24-04-A04
    # TODO D24-04-A04 : 본문과 선택적 제목을 합쳐 `passage: ` 입력을 만들고 Offset과 분리합니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # TODO를 완성한 뒤 아래 NotImplementedError 줄을 삭제합니다.

    # 섹션 제목 추출 및 공백 정리
    title = chunk.get('section_title', '').strip()
    # 제목 포함 옵션 및 유효 제목 여부에 따른 본문 조합
    body = (title + '\n' + chunk['body']) if include_title and title else chunk['body']
    # 임베딩 모델용 passage 접두사 결합 반환
    return 'passage: ' + body
    # raise NotImplementedError("D24-04-A04 TODO 미완성")
    # END D24-04-A04

# 모델 최대 토큰 길이 검사 함수
# - 모델 미제공 시 미실행 상태 반환
# - 청크별 토큰 수 측정 후 최대 길이 초과 항목 격리 대상 수집
def check_model_lengths(chunks:list[dict],model=None)->dict:
    # BEGIN D24-04-A05
    # TODO D24-04-A05 : 모델이 제공되면 Tokenizer로 길이를 측정하고 초과 결과를 격리합니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # TODO를 완성한 뒤 아래 NotImplementedError 줄을 삭제합니다.

    # 모델 미주입 시 실행 생략 반환
    if model is None: return {'status' : 'not_run', 'checked' : 0, 'oversize_ids' : []}
    # 초과 청크 ID 수집 리스트 초기화
    overs = []
    # 각 청크의 토큰 길이 측정 및 최대 시퀀스 길이 비교
    for chunk in chunks:
        t = embedding_input(chunk, True)
        # 최대 길이 초과 시 격리 대상 ID 기록
        if token_len(model, t) > model.max_seq_length: overs.append(chunk['chunk_id'])
    # 길이 검사 결과 요약 반환
    # - 초과 항목 존재 여부에 따라 pass 또는 quarantine 판정
    return {'status' : 'pass' if not overs else 'quarantine',
            'checked' : len(chunks), 'oversize_ids' : overs}
    # raise NotImplementedError("D24-04-A05 TODO 미완성")
    # END D24-04-A05

# 청킹 재현성 검증 함수
# - 동일 정제 텍스트 기준 청킹 파이프라인 2회 실행
# - 청크 ID, 시작/종료 위치, 본문 일치 여부 검증
def check_repeat(doc:dict,unit:dict)->dict:
    # BEGIN D24-04-A06
    # TODO D24-04-A06 : 동일 원문·설정의 재실행에서 Chunk ID·본문·문자 범위가 동일한지 검사합니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # TODO를 완성한 뒤 아래 NotImplementedError 줄을 삭제합니다.

    # 유닛 원문 정제 수행
    clean = clean_prose(unit['raw_text'])
    # 문단 추출 -> 긴 문단 분할 -> 청크 생성 파이프라인 정의
    def make():
        return make_records(doc, unit, clean, split_long(clean, paragraph_spans(clean)))
    # 1차 및 2차 청킹 실행
    first = make()
    second = make()
    # 비교용 핵심 필드(ID, 오프셋, 본문) 추출
    a = [(r['chunk_id'], r['char_start'], r['char_end'], r['body']) for r in first]
    b = [(r['chunk_id'], r['char_start'], r['char_end'], r['body']) for r in second]
    # 불일치 시 불안정 청킹 예외 발생
    if a != b: raise ValueError('unstable chunking')
    # 청크 목록 및 안정성 플래그 반환
    return {'chunks' : first, 'stable' : True}
    # raise NotImplementedError("D24-04-A06 TODO 미완성")
    # END D24-04-A06

# 프로그램 진입 함수
# - 대상 문서/유닛 파싱 및 재현성 청킹 실행
# - --live-e5 옵션 시 인코더 로드 및 토큰 길이 검사 수행
# - 결과 JSON 저장 및 완료 출력
def main():
    # 출결 문서 조회 및 첫 번째 유닛 추출
    doc=by_doc('DOC-ATTEND');unit=parse_one(doc)['units'][0]
    # 청킹 생성 및 재현성 검증 실행
    result=check_repeat(doc,unit)
    # 라이브 인코더 객체 초기화
    model=None
    # --live-e5 플래그 전달 시 실제 인코더 모델 로드
    if '--live-e5' in sys.argv:
        from coursekit.live import load_encoder
        model=load_encoder()
    # 청크 토큰 길이 검사 결과 및 입력 계약 정보 기록
    result['token_check']=check_model_lengths(result['chunks'],model)
    result['embedding_input_contract']='passage: [optional title] + body'
    # 결과 JSON 저장 및 완료 메시지 출력
    out=save_json(HERE,'structure_chunks.json',result)
    show_success('04 Advanced',out)

"""
문서 원문의 문단 경계와 오프셋을 유지한 채 길이가 긴 문단만 문자 창으로 재분할하도록 구현하였다.
임베딩 입력용 passage 구성과 청크 오프셋을 분리하고, 재실행 시 청크 구조의 일관성을 검증하였으며, 
선택적 live 인코더 연계를 통한 토큰 길이 초과 검사까지 결합하여 안정적인 청킹 파이프라인을 구축하였다.
"""