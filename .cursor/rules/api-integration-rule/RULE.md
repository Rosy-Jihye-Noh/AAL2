---
description: "API 연동 작업 규칙 및 가이드라인"
globs: ["server/bok_backend.py", "API/**/*", "apiguideline/**/*"]
alwaysApply: false
---

# API 연동 규칙

## 기본 원칙

1. **API 명세서 사전 학습 필수**
   - API 연동 작업 전에 `docs/api/ecos/` 디렉토리의 개발 명세서를 반드시 확인한다.

2. **백엔드 Agent와 협업**
   - API 연동 작업은 백엔드 Agent와 협업하여 진행한다.
   - 새로운 API 엔드포인트 추가 시 `server/main.py`와 `server/bok_backend.py`를 함께 수정한다.

3. **프론트엔드 코드 수정 금지**
   - API 연동 작업 시 프론트엔드 코드는 수정하지 않는다.
   - API 응답 형식이 변경되는 경우에만 프론트엔드 팀과 협의한다.

## 한국은행 ECOS API 연동

### API 구조 이해

1. **엔드포인트 형식**
```
/StatisticSearch/{KEY}/{언어}/{요청시작건수}/{요청종료건수}/{통계표코드}/{주기}/{시작일자}/{종료일자}/{항목코드}
```

2. **주요 파라미터**
   - `stat_code`: 통계표 코드 (예: "731Y001" - 주요국 통화의 대원화 환율)
   - `item_code`: 항목 코드 (예: "0000001" - USD)
   - `cycle`: 주기 (D: 일, M: 월, Q: 분기, Y: 연)
   - `start_date`, `end_date`: YYYYMMDD 형식

### BOK_MAPPING 구조

`server/bok_backend.py`의 `BOK_MAPPING` 딕셔너리에 카테고리와 항목을 정의한다:

```python
BOK_MAPPING = {
    "exchange": {
        "stat_code": "731Y001",
        "name": "환율 및 금리",
        "default_cycle": "D",
        "items": {
            "USD": {"code": "0000001", "name": "미국 달러 (USD)"},
            # ...
        },
        "default_item": "USD"
    }
}
```

### 새로운 통화 추가 절차

1. **item_code 확인**
   - `docs/CURRENCY_MAPPING_TABLE.md`에서 해당 통화의 `item_code` 확인
   - 또는 ECOS API를 직접 테스트하여 확인

2. **BOK_MAPPING 업데이트**
   - `server/bok_backend.py`의 `BOK_MAPPING["exchange"]["items"]`에 추가

3. **프론트엔드 업데이트** (필요시)
   - `frontend/ai_studio_code_F2.html`에 통화 버튼 및 색상 추가
   - 이 작업은 프론트엔드 Agent와 협업

4. **문서 업데이트**
   - `docs/CURRENCY_MAPPING_TABLE.md` 업데이트

## 에러 처리

1. **API 에러 응답 구조**
```json
{
    "RESULT": {
        "CODE": "ERROR-001",
        "MESSAGE": "에러 메시지"
    }
}
```

2. **에러 코드 처리**
   - `INFO-000`: 정상
   - 그 외: 에러 처리 및 로깅

3. **타임아웃 처리**
   - API 타임아웃은 30초로 설정
   - 타임아웃 발생 시 명확한 에러 메시지 반환

## 데이터 검증

1. **날짜 형식 검증**
   - `validate_date_format()` 함수 사용
   - YYYYMMDD 형식만 허용

2. **날짜 범위 검증**
   - 시작일이 종료일보다 늦을 수 없음
   - 최대 조회 기간: 5년 (1825일)

3. **주기 검증**
   - 유효한 주기: D, M, Q, Y, A

## 로깅

1. **로깅 레벨**
   - INFO: 정상 API 호출
   - WARNING: Fallback API 키 사용 등
   - ERROR: API 에러, 타임아웃 등

2. **로깅 내용**
   - API 요청 파라미터
   - 응답 데이터 개수
   - 에러 메시지

## 테스트

1. **API 테스트**
   - 새로운 통화 추가 시 실제 API 호출 테스트
   - 다양한 날짜 범위 테스트
   - 에러 케이스 테스트

2. **통합 테스트**
   - 백엔드 → 프론트엔드 데이터 흐름 확인
   - 프론트엔드 렌더링 확인

## 참고 파일

- `@docs/api/ecos/` - 한국은행 ECOS API 개발 명세서
- `@server/bok_backend.py` - API 연동 모듈
- `@docs/CURRENCY_MAPPING_TABLE.md` - 통화 매핑 테이블
- `@server/main.py` - Flask API 엔드포인트

