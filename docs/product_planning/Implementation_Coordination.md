# ECOS 추가 제품 구현 협의 문서

## 개요

이 문서는 ECOS API 기반 추가 제품(Inflation, GDP, Money Supply, Economic Sentiment, Balance of Payments) 구현 시 UI/UX, 백엔드, 프론트엔드 Agent 간 협의 사항을 정리합니다.

---

## 1. UI/UX Agent 협의 사항

### 1.1 디자인 일관성

**기존 Exchange Rate 및 Interest Rates와 동일한 UI 패턴 유지:**

1. **제품 전환 메뉴**
   - 좌측 사이드바에 제품 목록 표시
   - 현재 선택된 제품은 `selected` 클래스로 강조
   - 제품 전환 시 `switchProduct()` 함수 사용

2. **필터 섹션 레이아웃**
   - 날짜 범위 선택기: 시작일/종료일 입력 필드
   - 빠른 기간 버튼: 제품별 적절한 버튼 구성
   - 항목 선택기: 제품별 항목 (라디오/체크박스)

3. **차트 헤더**
   - 현재값, 변동률, 통계 요약 (고점/저점/평균)
   - Exchange Rate와 동일한 스타일 및 애니메이션

4. **차트 영역**
   - SVG 기반 인터랙티브 차트
   - 동일한 툴팁 스타일 및 위치 계산 로직

### 1.2 색상 시스템 확장

**새로운 제품별 색상 정의 필요:**

```css
/* 물가 (Inflation) */
--c-cpi-total: #3b82f6;      /* Blue - 총지수 */
--c-cpi-fresh: #22c55e;      /* Green - 신선식품 */
--c-cpi-industrial: #f59e0b;  /* Amber - 공업제품 */

/* GDP */
--c-gdp-total: #3b82f6;      /* Blue - GDP 총액 */
--c-gdp-consumption: #22c55e; /* Green - 소비 */
--c-gdp-investment: #f59e0b;  /* Amber - 투자 */

/* 통화 공급량 (Money Supply) */
--c-base-money: #3b82f6;     /* Blue - 본원통화 */
--c-m1: #22c55e;             /* Green - M1 */
--c-m2: #f59e0b;             /* Amber - M2 */

/* 경기 지표 (Economic Sentiment) */
--c-industrial: #3b82f6;     /* Blue - 산업생산 */
--c-bsi: #ec4899;            /* Pink - BSI */
--c-ccsi: #eab308;           /* Yellow - CCSI */

/* 국제 수지 (Balance of Payments) */
--c-current-account: #3b82f6;    /* Blue - 경상수지 */
--c-trade-balance: #22c55e;     /* Green - 상품수지 */
--c-service-balance: #f59e0b;   /* Amber - 서비스수지 */
```

**색상 선택 원칙:**
- 기존 통화 색상과 구분되도록 선택
- 색맹 친화적 팔레트 유지
- 다중 시리즈 비교 시 명확한 구분

### 1.3 반응형 디자인

**모든 제품에 동일한 반응형 규칙 적용:**

1. **모바일 (< 768px)**
   - 단일 항목 뷰 (멀티 선택 시 첫 번째 항목만 표시)
   - 필터 섹션 접기/펼치기 기능
   - 터치 친화적 버튼 크기 (최소 44px)

2. **태블릿 (768px - 1024px)**
   - 2컬럼 레이아웃 가능 (필터 + 차트)
   - 멀티 시리즈 표시 가능

3. **데스크톱 (> 1024px)**
   - 전체 기능 표시
   - 최대 너비 1440px

### 1.4 애니메이션

**기존 Exchange Rate와 동일한 애니메이션 패턴:**

1. **차트 헤더**
   - `fadeInUp` 애니메이션
   - 숫자 카운트업 애니메이션 (`animateValue`)

2. **차트 렌더링**
   - 부드러운 전환 효과
   - 데이터 업데이트 시 페이드 인

3. **제품 전환**
   - 페이드 아웃 → 페이드 인 효과

---

## 2. 백엔드 Agent 협의 사항

### 2.1 API 엔드포인트

**기존 `/api/market/indices` 엔드포인트 재사용:**

- 모든 제품은 `type` 파라미터로 구분
- 기존 백엔드 코드 수정 불필요 (이미 `BOK_MAPPING`에 정의됨)

