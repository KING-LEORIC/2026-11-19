"""실습 03 Advanced · 구조별 정제 정책과 실패 회귀."""
# 파일 경로 처리 기능 사용
# - Path : 파일 및 디렉터리 경로 관리
from pathlib import Path
# 해시, 정규식, 시스템 환경 및 유니코드 정규화 기능 사용
# - hashlib : SHA-256 해시 생성
# - re : 정규표현식 처리
# - sys : 모듈 검색 경로 설정
# - unicodedata : 유니코드 정규화 지원
import hashlib,re,sys,unicodedata
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
# 본문 정제 기능 사용
# - clean_prose : 일반 텍스트 NFC 정규화 및 공백 정리
from coursekit.processing import clean_prose
# 문서 조회 및 파싱 기능 사용
# - by_doc : 문서 ID 기반 원문 조회
# - parse_one : 문서 파싱 수행
from coursekit.documents import by_doc,parse_one

"""블록 유형별 텍스트 정제 정책을 선택하고 핵심 정보 누락 및 멱등성을 검증하여 감사 보고서를 생성하는 모듈"""

# 정제 정책 선택 함수
# - 블록 유형 유효성 검사
# - prose는 nfc_prose, 그 외 구조는 preserve_structure 선택
def choose_policy(block_type:str)->str:
    # BEGIN D24-03-A01
    # TODO D24-03-A01 : 본문 유형 prose/code/table을 구분해 정제 정책을 선택합니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # TODO를 완성한 뒤 아래 NotImplementedError 줄을 삭제합니다.

    # 지원 블록 유형 검사
    # - 허용되지 않은 유형이면 ValueError 발생
    if block_type not in ('prose', 'code', 'table'): raise ValueError('unknown block')
    # 정책 이름 반환
    # - 일반 본문(prose)은 nfc_prose, 코드/표는 구조 보존 정책 적용
    return 'nfc_prose' if block_type == 'prose' else 'preserve_structure'
    # raise NotImplementedError("D24-03-A01 TODO 미완성")
    # END D24-03-A01

# 블록 단위 정제 함수
# - 선택된 정책에 따른 정제 분기 처리
# - 비정제 구조는 개행 문자만 LF 기준으로 통일
def clean_block(text:str,block_type:str)->str:
    # BEGIN D24-03-A02
    # TODO D24-03-A02 : 일반 본문에만 NFC·LF·가로 공백 축약을 수행하고 코드·표 구조를 보존합니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # TODO를 완성한 뒤 아래 NotImplementedError 줄을 삭제합니다.

    # 블록 유형별 정제 정책 조회
    policy = choose_policy(block_type)
    # 일반 본문 정제 수행
    # - clean_prose로 NFC 및 공백 정제 적용
    if policy == 'nfc_prose': return clean_prose(text)
    # 구조 보존 대상 개행 정규화
    # - CRLF/CR을 LF('\n')로 통일하여 구조 유지
    return text.replace('\r\n', '\n').replace('\r', '\n')
    # raise NotImplementedError("D24-03-A02 TODO 미완성")
    # END D24-03-A02

# 핵심 표현 보존 검증 함수
# - 원본에 존재하던 필수 구문이 정제 후 누락되었는지 확인
# - 통과 여부와 누락된 구문 목록 반환
def check_critical(source:str,cleaned:str,required:list[str])->dict:
    # BEGIN D24-03-A03
    # TODO D24-03-A03 : 숫자·조건·부정 표현의 삭제를 발견해 실패로 표시합니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # TODO를 완성한 뒤 아래 NotImplementedError 줄을 삭제합니다.

    # 누락된 필수 구문 추출
    # - 원본에 있었으나 정제 결과에서 사라진 항목 수집
    missing=[p for p in required if p in source and p not in cleaned]
    # 검증 결과 딕셔너리 반환
    # - 누락 항목이 없으면 passed=True
    return {'passed' : not missing, 'lost_phrases' : missing}
    # raise NotImplementedError("D24-03-A03 TODO 미완성")
    # END D24-03-A03

