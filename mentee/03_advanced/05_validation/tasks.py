"""실습 05 Advanced · 검증 Gate와 Regression."""
# 파일 경로 처리 기능 사용
# - Path : 파일 및 디렉터리 경로 관리
from pathlib import Path
# 파이썬 실행 환경 제어 기능 사용
# - sys : 모듈 검색 경로 등록
import sys
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
# 문자 범위 커버리지 계산 기능 사용
# - covered_positions : 고유 커버 문자 수 및 누락 구간 계산
from coursekit.processing import covered_positions

"""청크 스키마 및 원문 일치 검증, 중복 ID 탐지, 커버리지 통계 산출, 검증 게이트 격리 및 회귀 테스트를 수행하는 모듈"""

# 청크 스키마 검증 함수
# - 필수 문자열 필드 존재 및 공백 여부 확인
# - char_start, char_end 정수 타입 검사
def schema_check(chunk:dict)->None:
    # BEGIN D24-05-A01
    # TODO D24-05-A01 : 필수 필드·자료형·문자 범위를 검증합니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # TODO를 완성한 뒤 아래 NotImplementedError 줄을 삭제합니다.

    # 필수 문자열 필드 순회 검사
    # - 누락되거나 공백만 있는 경우 ValueError 발생
    for name in ('chunk_id', 'doc_id', 'source_version', 'unit_id','body'):
        if not isinstance(chunk.get(name), str) or not chunk[name].strip():
            raise ValueError(f'missing_{name}')
    # 오프셋 범위 필드 정수 타입 검사
    # - bool 제외 순수 int 타입만 허용
    if type(chunk.get('char_start')) is not int or type(chunk.get('char_end')) is not int:
        raise ValueError('invalid_span_type')
    # raise NotImplementedError("D24-05-A01 TODO 미완성")
    # END D24-05-A01

# 청크 원문 일치 검증 함수
# - 스키마 선행 검사 수행
# - 시작·종료 인덱스 유효성 및 기준 clean_text 슬라이스 일치 여부 확인
def text_match(chunk:dict,clean:str)->None:
    # BEGIN D24-05-A02
    # TODO D24-05-A02 : 청크 본문이 기준 clean_text 슬라이스와 일치하는지 확인합니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # TODO를 완성한 뒤 아래 NotImplementedError 줄을 삭제합니다.

    # 스키마 유효성 선행 확인
    schema_check(chunk)
    # 문자 오프셋 추출 및 범위 유효성 검사
    a, b = chunk['char_start'], chunk['char_end']
    if not 0 <= a < b <= len(clean): raise ValueError('invalid_span')
    # 정제 본문 슬라이스와 청크 body 일치 여부 확인
    if chunk['body'] != clean[a:b]: raise ValueError('text_mismatch')
    # raise NotImplementedError("D24-05-A02 TODO 미완성")
    # END D24-05-A02

# 중복 청크 ID 탐지 함수
# - 청크 목록을 순회하며 반복 등장하는 chunk_id 수집
# - 정렬된 중복 ID 목록 반환
def duplicated_ids(chunks:list[dict])->list[str]:
    # BEGIN D24-05-A03
    # TODO D24-05-A03 : 같은 chunk_id 중복과 의도한 overlap을 구분합니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # TODO를 완성한 뒤 아래 NotImplementedError 줄을 삭제합니다.

    # 기출현 ID 집합 및 중복 ID 집합 초기화
    seen = set()
    duplicates = set()
    # 청크 순회 및 중복 여부 기록
    for c in chunks:
        cid = c.get('chunk_id')
        if cid in seen: duplicates.add(cid)
        seen.add(cid)
    # 정렬된 중복 ID 리스트 반환
    return sorted(duplicates)
    # raise NotImplementedError("D24-05-A03 TODO 미완성")
    # END D24-05-A03

# 청크 커버리지 통계 산출 함수
# - 빈 텍스트 방어 처리
# - 고유 문자 커버 비율, 누락 구간(gaps), 중복 중첩량(repeat_extra) 계산
def coverage_stats(chunks:list[dict],clean:str)->dict:
    # BEGIN D24-05-A04
    # TODO D24-05-A04 : 고유 문자 위치 Coverage와 Gap·Repeat 양을 계산합니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # TODO를 완성한 뒤 아래 NotImplementedError 줄을 삭제합니다.

    # 기준 텍스트가 비어 있는 경우 기본값 반환
    if not clean: return {'coverage' : None, 'gaps' : [], 'repeat_extra' : 0}
    # 청크별 문자 오프셋 쌍 추출
    spans = [(c['char_start'], c['char_end']) for c in chunks]
    # 커버된 고유 문자 수 및 미커버 구간 조회
    n, missing = covered_positions(spans, len(clean))
    # 커버리지 비율, 갭 목록, 중복 초과 문자 수 반환
    return {'coverage' : n / len(clean), 'gaps' : missing,
            'repeat_extra' : sum(b - a for a, b in spans) - n}
    # raise NotImplementedError("D24-05-A04 TODO 미완성")
    # END D24-05-A04