**엔드포인트 예시:**
```
GET /api/market/indices?type=inflation&itemCode=CPI_TOTAL&startDate=20240101&endDate=20241231&cycle=M
GET /api/market/indices?type=gdp&itemCode=GDP_TOTAL&startDate=20230101&endDate=20241231&cycle=Q
GET /api/market/indices?type=money&itemCode=M2&startDate=20240101&endDate=20241231&cycle=M
GET /api/market/indices?type=sentiment&itemCode=INDUSTRIAL_PRODUCTION&startDate=20240101&endDate=20241231&cycle=M
GET /api/market/indices?type=balance&itemCode=CURRENT_ACCOUNT&startDate=20240101&endDate=20241231&cycle=M
```

### 2.2 통계 정보 API

**기존 `/api/market/indices/stats` 엔드포인트 재사용:**

- 모든 제품에 동일한 통계 계산 로직 적용
- `calculate_statistics()` 함수는 범용적으로 사용 가능

**응답 형식:**
```json
{
  "currency": "CPI_TOTAL",
  "high": 106.1,
  "low": 103.8,
  "average": 105.2,
  "current": 105.2,
  "previous": 104.9,
  "change": 0.3,
  "changePercent": 0.29
}
```

**주의사항:**
- `currency` 필드는 제품별 항목 코드로 대체 (예: "CPI_TOTAL", "GDP_TOTAL")
- 프론트엔드에서 필드명 해석 필요

### 2.3 데이터 검증

**기존 검증 로직 재사용:**

1. **날짜 형식 검증**
   - `validate_date_format()` 함수 사용
   - YYYYMMDD 형식만 허용

2. **날짜 범위 검증**
   - 시작일 ≤ 종료일
   - 최대 조회 기간: 5년 (1825일)

3. **주기 검증**
   - 제품별 기본 주기 사용 (M, Q 등)
   - 주기별 날짜 형식 변환 (`format_date_for_cycle()`)

### 2.4 에러 처리

**기존 에러 처리 패턴 유지:**

1. **API 에러 응답**
   ```json
   {
     "error": "BOK API Error [ERROR-101]: 주기와 다른 형식의 날짜 형식입니다.",
     "result_code": "ERROR-101",
     "result_message": "주기와 다른 형식의 날짜 형식입니다."
   }
   ```

2. **HTTP 상태 코드**
   - 400: Bad Request (잘못된 파라미터)
   - 500: Internal Server Error (API 호출 실패)

### 2.5 로깅

**기존 로깅 패턴 유지:**

- INFO: 정상 API 호출
- WARNING: 데이터 부재, Fallback API 키 사용
- ERROR: API 에러, 타임아웃

---

## 3. 프론트엔드 Agent 협의 사항

### 3.1 제품 전환 함수

**기존 `switchProduct()` 함수 확장:**

```javascript
function switchProduct(productName) {
    // 기존: 'exchange-rate', 'interest-rates'
    // 추가: 'inflation', 'gdp', 'money', 'sentiment', 'balance'
    
    // 모든 패널 숨기기
    const panels = ['economy-panel', 'interest-rates-panel', 
                    'inflation-panel', 'gdp-panel', 'money-panel', 
                    'sentiment-panel', 'balance-panel'];
    panels.forEach(panelId => {
        const panel = document.getElementById(panelId);
        if (panel) panel.style.display = 'none';
    });
    
    // 선택된 패널 표시
    const targetPanel = document.getElementById(`${productName}-panel`);
    if (targetPanel) {
        targetPanel.style.display = 'block';
        // 초기화 함수 호출
        initProduct(productName);
    }
}
```

### 3.2 데이터 처리 함수

**제품별 데이터 처리 함수 생성:**

각 제품마다 다음 함수들을 생성:

1. **데이터 조회 함수**
   ```javascript
   function fetchInflationData() { ... }
   function fetchGDPData() { ... }
   // 등등
   ```

2. **데이터 처리 함수**
   ```javascript
   function processInflationData(data) { ... }
   function processGDPData(data) { ... }
   // 등등
   ```

3. **차트 렌더링 함수**
   ```javascript
   function updateInflationChart() { ... }
   function updateGDPChart() { ... }
   // 등등
   ```

**공통 패턴:**
- Exchange Rate 및 Interest Rates와 동일한 구조
- 함수명만 제품별로 변경
- 로직은 대부분 재사용 가능

### 3.3 차트 렌더링

**SVG 차트 렌더링 패턴:**

1. **기본 구조**
   - SVG `viewBox` 설정
   - 그리드 라인 렌더링
   - 데이터 라인/막대 렌더링
   - X/Y축 레이블 렌더링

2. **인터랙티브 요소**
   - 마우스 이벤트 리스너
   - 툴팁 표시/숨김
   - 범례 클릭 이벤트

