"""실습 01 Advanced · 원문 스냅샷과 변경 추적."""
# 파일 경로 처리 기능 사용
# - Path : 파일 및 디렉터리 경로 관리
from pathlib import Path
# 해시 및 JSON 처리 기능 사용
# - hashlib : SHA256 해시 생성
# - json : JSON 직렬화 및 역직렬화
# - sys : 파이썬 모듈 검색 경로 설정
import hashlib,json,sys
# 현재 실습 파일 경로 조회
# - 결과 파일 저장 기준 위치
# - 프로젝트 상대 경로 계산에 사용
HERE=Path(__file__).resolve().parent
# 상위 디렉터리 모듈 경로 등록
# - coursekit 패키지 import 가능
sys.path.insert(0,str(HERE.parents[1]))
# 입출력 기능 사용
# - DATA : 실습 데이터 디렉터리
# - load_json : JSON 파일 읽기
# - save_json : JSON 파일 저장
# - show_success : 실습 완료 메시지 출력
from coursekit.io import DATA,load_json,save_json,show_success
# 원문 문서 처리 기능 사용
# - raw_path : 원문 파일 실제 경로 조회
# - sha_bytes : 파일 SHA256 해시 계산
from coursekit.documents import raw_path,sha_bytes

"""Manifest 정보를 기준으로 원문 파일을 수집하고 파일 변경 여부를 추적하기 위한 모듈"""

# Manifest 검증 함수
# - 필수 필드 존재 여부 검사
# - 중복 문서 ID 검사
# - 허용된 파일 경로 형식 검사
# - 안정적인 처리 순서를 위해 정렬 수행
def validate_manifest(rows:list[dict])->list[dict]:
    # BEGIN D24-01-A01
    # TODO D24-01-A01 : 입력 manifest의 필수 필드·중복 ID·허용 형식과 경로 계약을 검증합니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # TODO를 완성한 뒤 아래 NotImplementedError 줄을 삭제합니다.

    # 확인된 문서 ID 저장
    # - 중복 ID 검사용
    ids = set()
    # 검증 완료 데이터 저장
    # - 정상 Manifest만 보관
    out = []
    # 전체 Manifest 순회
    for row in rows:
        # 필수 필드 검증
        # - doc_id : 문서 식별자
        # - file : 원문 파일명
        # - category : 문서 분류
        # - source_version : 원문 버전 정보
        for key in ('doc_id', 'file', 'category', 'source_version'):
            # 필드 값 검증
            # - 문자열만 허용
            # - 공백 문자열 금지
            if not isinstance(row.get(key), str) or not row[key].strip(): raise ValueError('missing ' + key)
        # 문서 ID 중복 검증
        # - 동일 문서가 여러 번 등록되는 상황 방지
        if row['doc_id'] in ids: raise ValueError('duplicate doc_id')
        # 확인된 문서 ID 등록
        ids.add(row['doc_id'])
        # 파일 경로 검증
        # - 파일명만 허용
        # - 절대 경로 사용 금지
        # - 경로 이동(Path Traversal) 방지
        if Path(row['file']).name != row['file'] or Path(row['file']).is_absolute():
            raise ValueError('untrusted filename')
        # 검증 완료 데이터 저장.append(row)
        out.append(row)
    # 검증 결과 반환
    # - doc_id 기준 정렬
    # - 실행 순서와 결과 일관성 유지
    return sorted(out, key = lambda row : row['doc_id'])
    # raise NotImplementedError("D24-01-A01 TODO 미완성")
    # END D24-01-A01

