---
description: "백엔드 개발 작업 규칙 및 가이드라인"
globs: ["server/**/*.py"]
alwaysApply: false
---

# 백엔드 개발 규칙

## 기본 원칙

1. **프론트엔드 코드 절대 수정 금지**
   - 백엔드 작업 시 `ai_studio_code_F2.html`, `client/` 디렉토리 내 파일은 절대 수정하지 않는다.
   - 백엔드 관련 작업은 오직 `server/` 디렉토리 내에서만 수행한다.

2. **API 엔드포인트 규칙**
   - 모든 API 엔드포인트는 `/api/` 접두사를 사용한다.
   - RESTful 원칙을 따르되, 한국은행 ECOS API 구조에 맞춘다.
   - 에러 응답은 항상 JSON 형식으로 반환한다.

## 작업 전 사전 검증

새로운 기능을 개발하기 전에 다음을 확인:

1. **통합 검증 스크립트 실행**
   ```bash
   python scripts/validate_integration.py
   ```
   - 에러가 있으면 먼저 수정
   - 경고 메시지 확인 및 필요 시 수정

2. **파일 참조 확인**
   - RULE.md에서 언급한 파일들이 실제로 존재하는지 확인
   - 참조된 함수가 실제 코드에 존재하는지 확인

3. **의존성 확인**
   - ECOS API 명세서 확인 (`docs/api/ecos/`)
   - `BOK_MAPPING`에 새로운 카테고리 추가 시 기존 구조 확인
   - 프론트엔드에서 사용할 API 엔드포인트 확인

4. **일관성 확인**
   - 기존 코드 스타일과 일치하는지 확인
   - 함수 네이밍 컨벤션(`snake_case`) 준수 확인
   - 에러 처리 패턴 일관성 확인

3. **에러 처리**
   - 모든 API 함수는 try-except 블록으로 감싼다.
   - 에러 메시지는 명확하고 사용자 친화적으로 작성한다.
   - HTTP 상태 코드를 적절히 사용한다 (400: Bad Request, 500: Internal Server Error 등).

4. **환경 변수 관리**
   - 민감한 정보(API 키 등)는 `.env` 파일에 저장한다.
   - `python-dotenv`를 사용하여 환경 변수를 로드한다.
   - Fallback 값은 개발용으로만 사용한다.

## 파일 구조

### `server/main.py`
- Flask 애플리케이션 메인 파일
- API 라우트 정의
- 정적 파일 서빙 설정
- CORS 설정

### `server/bok_backend.py`
- 한국은행 ECOS API 연동 모듈
- `BOK_MAPPING` 딕셔너리에 카테고리 및 항목 정의
- API 호출 함수들 (`get_bok_statistics`, `get_market_index` 등)

## 코딩 스타일

1. **함수 네이밍**
   - 함수명은 `snake_case`를 사용한다.
   - API 라우트 핸들러는 `get_`, `post_` 등의 접두사를 사용한다.

2. **주석 및 문서화**
   - 모든 함수에는 docstring을 작성한다.
   - 복잡한 로직에는 인라인 주석을 추가한다.

3. **데이터 검증**
   - 모든 입력 파라미터는 검증한다.
   - 날짜 형식은 `YYYYMMDD` 형식을 사용한다.
   - `validate_date_format()` 함수를 활용한다.

## API 연동 규칙

1. **한국은행 ECOS API**
   - `bok_backend.py`의 함수를 통해만 API를 호출한다.
   - 직접 `requests.get()`을 사용하지 않고, 래퍼 함수를 사용한다.
   - API 타임아웃은 30초로 설정한다.

2. **새로운 카테고리 추가**
   - `BOK_MAPPING`에 새로운 카테고리 추가
   - `stat_code`, `default_cycle`, `items` 정보 포함
   - `get_category_info()` 함수가 자동으로 인식하도록 구성

3. **에러 응답 형식**
```python
{
    "error": "에러 메시지",
    "result_code": "ERROR-001",  # 선택적
    "result_message": "상세 메시지"  # 선택적
}
```

## 테스트

- API 엔드포인트는 수동 테스트를 통해 검증한다.
- 에러 케이스도 함께 테스트한다 (잘못된 날짜 형식, 누락된 파라미터 등).

## 개발 후 검증 프로세스

### 1. API 엔드포인트 검증

#### 기본 동작 검증
- [ ] 정상 케이스 테스트
  ```bash
  # 예시: 환율 데이터 조회
  curl "http://localhost:5000/api/market/indices?type=exchange&itemCode=USD&startDate=20240101&endDate=20241231&cycle=D"
  ```
  - HTTP 상태 코드 200 확인
  - 응답이 JSON 형식인지 확인
  - 응답 데이터 구조 확인 (`StatisticSearch` 키 존재)
  - 데이터 개수 확인 (`list_total_count` > 0)

#### 파라미터 검증
- [ ] 필수 파라미터 누락 시 에러 처리
  - `type`, `startDate`, `endDate` 누락 시 400 에러 반환 확인
  - 에러 메시지가 명확한지 확인