# 정제 멱등성 검증 함수
# - 정제된 텍스트를 재정제했을 때 동일 결과 유지 여부 확인
def check_idempotent(cleaned:str,block_type:str)->bool:
    # BEGIN D24-03-A04
    # TODO D24-03-A04 : 같은 Cleaner를 반복 적용했을 때 결과가 동일한지 검사합니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # TODO를 완성한 뒤 아래 NotImplementedError 줄을 삭제합니다.

    # 반복 정제 결과 비교
    # - 한 번 더 정제해도 결과가 같으면 True 반환
    return clean_block(cleaned,block_type) == cleaned
    # raise NotImplementedError("D24-03-A04 TODO 미완성")
    # END D24-03-A04

# 정제 텍스트 지문 생성 함수
# - 입력 문자열을 UTF-8로 인코딩 후 SHA-256 16진수 해시 산출
def clean_fingerprint(text:str)->str:
    # BEGIN D24-03-A05
    # TODO D24-03-A05 : 원본 bytes 해시와 별도로 clean_text UTF-8 해시를 기록합니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # TODO를 완성한 뒤 아래 NotImplementedError 줄을 삭제합니다.

    # UTF-8 기준 SHA-256 해시 반환
    return hashlib.sha256(text.encode('utf-8')).hexdigest()
    # raise NotImplementedError("D24-03-A05 TODO 미완성")
    # END D24-03-A05

# 단위 감사 수행 함수
# - 원문 정제 및 핵심 표현 보존 여부 점검
# - 훼손 시 예외 발생, 정상 시 감사 레코드 생성
def audit_unit(doc_id:str,unit:dict,source_version:str)->dict:
    # BEGIN D24-03-A06
    # TODO D24-03-A06 : 문서 ID·단위 ID·버전·정제 규칙과 실패 이유를 감사 보고서로 남깁니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # TODO를 완성한 뒤 아래 NotImplementedError 줄을 삭제합니다.

    # 원문 추출 및 본문 정제 수행
    raw = unit['raw_text']
    clean = clean_block(raw,'prose')
    # 핵심 키워드('10분', '결석', '사전 승인') 보존 검사
    check = check_critical(raw,clean, ['10분', '결석', '사전 승인'])
    # 핵심 정보 누락 시 예외 발생
    if not check['passed']: raise ValueError('critical text removed')
    # 감사 결과 레코드 반환
    # - 버전, 정제문, SHA-256 해시, 의미 검사 및 멱등성 여부 포함
    return {'doc_id' : doc_id, 'source_version' : source_version, 'unit_id' : unit['unit_id'],
            'cleaner_version' : 'nfc-prose-v1', 'clean_text' : clean,
            'clean_hash' : clean_fingerprint(clean), 'meaning_check' : check,
            'idempotent' : check_idempotent(clean, 'prose')}
    # raise NotImplementedError("D24-03-A06 TODO 미완성")
    # END D24-03-A06

# 프로그램 진입 함수
# - 대상 문서 파싱 및 단위별 감사 실행
# - 의도적 누락 케이스 검증 및 결과 JSON 저장
def main():
    # 출결 규정 문서 조회 및 파싱
    doc=by_doc('DOC-ATTEND');result=parse_one(doc)
    # 파싱된 각 유닛 감사 수행
    units=[audit_unit(doc['doc_id'],u,doc['source_version']) for u in result['units']]
    # 의도적 숫자 삭제 테스트 데이터 생성
    corrupt='10분 초과는 결석.'.replace('10분','')
    # 삭제 탐지 여부 검증
    bad=check_critical('10분 초과는 결석.',corrupt,['10분'])
    # 누락 미탐지 시 단언 오류 발생
    if bad['passed']:raise AssertionError('must detect lost number')
    # 감사 결과 JSON 저장 및 완료 메시지 출력
    out=save_json(HERE,'cleaning_audit.json',{'units':units,'bad_rule':bad})
    show_success('03 Advanced',out)

"""
문서 블록 유형에 따라 NFC 정규화 및 구조 보존 정제 정책을 구분하여 적용하도록 구현하였다.
핵심 정보 누락 검사, 반복 정제 멱등성 확인, SHA-256 해시 기록 및 실패 회귀 테스트를 결합하여 
데이터 전처리 단계에서의 정보 손실을 사전에 차단하고 정제 결과의 추적성과 신뢰성을 확보하였다.
"""