# 원문 수집 함수
# - 파일 존재 여부 확인
# - 원문 바이트 수집
# - SHA256 생성
# - 수집 상태 기록
def collect_one(row:dict)->dict:
    # BEGIN D24-01-A02
    # TODO D24-01-A02 : 원문을 수집하여 bytes 길이·raw_sha256 또는 명시적 오류를 기록합니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # TODO를 완성한 뒤 아래 NotImplementedError 줄을 삭제합니다.

    # 실제 원문 파일 경로 조회
    # - Manifest 정보 기반 경로 생성
    path = raw_path(row)
    # 공통 문서 정보 생성
    # - 결과 상태와 무관하게 유지되는 메타데이터
    info = {'doc_id' : row['doc_id'], 'source_version' : row['source_version'], 'file' : row['file']}
    # 파일 형식 검증
    # - txt, md, html, pdf만 허용
    # - 지원하지 않는 확장자는 수집 제외
    if path.suffix.lower() not in {'.txt', '.md', '.html', '.pdf'}:
        return {**info, 'status' : 'unsupported', 'reason' : 'extension'}
    try:
        # 원문 파일 읽기
        # - 파일 내용을 bytes 형태로 수집
        raw = path.read_bytes()
    except OSError as exc:
        # 파일 읽기 실패 결과 반환
        # - 파일 없음
        # - 접근 권한 문제
        # - 입출력 오류 등
        return {**info,'status':'read_error','reason':type(exc).__name__}
    # 수집 성공 결과 반환
    # - status : collected
    # - size_bytes : 원문 크기
    # - raw_sha256 : 원문 해시값
    return {**info, 'status' : 'collected', 'size_bytes' : len(raw), 'raw_sha256' : sha_bytes(raw)}
    # raise NotImplementedError("D24-01-A02 TODO 미완성")
    # END D24-01-A02

# 버전 변경 여부 판별 함수
# - 신규 문서 여부 확인
# - 변경 여부 확인
# - 읽을 수 없는 문서 구분
def compare_version(record:dict,previous:dict|None)->str:
    # BEGIN D24-01-A03
    # TODO D24-01-A03 : 이전 해시와 현재 해시로 new·unchanged·changed·unreadable을 구분합니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # TODO를 완성한 뒤 아래 NotImplementedError 줄을 삭제합니다.

    # 현재 문서 수집 상태 확인
    # - collected 상태가 아니면 비교 불가
    # - 읽기 실패 또는 미지원 형식 포함
    if record['status'] != 'collected':
        # 비교 불가 상태 반환
        # - 원문 해시 확인 불가
        return 'unreadable'
    # 이전 수집 기록 존재 여부 확인
    # - 이전 기록이 없으면 신규 문서
    if previous is None:
        # 신규 문서 상태 반환
        # - 최초 수집 대상
        return 'new'
    # 해시 비교 결과 반환
    # - 동일 해시 : unchanged
    # - 다른 해시 : changed
    return 'unchanged' if previous.get('raw_sha256') == record['raw_sha256'] else 'changed'
    # raise NotImplementedError("D24-01-A03 TODO 미완성")
    # END D24-01-A03

# 수집 실패 감사 함수
# - 미지원 파일 형식 기록
# - 파일 읽기 실패 기록
# - 수집 실패 원인 추적
def failure_audit(records:list[dict])->list[dict]:
    # BEGIN D24-01-A04
    # TODO D24-01-A04 : 지원하지 않는 형식과 파일 접근 실패를 감사 목록에 기록합니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # TODO를 완성한 뒤 아래 NotImplementedError 줄을 삭제합니다.

    # 실패 감사 목록 생성
    # - collected 상태 제외
    # - 오류 상태와 원인 기록
    # - 추후 장애 분석에 사용
    return [{'doc_id' : r['doc_id'], 'status' : r['status'], 'reason' : r.get('reason')} for r in records if r['status'] != 'collected']
    # raise NotImplementedError("D24-01-A04 TODO 미완성")
    # END D24-01-A04

# 수집 결과 정합성 검증 함수
# - 상태별 건수 집계
# - 누락 데이터 여부 확인
# - 감사 정보 생성
def reconcile(records:list[dict])->dict:
    # BEGIN D24-01-A05
    # TODO D24-01-A05 : 입력 건수 = 수집·미지원·읽기 오류 건수인지 검사합니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # TODO를 완성한 뒤 아래 NotImplementedError 줄을 삭제합니다.

    # 상태별 건수 집계
    # - collected : 수집 성공
    # - unsupported : 미지원 형식
    # - read_error : 파일 읽기 실패
    by = {s : sum(r['status'] == s for r in records) for s in ('collected', 'unsupported', 'read_error')}
    # 정합성 검증
    # - 입력 건수와 상태 건수 합계 비교
    # - 누락되거나 알 수 없는 상태 방지
    if len(records) != sum(by.values()): raise ValueError('lost or unknown status')
    # 집계 결과 반환
    # - input_count : 전체 입력 건수
    # - by_status : 상태별 건수
    # - failures : 실패 감사 목록
    return {'input_count' : len(records), 'by_status': by, 'failures' : failure_audit(records)}
    # raise NotImplementedError("D24-01-A05 TODO 미완성")
    # END D24-01-A05

