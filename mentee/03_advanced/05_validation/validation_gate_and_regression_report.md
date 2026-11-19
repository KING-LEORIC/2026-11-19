# \[Day24 실습 05 Advanced\] 검증 Gate와 Regression 결과 보고서

## 1. 개요 및 실행 정보

* **실습 주제:** Day24 실습 05 Advanced · 검증 Gate와 Regression
* **결과 파일:** `C:\workspace\2026-11-19\mentee\03_advanced\05_validation\outputs\validation_gate.json`
* **주요 검증 항목:**
  * 청크 스키마 및 문자 범위(`char_start`, `char_end`) 유효성 검사 (`schema_check`, `text_match`)
  * 중복 `chunk_id` 탐지 (`duplicated_ids`) 및 문자 위치 커버리지/갭/중복량 집계 (`coverage_stats`)
  * 오류 청크 격리 및 사유 기록 (`gate`)
  * 결함 주입 후 정상 복구 회귀 검증 (`regression`)

---

## 2. 원문 및 데이터 출처

본 실행은 외부 파싱 문서 파일(`manifest.json` 또는 `DOC-ATTEND` 등)을 직접 청킹하여 검증한 것이 아니라, **`05_validation` 스크립트의 `regression()` 함수 내부에 정의된 인메모리 합성(Synthetic) 테스트 데이터**를 기반으로 수행되었습니다.

* **기준 문자열 (`clean`):** `'01234567890123456789'` (총 20자 길이의 숫자 문자열)
* **정상 청크 집합 (`good`):** 문서 ID `DOC-TEST` (`source_version: 'v1'`, `unit_id: 't1'`) 기준 2개 청크
  * `C1`: `[0:10]` 구간 (`'0123456789'`)
  * `C2`: `[10:20]` 구간 (`'0123456789'`)
* **결함 주입 입력 (`broken`):** `good` 청크 2개 뒤에 다음 2개 항목을 추가한 총 4개 청크 구성
  * 본문 변조 `C1` (`body: 'corrupted'`) → `text_mismatch` 유발
  * 중복 `C2` → `duplicate_id` 유발

---

## 3. 실행 결과 분석 (`validation_gate.json`)

```json
{
  "failure_reasons": [
    {
      "chunk_id": "C1",
      "reason": "text_mismatch"
    },
    {
      "chunk_id": "C2",
      "reason": "duplicate_id"
    }
  ],
  "fixed_passed": 2
}
```

### 💡 핵심 검증 포인트
1. **비정상 청크 격리 (`quarantine`):**
   * `broken` 입력에 대해 `gate()`를 수행한 결과, 손상된 본문을 가진 `C1`이 `text_mismatch` 사유로, 이미 등장한 ID를 재사용한 `C2`가 `duplicate_id` 사유로 정확히 격리되어 총 2건의 오류가 누락 없이 탐지되었습니다.
2. **정상 회귀 통과 (`fixed_passed: 2`):**
   * 결함이 제거된 `good` 입력을 재검증한 결과, 2개 청크 모두 통과(`passed`)하고 기준 문자열(20자) 전체를 빈틈없이 덮는 `coverage: 1.0`(100%)을 만족하여 회귀 테스트가 정상 통과했습니다.

---

## 4. 한계점 및 보완 방향

* **합성 소규모 픽스처의 한계:** 20자 길이의 고정 문자열과 2개 청크로 구성된 단위/회귀 시나리오이므로, 장문 문서에서 발생하는 다중 중복(`overlap`) 구간, 복잡한 표/코드 블록, 누락 문자 갭(`gaps`)이 혼재된 실제 대용량 데이터의 모든 엣지 케이스를 대표하지는 못합니다.
* **실제 문서 청크 연계 필요:** 향후 실습 04에서 생성된 실제 문서 청크(`structure_chunks.json` 등)를 `gate()` 파이프라인에 연결하여 실데이터 기반의 격리 비율과 커버리지 지표를 함께 점검하는 것이 좋습니다.
* **상세 대조 권장:** 세부 기준은 `expected/EXPECTED.md`와 대조하여 필드명, 사유 코드(`reason`), 출력 스키마가 기대 기준과 완전히 일치하는지 최종 확인해야 합니다.

---

## 5. 결론

05 Advanced 실행을 통해 스키마·슬라이스 일치·ID 중복 검사를 결합한 검증 Gate가 비정상 청크를 사유 코드와 함께 안정적으로 격리하고, 정상 데이터 재투입 시 100% 커버리지로 회귀 기준을 충족함을 확인했습니다.