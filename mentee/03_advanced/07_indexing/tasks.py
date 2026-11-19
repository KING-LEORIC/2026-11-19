"""실습 07 Advanced · --live-db에서 PostgreSQL 실제 버전 전환/회귀."""
# 파일 경로 처리 기능 사용
# - Path : 파일 및 디렉터리 경로 관리
from pathlib import Path
# 파이썬 실행 환경 제어 기능 사용
# - sys : 모듈 검색 경로 및 명령행 인자 접근
import sys
# 현재 실습 파일 경로 조회
# - 결과 파일 저장 위치 계산
# - 상대 경로 계산 기준
HERE=Path(__file__).resolve().parent
# 상위 디렉터리 모듈 경로 등록
# - coursekit 패키지 import 가능
sys.path.insert(0,str(HERE.parents[1]))
# 입출력 및 완료 출력 기능 사용
# - DATA : 실습 데이터 디렉터리
# - save_json : JSON 파일 저장
# - show_success : 실행 완료 메시지 출력
from coursekit.io import DATA,save_json,show_success
# 문서 조회 및 마크다운 파싱 기능 사용
# - by_doc : 문서 ID 기반 원문 조회
# - parse_one : 문서 파싱 수행
# - parse_markdown_units : 마크다운 본문 단위 분할 파싱
from coursekit.documents import by_doc,parse_one,parse_markdown_units
# 청크 생성 기능 사용
# - make_chunks : 단위 본문 기반 청크 목록 생성
from coursekit.processing import make_chunks

"""문서 버전(v1/v2)별 청킹 및 E5 임베딩 생성, PostgreSQL 스테이징, 롤백 검증, 공개 버전 전환 및 구버전 배제 회귀 테스트를 수행하는 모듈"""

# 개정 버전 문서 및 청크 준비 함수
# - v1/v2 버전별 원문 파싱 및 메타데이터 보존
# - 파싱된 유닛별 슬라이딩 청크 생성
def prepare_revision(doc_id:str,version:str)->tuple[dict,list[dict]]:
    # BEGIN D24-07-A01
    # TODO D24-07-A01 : DOC-ATTEND v1·v2를 동일한 Markdown Parser로 처리하고, 문서 ID·원문 버전·처리 설정을 보존합니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # TODO를 완성한 뒤 아래 NotImplementedError 줄을 삭제합니다.

    # 대상 문서 메타데이터 복사 및 지원 버전 확인
    doc = by_doc(doc_id).copy()
    if version not in {'v1', 'v2'}: raise ValueError('unsupported source version')
    # 버전별 문서 파싱 분기 처리
    # - v1은 기존 파서 사용, v2는 versions/attendance_v2.md 로드 및 마크다운 단위 파싱
    if version == 'v1':
        parsed = parse_one(doc)
    else:
        src = (DATA/'versions'/'attendance_v2.md').read_text(encoding = 'utf-8')
        doc['source_version'] = 'v2'
        parsed = {'status' : 'parsed', 'units' : parse_markdown_units(src, 'attendance_v2.md')}
    # 파싱 성공 상태 확인
    if parsed['status'] != 'parsed' : raise ValueError(parsed['status'])
    # 파싱된 유닛별 청크 생성 및 누적
    chunks = []
    for u in parsed['units']: chunks.extend(make_chunks(doc, u, 110, 15))
    # 준비된 문서 메타데이터와 청크 목록 반환
    return doc, chunks
    # raise NotImplementedError("D24-07-A01 TODO 미완성")
    # END D24-07-A01

# DB 트랜잭션 전 패시지 임베딩 생성 함수
# - 인코더로 청크 목록의 passage 벡터 계산
# - 청크 수와 생성 벡터 수 일치 검증
def embeddings_before_db(model,chunks:list[dict]):
    # BEGIN D24-07-A02
    # TODO D24-07-A02 : E5 passage Embedding을 DB Transaction 전에 계산·검증합니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # TODO를 완성한 뒤 아래 NotImplementedError 줄을 삭제합니다.

    # 라이브 패시지 인코더 호출 및 벡터 생성
    from coursekit.live import encode_passages
    vectors = encode_passages(model, chunks)
    # 생성 벡터 개수 정합성 검사
    if len(chunks) != len(vectors): raise ValueError('vector count mismatch')
    # 계산된 벡터 목록 반환
    return vectors
    # raise NotImplementedError("D24-07-A02 TODO 미완성")
    # END D24-07-A02