# Manifest Fingerprint 생성 함수
# - 동일 데이터 여부 확인
# - 재실행 안정성 검증
# - 변경 추적 기준 제공
def fingerprint(records:list[dict])->str:
    # BEGIN D24-01-A06
    # TODO D24-01-A06 : 같은 파일·같은 순서 재실행 시 안정적인 manifest fingerprint를 계산합니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # TODO를 완성한 뒤 아래 NotImplementedError 줄을 삭제합니다.

    # Fingerprint 계산용 정규화 문자열 생성
    # - JSON 형태로 직렬화
    # - sort_keys=True : 키 순서 고정
    # - separators 지정 : 불필요한 공백 제거
    # - 동일 입력 시 동일 문자열 생성
    canonical = json.dumps(records, ensure_ascii = False, sort_keys = True, separators=(',', ':'))
    # SHA256 Fingerprint 생성
    # - 동일 데이터면 항상 동일 결과 반환
    # - 변경 발생 시 다른 Fingerprint 생성
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()
    # raise NotImplementedError("D24-01-A06 TODO 미완성")
    # END D24-01-A06

# 실습 실행 함수
# - Manifest 로드 및 검증
# - 원문 수집 수행
# - 변경 추적 정보 생성
# - 결과 파일 저장
def main():
    # Manifest 파일 로드 및 검증
    # - manifest.json 읽기
    # - 필수 필드 및 경로 규칙 검증
    rows=validate_manifest(load_json(DATA/'manifest.json'))
    # 원문 수집 수행
    # - 문서별 상태 기록
    # - SHA256 계산
    records=[collect_one(r) for r in rows]
    # 수집 결과 집계
    # - 상태별 건수 계산
    # - 정합성 검사 수행
    report=reconcile(records)
    # Manifest Fingerprint 생성
    # - 전체 수집 결과 대표 해시 생성
    report['fingerprint']=fingerprint(records)
    # 재실행 안정성 검증
    # - 동일 데이터 재수집 시 동일 Fingerprint 확인
    report['repeat_equal']=fingerprint([collect_one(r) for r in rows])==report['fingerprint']
    # 변경 감지 예시 데이터 생성
    # - 기존 해시를 가상의 값으로 변경
    changed={**records[0],'raw_sha256':'0'*64}
    # 버전 비교 예시 생성
    # - 변경 여부 판정 결과 저장
    report['change_example']=compare_version(records[0],changed)
    # 결과 파일 저장
    # - collection_audit.json 생성
    out=save_json(HERE,'collection_audit.json',report)
    # 실습 완료 메시지 출력
    # - 결과 파일 저장 위치 함께 출력
    show_success('01 Advanced',out)

"""
Manifest 정보를 검증하여 원문 수집 대상의 무결성을 확인하도록 구현하였다.
원문 파일을 직접 수집하고 SHA256 해시를 생성하여 파일 변경 여부를 추적할 수 있도록 구성하였다.
또한 지원하지 않는 형식과 파일 읽기 실패를 별도로 기록하여 수집 과정의 문제를 감사(Audit)할 수 있도록 구현하였다.
Fingerprint를 사용하여 동일 데이터 재실행 시 결과의 안정성을 검증하고, 이전 수집 결과와 현재 수집 결과를 비교하여
신규(New), 변경(Changed), 미변경(Unchanged) 상태를 판별할 수 있도록 구성하였다.
수집 결과의 정합성을 검증함으로써 원문 기반 검색 시스템의 신뢰성과 추적 가능성을 확보하도록 구현하였다.
"""