3. **성능 최적화**
   - `requestAnimationFrame` 사용
   - 이벤트 스로틀링
   - DOM 조작 최소화

### 3.4 필터 및 컨트롤

**제품별 필터 구성:**

1. **날짜 범위 선택기**
   - 모든 제품 공통 사용
   - `YYYY-MM-DD` 형식 입력

2. **빠른 기간 버튼**
   - 제품별 적절한 버튼 구성
   - 예: Inflation → "1년", "2년", "5년", "10년"
   - 예: GDP → "최근 2년", "최근 5년", "최근 10년"

3. **항목 선택기**
   - 제품별 항목 구성
   - 라디오 버튼 (단일 선택) 또는 체크박스 (다중 선택)

4. **주기 선택기**
   - 제품별 기본 주기 사용
   - 필요 시 주기 변경 옵션 제공

### 3.5 통계 요약 표시

**기존 `updateChartHeader()` 함수 패턴 재사용:**

```javascript
function updateInflationChartHeader() {
    // /api/market/indices/stats 호출
    // 응답 데이터로 헤더 업데이트
    // animateValue() 함수로 숫자 애니메이션
}
```

**표시 항목:**
- 현재값
- 변동률 (전년 동월 대비 또는 전월 대비)
- 통계 요약 (고점, 저점, 평균)

---

## 4. 구현 우선순위 및 단계

### Phase 1 (높은 우선순위)

1. **Inflation (물가)**
   - 일반인 관심도 높음
   - 이해하기 쉬움
   - 월별 데이터로 구현 복잡도 낮음

2. **GDP (국민소득)**
   - 핵심 경제 지표
   - 정책 분석에 필수
   - 분기별 데이터로 구현 복잡도 중간

### Phase 2 (중간 우선순위)

3. **Economic Sentiment (경기)**
   - 경기 전망에 유용
   - 다중 지표 통합 대시보드

4. **Balance of Payments (국제 수지)**
   - 무역 분석에 중요
   - 적자/흑자 시각화

### Phase 3 (낮은 우선순위)

5. **Money Supply (통화 및 금융)**
   - 전문가 대상
   - 복잡도 높음 (이중 Y축 등)

---

## 5. 구현 체크리스트

### 백엔드

- [ ] `BOK_MAPPING`에 모든 카테고리 정의 확인 (이미 완료)
- [ ] `/api/market/indices` 엔드포인트가 모든 `type` 지원 확인 (이미 완료)
- [ ] `/api/market/indices/stats` 엔드포인트가 모든 제품 지원 확인
- [ ] 에러 처리 및 로깅 확인

### 프론트엔드

- [ ] 제품 전환 메뉴에 새 제품 추가
- [ ] 각 제품별 HTML 섹션 생성
- [ ] 각 제품별 JavaScript 함수 생성
- [ ] CSS 변수에 새 색상 추가
- [ ] 반응형 디자인 테스트

### UI/UX

- [ ] 디자인 일관성 확인
- [ ] 색상 팔레트 확장
- [ ] 애니메이션 일관성 확인
- [ ] 접근성 체크리스트 확인

---

## 6. 테스트 계획

### 단위 테스트

1. **백엔드**
   - 각 제품별 API 호출 테스트
   - 에러 케이스 테스트
   - 데이터 검증 테스트

2. **프론트엔드**
   - 데이터 처리 함수 테스트
   - 차트 렌더링 테스트
   - 필터 동작 테스트

### 통합 테스트

1. **API → 프론트엔드 데이터 흐름**
   - 실제 API 호출 테스트
   - 데이터 파싱 및 표시 확인

2. **사용자 시나리오 테스트**
   - 제품 전환
   - 필터 변경
   - 차트 인터랙션

### 사용성 테스트

1. **반응형 디자인**
   - 모바일, 태블릿, 데스크톱 테스트

2. **접근성**
   - 키보드 네비게이션
   - 스크린 리더 지원
   - 색상 대비

---

## 7. 참고 문서

- [상세 기능 기획안](./ECOS_Additional_Products_Planning.md)
- [Planner 규칙](../.cursor/rules/Planner/RULE.md)
- [UI/UX 규칙](../.cursor/rules/uiux-rule/RULE.md)
- [백엔드 규칙](../.cursor/rules/backend-rule/RULE.md)
- [프론트엔드 규칙](../.cursor/rules/frontend-rule/RULE.md)

---

이 문서는 각 Agent가 협업하여 추가 제품을 구현할 때 참고하는 가이드입니다. 구현 과정에서 추가 협의가 필요한 사항은 이 문서를 업데이트하거나 별도 문서로 정리합니다.