# 청크 검증 게이트 함수
# - 원문 일치 및 중복 ID 검사 수행
# - 오류 발생 청크 격리 및 정상 청크 통과 분리 후 통계 집계
def gate(chunks:list[dict],clean:str)->dict:
    # BEGIN D24-05-A05
    # TODO D24-05-A05 : 입력 오류별 reason code를 기록하고 통과 청크·격리 청크를 분리합니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # TODO를 완성한 뒤 아래 NotImplementedError 줄을 삭제합니다.

    # 통과 목록, 격리 목록, 처리 완료 ID 집합 초기화
    good = []
    quarantine = []
    seen = set()
    # 청크별 검증 및 분류 수행
    for c in chunks:
        try:
            # 원문 슬라이스 일치 검증 및 중복 ID 확인
            text_match(c, clean)
            if c['chunk_id'] in seen: raise ValueError('duplicate_id')
            seen.add(c['chunk_id'])
        # 검증 실패 시 사유 코드와 함께 격리 목록에 추가
        except (ValueError, KeyError, TypeError) as exc:
            quarantine.append({'chunk_id' : c.get('chunk_id'), 'reason' : str(exc)})
        # 검증 통과 시 정상 청크 목록에 추가
        else: good.append(c)
    # 통과 청크, 격리 청크, 통과 청크 기준 커버리지 통계 반환
    return {'passed' : good, 'quarantine' : quarantine, 'stats' : coverage_stats(good, clean)}
    # raise NotImplementedError("D24-05-A05 TODO 미완성")
    # END D24-05-A05

# 검증 게이트 회귀 테스트 함수
# - 손상 청크 및 중복 청크 격리 동작 확인
# - 정상 청크 재검증 시 통과 건수 및 100% 커버리지 확인
def regression()->dict:
    # BEGIN D24-05-A06
    # TODO D24-05-A06 : 오류 수정 후 정상 회귀 사례를 다시 확인합니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # TODO를 완성한 뒤 아래 NotImplementedError 줄을 삭제합니다.

    # 테스트용 기준 문자열 및 정상 청크 2건 구성
    clean = '01234567890123456789'
    good = [{'chunk_id' : 'C1', 'doc_id' : 'DOC-TEST', 'source_version' : 'v1', 'unit_id' : 't1', 'char_start' : 0, 'char_end' : 10, 'body' : clean[:10]},
            {'chunk_id' : 'C2', 'doc_id' : 'DOC-TEST', 'source_version' : 'v1', 'unit_id' : 't1', 'char_start' : 10, 'char_end' : 20, 'body' : clean[10:]}]
    # 본문 변조 및 중복 ID가 포함된 비정상 입력 구성
    broken = [*good, {**good[0], 'body' : 'corrupted'}, good[1]]
    # 비정상 입력 게이트 검증 및 격리 건수 단언
    result = gate(broken, clean)
    if len(result['quarantine']) != 2: raise AssertionError('error cases not isolated')
    # 정상 입력 재검증 및 통과 건수·커버리지 단언
    fixed = gate(good, clean)
    if len(fixed['passed']) != 2 or fixed['stats']['coverage'] != 1.0:
        raise AssertionError('normal regression failed')
    # 격리 사유 목록 및 정상 통과 건수 반환
    return {'failure_reasons' : result['quarantine'], 'fixed_passed' : len(fixed['passed'])}
    # raise NotImplementedError("D24-05-A06 TODO 미완성")
    # END D24-05-A06

# 프로그램 진입 함수
# - 회귀 테스트 실행 및 결과 JSON 저장
# - 완료 메시지 출력
def main():
    # 회귀 테스트 수행 후 validation_gate.json 저장
    out=save_json(HERE,'validation_gate.json',regression())
    # 완료 메시지 출력
    show_success('05 Advanced',out)

"""
청크 데이터의 스키마 유효성, 원문 슬라이스 정합성, ID 중복 여부를 검사하는 검증 게이트를 구현하였다.
오류 데이터를 사유 코드와 함께 격리하는 구조와 커버리지·중복 통계를 결합하였으며, 
오류 사례 격리와 정상 회귀 테스트를 통해 청킹 품질 관리 파이프라인의 신뢰성을 확보하였다.
"""