# 새 버전 스테이징 함수
# - 트랜잭션 블록 내에서 벡터·원문·출처 및 청크를 새 버전으로 스테이징
def stage_revision(conn,doc:dict,chunks:list[dict],vectors)->None:
    # BEGIN D24-07-A03
    # TODO D24-07-A03 : 벡터·원문·출처를 새 버전으로 Stage하고 ID 충돌을 검사합니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # TODO를 완성한 뒤 아래 NotImplementedError 줄을 삭제합니다.

    # 스테이징 함수 호출 및 트랜잭션 커밋/롤백 관리
    from coursekit.db import stage_version
    with conn.transaction():
        stage_version(conn, doc, doc['file'], chunks, vectors)
    # raise NotImplementedError("D24-07-A03 TODO 미완성")
    # END D24-07-A03

# 현재 공개 포인터 조회 함수
# - ingest_documents 테이블에서 문서의 current_version 및 current_pipeline_version 조회
def current_pointer(conn,doc_id:str)->tuple|None:
    # BEGIN D24-07-A04
    # TODO D24-07-A04 : 현재 문서의 공개 포인터(source_version, pipeline_version)를 조회합니다. Publish는 A06에서 처리합니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # TODO를 완성한 뒤 아래 NotImplementedError 줄을 삭제합니다.

    # 현재 공개 버전 포인터 단건 조회 및 반환
    return conn.execute('SELECT current_version,current_pipeline_version FROM ingest_documents ''WHERE doc_id=%s', (doc_id, )).fetchone()
    # raise NotImplementedError("D24-07-A04 TODO 미완성")
    # END D24-07-A04

# 트랜잭션 롤백 검증 함수
# - 배포 호출 직후 의도적 예외 발생으로 롤백 유도
# - 롤백 전후 현재 공개 포인터가 동일하게 유지되는지 확인
def test_rollback(conn,doc:dict,chunks:list[dict])->dict:
    # BEGIN D24-07-A05
    # TODO D24-07-A05 : 강제로 예외를 발생시킨 Transaction에서 Rollback 후 현재 포인터가 유지되는지 확인합니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # TODO를 완성한 뒤 아래 NotImplementedError 줄을 삭제합니다.

    # 롤백 이전 현재 포인터 기록
    from coursekit.db import publish_version
    before = current_pointer(conn, doc['doc_id'])
    try:
        # 트랜잭션 내 배포 실행 후 강제 예외 발생
        with conn.transaction():
            publish_version(conn, doc['doc_id'], doc['source_version'], chunks[0]['pipeline_version'])
            raise RuntimeError('injected_rollback_before_commit')
    # 의도된 롤백 예외 포착 및 다른 RuntimeError 재발생
    except RuntimeError as exc:
        if str(exc) != 'injected_rollback_before_commit': raise
    # 롤백 이후 포인터 재조회 및 변경 여부 검사
    after = current_pointer(conn, doc['doc_id'])
    if before != after: raise ValueError('rollback failed: pointer changed')
    # 롤백 검증 결과 반환
    return {'rollback_ok' : True, 'pointer_before' : before, 'pointer_after' : after}
    # raise NotImplementedError("D24-07-A05 TODO 미완성")
    # END D24-07-A05