- [ ] 잘못된 파라미터 값 처리
  - 잘못된 날짜 형식 (YYYYMMDD가 아닌 경우)
  - 잘못된 카테고리명 (`type=invalid`)
  - 잘못된 항목 코드 (`itemCode=INVALID`)
  - 시작일이 종료일보다 늦은 경우

#### 날짜 범위 검증
- [ ] 날짜 형식 검증
  - YYYYMMDD 형식만 허용하는지 확인
  - 잘못된 형식 시 명확한 에러 메시지 반환
- [ ] 날짜 범위 제한
  - 최대 5년(1825일) 제한 확인
  - 범위 초과 시 에러 메시지 반환

### 2. 데이터 검증

#### API 응답 구조 검증
- [ ] ECOS API 응답 구조 확인
  ```python
  {
    "StatisticSearch": {
      "list_total_count": int,
      "row": [
        {
          "TIME": "YYYYMMDD",
          "DATA_VALUE": "숫자 문자열"
        }
      ]
    }
  }
  ```
- [ ] 에러 응답 처리
  - `RESULT.CODE`가 "INFO-000"이 아닌 경우 에러 처리
  - 에러 메시지를 사용자 친화적으로 변환

#### 데이터 변환 검증
- [ ] 주기별 날짜 형식 변환 확인
  - D (일): YYYYMMDD
  - M (월): YYYYMM
  - Q (분기): YYYYQn
  - A (연): YYYY
- [ ] `end_index` 자동 계산 확인
  - 기간에 따라 올바르게 계산되는지 확인
  - 최대 1000건 제한 확인

### 3. 에러 처리 검증

#### API 에러 처리
- [ ] ECOS API 에러 코드 처리
  - `ERROR-101`: 날짜 형식 오류
  - `INFO-200`: 데이터 없음
  - 기타 에러 코드 처리
- [ ] 네트워크 에러 처리
  - 타임아웃 (30초) 처리
  - 연결 실패 처리
- [ ] HTTP 상태 코드 확인
  - 400: Bad Request (잘못된 파라미터)
  - 500: Internal Server Error (서버 오류)

#### 로깅 검증
- [ ] 로그 레벨 확인
  - INFO: 정상 API 호출
  - WARNING: Fallback API 키 사용, 데이터 부재
  - ERROR: API 에러, 타임아웃
- [ ] 로그 내용 확인
  - API 요청 파라미터 로깅
  - 응답 데이터 개수 로깅
  - 에러 메시지 로깅

### 4. 통계 계산 검증

#### `/api/market/indices/stats` 엔드포인트
- [ ] 통계 값 계산 정확성 확인
  - `high`: 최고값이 올바른지 확인
  - `low`: 최저값이 올바른지 확인
  - `average`: 평균값이 올바른지 확인
  - `current`: 현재값(최신값)이 올바른지 확인
  - `previous`: 이전값(첫 번째 값)이 올바른지 확인
  - `change`: 변동액 계산 정확성 확인
  - `changePercent`: 변동률 계산 정확성 확인

### 5. 새로운 카테고리 추가 시 검증

- [ ] `BOK_MAPPING` 구조 확인
  - `stat_code`가 올바른지 확인
  - `default_cycle`가 적절한지 확인
  - `items` 딕셔너리가 올바른지 확인
  - `item_code`가 실제 API와 일치하는지 확인
- [ ] API 호출 테스트
  - 실제 ECOS API를 호출하여 데이터가 반환되는지 확인
  - 다양한 날짜 범위로 테스트
  - 주기별(D, M, Q, A) 테스트

### 6. 성능 검증

- [ ] API 응답 시간 확인
  - 일반적인 요청: 1-3초 이내
  - 대용량 데이터: 5초 이내
- [ ] 동시 요청 처리 확인
  - 여러 클라이언트가 동시에 요청해도 정상 동작하는지 확인

### 검증 체크리스트 요약

작업 완료 후 다음 항목을 모두 확인:

```
□ API 엔드포인트가 정상적으로 동작하는가?
□ 파라미터 검증이 올바른가?
□ 날짜 범위 검증이 올바른가?
□ 데이터가 올바르게 변환되는가?
□ 에러 처리가 적절한가?
□ 로깅이 올바르게 이루어지는가?
□ 통계 계산이 정확한가?
□ 성능 문제가 없는가?
```

### 문제 발견 시 조치

1. **API 호출 실패**: ECOS API 키 확인, 네트워크 연결 확인
2. **데이터 파싱 오류**: API 응답 구조 확인 및 파싱 로직 수정
3. **날짜 형식 오류**: `format_date_for_cycle()` 함수 확인
4. **통계 계산 오류**: `calculate_statistics()` 함수 로직 확인
5. **성능 문제**: 캐싱 전략 검토, API 호출 최적화

## 참고 파일

- `@server/bok_backend.py` - API 연동 모듈
- `@docs/api/ecos/` - 한국은행 ECOS API 개발 명세서
- `@docs/CURRENCY_MAPPING_TABLE.md` - 통화 매핑 정보