# 공개 전환 및 검색 회귀 검증 함수
# - 트랜잭션 내 새 버전 Publish 및 포인터 반영 확인
# - 쿼리 임베딩 생성 후 현재 공개 검색에서 구버전(v1) 청크 미노출 검증
def publish_and_verify(conn,doc:dict,chunks:list[dict],model)->dict:
    # BEGIN D24-07-A06
    # TODO D24-07-A06 : v2를 짧은 Transaction에서 Publish하고, 정확 검색에서 이전 v1 청크가 제외되는지 확인합니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # TODO를 완성한 뒤 아래 NotImplementedError 줄을 삭제합니다.

    # 배포 및 현재 검색 함수 import
    from coursekit.db import publish_version,search_current
    from coursekit.live import encode_query
    # 짧은 트랜잭션으로 새 버전 공개
    with conn.transaction():
        publish_version(conn, doc['doc_id'], doc['source_version'], chunks[0]['pipeline_version'])
    # 공개 포인터 갱신 여부 확인
    pointer = current_pointer(conn, doc['doc_id'])
    if pointer != (doc['source_version'], chunks[0]['pipeline_version']):
        raise ValueError('publish pointer mismatch')
    # 검증 질의 임베딩 및 현재 공개 버전 대상 검색 수행
    query = encode_query(model, '15분 늦으면 어떻게 기록되나요?')
    hits = search_current(conn, query, '학사', k = 10)
    # 대상 문서 검색 결과 필터링 및 구버전 혼합 여부 검사
    mine = [h for h in hits if h[4] == doc['doc_id']]
    if any(h[5] != doc['source_version'] for h in mine): raise ValueError('stale version in current search')
    # 검증 완료 결과 딕셔너리 반환
    return {'pointer' : pointer, 'hits_for_this_document' : len(mine), 'source_versions' : [h[5] for h in mine]}
    # raise NotImplementedError("D24-07-A06 TODO 미완성")
    # END D24-07-A06

# 프로그램 진입 함수
# - v1/v2 개정 준비 및 기본 리포트 초기화
# - --live-db 옵션 시 DB 스키마 초기화, 스테이징, 롤백 테스트, 공개 전환 및 검증 수행
# - 결과 JSON 저장 및 완료 메시지 출력
def main():
    # v1 및 v2 문서/청크 준비 및 초기 리포트 구성
    v1,c1=prepare_revision('DOC-ATTEND','v1')
    v2,c2=prepare_revision('DOC-ATTEND','v2')
    report={'source_mode':'prepared_only_not_db','v1_chunks':len(c1),'v2_chunks':len(c2),
            'db_status':'not_run'}
    # --live-db 플래그 전달 시 실제 PostgreSQL/E5 검증 실행
    if '--live-db' in sys.argv:
        from coursekit.live import connect_db,load_encoder
        from coursekit.db import initialize,publish_version,use_schema
        # 모델 로드 및 트랜잭션 외부 임베딩 선계산
        model=load_encoder();vec1=embeddings_before_db(model,c1);vec2=embeddings_before_db(model,c2)
        # DB 연결 및 스키마/테이블 초기화
        with connect_db() as conn:
            use_schema(conn,'d24_adv07')
            initialize(conn)
            # v1 스테이징 및 기준 버전 공개
            stage_revision(conn,v1,c1,vec1)
            # 처음 실행에서는 v1을 정상 공개해 비교 기준을 준비합니다.
            with conn.transaction():publish_version(conn,v1['doc_id'],'v1',c1[0]['pipeline_version'])
            # v2 스테이징, 롤백 검증, 공개 및 검색 검증 순차 수행
            stage_revision(conn,v2,c2,vec2)
            report['injected_failure']=test_rollback(conn,v2,c2)
            report['after_retry']=publish_and_verify(conn,v2,c2,model)
            report['source_mode']='e5_pgvector_live'
            report['db_status']='verified'
    # 결과 JSON 저장 및 완료 알림 출력
    out=save_json(HERE,'version_regression.json',report)
    show_success('07 Advanced',out)

"""
문서 버전별 파싱·청킹과 DB 트랜잭션 외부의 임베딩 선계산을 분리하여 DB 락 부담과 실패 위험을 줄이도록 구현하였다.
스테이징 및 공개 포인터 전환 과정에서 트랜잭션 롤백 안전성과 버전 전환 후 구버전 검색 배제 회귀 테스트를 결합하여, 
실제 PostgreSQL·pgvector 환경에서도 무중단 버전 갱신과 검색 일관성이 보장되도록 구성하였다.
"""