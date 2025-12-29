# ECOS API 기반 추가 제품 기획안

## 개요

이 문서는 한국은행 ECOS API를 활용하여 추가로 개발 가능한 경제 지표 제품들의 상세 기능 기획안입니다. 현재 Exchange Rate(환율)와 Interest Rates(기준금리)가 구현되어 있으며, 백엔드에 정의되어 있지만 프론트엔드에 미구현된 5개 제품에 대한 기획안을 제시합니다.

---

## 1. Inflation (물가) - 소비자물가지수

### 1.1 개요 (Overview)

**기능 정의:** 소비자물가지수(CPI) 및 세부 항목(신선식품, 공업제품)의 추이를 시각화하고, 인플레이션율을 계산하여 표시하는 기능

**해결하려는 문제:** 
- 일반인과 기업이 물가 동향을 쉽게 파악하기 어려움
- 인플레이션율 계산을 수동으로 해야 하는 불편함
- 신선식품과 공업제품의 물가 변동을 비교하기 어려움

**비즈니스 가치:**
- 소비자: 구매 시기 결정 지원
- 기업: 가격 정책 수립 지원
- 정책 분석가: 통화정책 효과 분석 지원

### 1.2 유저 스토리 (User Story)

- `As a 소비자, I want to view CPI trends over the past year, So that I can understand how prices have changed`
- `As a 기업 경영자, I want to compare fresh food CPI vs industrial goods CPI, So that I can adjust pricing strategies`
- `As a 정책 분석가, I want to see inflation rate calculations, So that I can analyze monetary policy effectiveness`

### 1.3 데이터 소스 및 API 매핑

**API Source:** 한국은행 ECOS API
- **통계표 코드:** `901Y001` (소비자물가지수)
- **주기:** M (월별)
- **엔드포인트:** `/api/market/indices?type=inflation`

**Key Metrics:**
- CPI_TOTAL: 소비자물가지수 (총지수) - 기본값
- CPI_FRESH: 신선식품 물가지수
- CPI_INDUSTRIAL: 공업제품 물가지수

**Data Mapping:**
- **Input:** 
  - 사용자 입력: 시작일, 종료일, 선택 항목 (총지수/신선식품/공업제품)
  - API 파라미터: `type=inflation`, `itemCode=CPI_TOTAL|CPI_FRESH|CPI_INDUSTRIAL`, `cycle=M`, `startDate`, `endDate`
- **Process:**
  - 전년 동월 대비 상승률 계산: `((현재값 - 전년동월값) / 전년동월값) * 100`
  - 인플레이션율 계산: 연간 물가 상승률
  - 전월 대비 변화율 계산
- **Output:**
  - 시계열 데이터: `{date: "202412", value: 105.2}`
  - 통계 요약: `{current: 105.2, yoy: 2.5, mom: 0.3, high: 106.1, low: 103.8}`

### 1.4 시각화 설계 (Visualization Design)

**차트 타입:**
- **메인 차트:** Time-Series Line Chart (꺾은선 그래프)
- **비교 차트:** Multi-series Line Chart (신선식품 vs 공업제품 비교 시)

**X축/Y축:**
- X축: 월 (예: "2024.01", "2024.02", ...)
- Y축: 물가지수 (기준년도 = 100)

**다중 시리즈:**
- 총지수, 신선식품, 공업제품을 동시에 표시 가능
- 각 시리즈별 색상 구분 (총지수: 파란색, 신선식품: 초록색, 공업제품: 주황색)

**인터랙티브 요소:**
- 호버 툴팁: 날짜, 물가지수, 전년 동월 대비 상승률
- 범례 클릭: 시리즈 표시/숨김 토글
- 줌: 특정 기간 확대

### 1.5 사용자 컨트롤 및 필터 (User Controls & Filters)

**날짜 범위 선택기:**
- 시작일/종료일 캘린더 선택
- 빠른 선택 버튼: "1년", "2년", "5년", "10년"

**항목 선택기:**
- 라디오 버튼 또는 드롭다운: "총지수", "신선식품", "공업제품"
- 멀티 선택 모드: 여러 항목 동시 비교

**뷰 모드:**
- 그래프 뷰 (기본)
- 테이블 뷰: 월별 상세 데이터 표시

### 1.6 UI/UX 제안 (Wireframe Description)

**화면 구성 요소:**
1. **헤더 섹션:**
   - 제목: "소비자물가지수 (CPI)"
   - 현재값, 전년 동월 대비 상승률, 전월 대비 변화율 표시
   - 통계 요약: 고점, 저점, 평균

2. **필터 섹션:**
   - 날짜 범위 선택기
   - 항목 선택기 (총지수/신선식품/공업제품)
   - 빠른 기간 선택 버튼

3. **차트 섹션:**
   - 메인 꺾은선 그래프
   - 범례 (항목별 색상 표시)
   - X축: 월별 라벨
   - Y축: 물가지수 라벨

4. **인사이트 섹션 (선택적):**
   - "인플레이션율: 2.5% (전년 대비)"
   - "최근 3개월 평균 상승률: 0.2%"

**레이아웃 구조:**
- Exchange Rate와 동일한 레이아웃 구조 유지
- 반응형 디자인: 모바일에서는 단일 항목 뷰

**디자인 일관성:**
- 기존 Exchange Rate UI와 동일한 색상 팔레트 및 폰트 사용
- 차트 스타일 통일 (SVG 기반)

### 1.7 개발 시 고려사항 (Tech Notes)

**API Rate Limit:**
- 월별 데이터이므로 호출 빈도 낮음
- 캐싱: 일일 1회 갱신

**에러 처리:**
- 데이터 부재 시: "해당 기간의 데이터가 없습니다" 메시지
- API 타임아웃: 재시도 로직 또는 캐시 데이터 표시

**데이터 품질:**
- 물가지수는 보통 매월 말에 전월 데이터 공개
- 최신 데이터 부재 시 안내 메시지 표시

**성능 최적화:**
- 10년 이상 데이터 조회 시 샘플링 고려 (연간 평균 표시 옵션)

**보안:**
- 사용자 입력 검증 (날짜 형식, 범위 제한)

---

## 2. GDP (국민소득) - 실질 국내총생산

### 2.1 개요 (Overview)

**기능 정의:** 분기별 실질 GDP 및 구성 요소(소비, 투자)의 추이를 시각화하고, 성장률을 계산하여 표시하는 기능

**해결하려는 문제:**
- GDP 데이터를 분기별로 추적하기 어려움
- GDP 구성 요소(소비 vs 투자) 비교가 불편함
- 전년 동기 대비 성장률 계산이 복잡함

**비즈니스 가치:**
- 투자자: 경제 성장 전망 파악
- 기업: 경기 사이클 대응 전략 수립
- 정책 분석가: 재정정책 효과 분석

### 2.2 유저 스토리 (User Story)

- `As a 투자자, I want to view quarterly GDP growth rates, So that I can assess economic health`
- `As a 기업 경영자, I want to compare consumption vs investment trends, So that I can plan business strategies`
- `As a 정책 분석가, I want to see GDP component breakdowns, So that I can analyze economic structure`

### 2.3 데이터 소스 및 API 매핑

**API Source:** 한국은행 ECOS API
- **통계표 코드:** `200Y002` (실질 국내총생산(지출))
- **주기:** Q (분기별)
- **엔드포인트:** `/api/market/indices?type=gdp`

**Key Metrics:**
- GDP_TOTAL: 국내총생산 (GDP) - 기본값
- GDP_CONSUMPTION: 개인소비지출
- GDP_INVESTMENT: 총고정자본형성

**Data Mapping:**
- **Input:**
  - 사용자 입력: 시작일, 종료일, 선택 항목 (GDP/소비/투자)
  - API 파라미터: `type=gdp`, `itemCode=GDP_TOTAL|GDP_CONSUMPTION|GDP_INVESTMENT`, `cycle=Q`, `startDate`, `endDate`
- **Process:**
  - 전년 동기 대비 성장률: `((현재분기 - 전년동기분기) / 전년동기분기) * 100`
  - 전분기 대비 성장률: `((현재분기 - 전분기) / 전분기) * 100`
  - 연간 GDP 추정: 4개 분기 합계 또는 평균
- **Output:**
  - 시계열 데이터: `{date: "2024Q1", value: 450.2}`
  - 통계 요약: `{current: 450.2, yoy: 2.1, qoq: 0.5, high: 455.8, low: 420.1}`

### 2.4 시각화 설계 (Visualization Design)

**차트 타입:**
- **메인 차트:** Time-Series Line Chart with Markers (분기별 데이터 포인트 강조)
- **비교 차트:** Grouped Bar Chart (소비 vs 투자 비교 시)
- **구성 차트:** Stacked Area Chart (GDP 구성 요소 비중 시각화)

**X축/Y축:**
- X축: 분기 (예: "2024Q1", "2024Q2", ...)
- Y축: GDP (조원, 또는 지수)

**다중 시리즈:**
- GDP 총액, 소비, 투자를 동시에 표시 가능
- 각 시리즈별 색상 구분

**인터랙티브 요소:**
- 호버 툴팁: 분기, GDP 값, 전년 동기 대비 성장률, 전분기 대비 성장률
- 범례 클릭: 시리즈 표시/숨김 토글

### 2.5 사용자 컨트롤 및 필터 (User Controls & Filters)

**날짜 범위 선택기:**
- 시작일/종료일 캘린더 선택
- 빠른 선택 버튼: "최근 2년", "최근 5년", "최근 10년"

**항목 선택기:**
- 라디오 버튼 또는 드롭다운: "GDP 총액", "개인소비지출", "총고정자본형성"
- 멀티 선택 모드: 여러 항목 동시 비교

**뷰 모드:**
- 그래프 뷰 (기본)
- 테이블 뷰: 분기별 상세 데이터 표시
- 성장률 뷰: 성장률만 강조 표시

### 2.6 UI/UX 제안 (Wireframe Description)

**화면 구성 요소:**
1. **헤더 섹션:**
   - 제목: "실질 국내총생산 (GDP)"
   - 현재값 (최신 분기), 전년 동기 대비 성장률, 전분기 대비 성장률
   - 통계 요약: 고점, 저점, 평균

2. **필터 섹션:**
   - 날짜 범위 선택기
   - 항목 선택기 (GDP/소비/투자)
   - 빠른 기간 선택 버튼

3. **차트 섹션:**
   - 메인 꺾은선 그래프 (분기별 마커 표시)
   - 범례
   - X축: 분기별 라벨
   - Y축: GDP 값 라벨

4. **인사이트 섹션:**
   - "연간 GDP 추정: 1,800조원"
   - "최근 4분기 평균 성장률: 2.3%"

**레이아웃 구조:**
- Exchange Rate와 동일한 레이아웃 구조 유지

### 2.7 개발 시 고려사항 (Tech Notes)

**API Rate Limit:**
- 분기별 데이터이므로 호출 빈도 매우 낮음
- 캐싱: 주간 1회 갱신

**에러 처리:**
- 데이터 부재 시: "해당 기간의 데이터가 없습니다" 메시지
- GDP 데이터는 보통 분기 종료 후 2-3개월 후 공개

**데이터 품질:**
- GDP는 수정 발표가 많으므로 "예비" vs "확정" 구분 표시 (가능한 경우)

**성능 최적화:**
- 10년 이상 데이터 조회 시 샘플링 고려

---

## 3. Money Supply (통화 및 금융) - 통화 공급량

### 3.1 개요 (Overview)

**기능 정의:** M1, M2, 본원통화 등 통화 공급량 추이를 시각화하고, 성장률 및 비율을 분석하는 기능

**해결하려는 문제:**
- 통화 공급량 지표를 한눈에 비교하기 어려움
- M1/M2 비율 변화를 추적하기 불편함
- 금리와의 상관관계 파악이 어려움

**비즈니스 가치:**
- 투자자: 유동성 동향 파악
- 경제 분석가: 통화정책 효과 분석
- 기업: 자금 조달 전략 수립

### 3.2 유저 스토리 (User Story)

- `As a 투자자, I want to view M2 money supply trends, So that I can assess liquidity conditions`
- `As a 경제 분석가, I want to compare M1 vs M2 growth rates, So that I can analyze monetary policy`
- `As a 기업 재무담당자, I want to see money supply and interest rate correlation, So that I can plan financing`

### 3.3 데이터 소스 및 API 매핑

**API Source:** 한국은행 ECOS API
- **통계표 코드:** `102Y004` (본원통화 구성내역)
- **주기:** M (월별)
- **엔드포인트:** `/api/market/indices?type=money`

**Key Metrics:**
- BASE_MONEY: 본원통화 - 기본값
- M2: M2 (광의통화)
- M1: M1 (협의통화)

**Data Mapping:**
- **Input:**
  - 사용자 입력: 시작일, 종료일, 선택 항목 (본원통화/M1/M2)
  - API 파라미터: `type=money`, `itemCode=BASE_MONEY|M1|M2`, `cycle=M`, `startDate`, `endDate`
- **Process:**
  - 전년 동월 대비 성장률 계산
  - M1/M2 비율 계산: `(M1 / M2) * 100`
  - 통화 공급량 성장률 추이
- **Output:**
  - 시계열 데이터: `{date: "202412", value: 350.5}`
  - 통계 요약: `{current: 350.5, yoy: 5.2, mom: 0.3, high: 360.1, low: 320.5}`
  - 비율 데이터: `{m1_m2_ratio: 25.3}`

### 3.4 시각화 설계 (Visualization Design)

**차트 타입:**
- **메인 차트:** Multi-series Line Chart (M1, M2, 본원통화 동시 표시)
- **비율 차트:** Secondary Y-axis Line Chart (M1/M2 비율)

**X축/Y축:**
- X축: 월 (예: "2024.01", "2024.02", ...)
- Y축 (왼쪽): 통화 공급량 (조원)
- Y축 (오른쪽): M1/M2 비율 (%)

**다중 시리즈:**
- 본원통화, M1, M2를 동시에 표시
- 각 시리즈별 색상 구분

**인터랙티브 요소:**
- 호버 툴팁: 날짜, 통화 공급량, 전년 동월 대비 성장률
- 범례 클릭: 시리즈 표시/숨김 토글

### 3.5 사용자 컨트롤 및 필터 (User Controls & Filters)

**날짜 범위 선택기:**
- 시작일/종료일 캘린더 선택
- 빠른 선택 버튼: "1년", "2년", "5년"

**항목 선택기:**
- 체크박스: "본원통화", "M1", "M2" (다중 선택 가능)

**비율 표시 토글:**
- "M1/M2 비율 표시" 체크박스

**뷰 모드:**
- 그래프 뷰 (기본)
- 테이블 뷰: 월별 상세 데이터 표시

### 3.6 UI/UX 제안 (Wireframe Description)

**화면 구성 요소:**
1. **헤더 섹션:**
   - 제목: "통화 공급량"
   - 현재값 (M2), 전년 동월 대비 성장률
   - 통계 요약: 고점, 저점, 평균

2. **필터 섹션:**
   - 날짜 범위 선택기
   - 항목 선택기 (본원통화/M1/M2)
   - M1/M2 비율 표시 토글

3. **차트 섹션:**
   - 메인 다중 시리즈 꺾은선 그래프
   - 이중 Y축 (통화 공급량 + 비율)
   - 범례

**레이아웃 구조:**
- Exchange Rate와 동일한 레이아웃 구조 유지

### 3.7 개발 시 고려사항 (Tech Notes)

**API Rate Limit:**
- 월별 데이터이므로 호출 빈도 낮음
- 캐싱: 일일 1회 갱신

**에러 처리:**
- 데이터 부재 시 안내 메시지

**데이터 품질:**
- 통화 공급량은 보통 매월 말에 전월 데이터 공개

**성능 최적화:**
- 이중 Y축 렌더링 최적화

---

## 4. Economic Sentiment (경기) - 경기 지표

### 4.1 개요 (Overview)

**기능 정의:** 산업생산지수, 기업경기실사지수(BSI), 소비자심리지수(CCSI) 등 경기 지표를 통합 대시보드로 시각화하는 기능

**해결하려는 문제:**
- 여러 경기 지표를 한눈에 비교하기 어려움
- 경기 사이클을 파악하기 불편함
- 지표 간 상관관계 분석이 어려움

**비즈니스 가치:**
- 투자자: 경기 전망 파악
- 기업: 경기 사이클 대응 전략 수립
- 정책 분석가: 경기 정책 효과 분석

### 4.2 유저 스토리 (User Story)

- `As a 투자자, I want to view multiple economic sentiment indicators together, So that I can assess economic outlook`
- `As a 기업 경영자, I want to see industrial production and BSI trends, So that I can plan production`
- `As a 정책 분석가, I want to analyze correlation between production and consumer sentiment, So that I can evaluate policy effectiveness`

### 4.3 데이터 소스 및 API 매핑

**API Source:** 한국은행 ECOS API
- **통계표 코드:** `801Y001` (산업활동동향)
- **주기:** M (월별)
- **엔드포인트:** `/api/market/indices?type=sentiment`

**Key Metrics:**
- INDUSTRIAL_PRODUCTION: 산업생산지수 - 기본값
- BSI: 기업경기실사지수 (BSI)
- CCSI: 소비자심리지수 (CCSI)

**Data Mapping:**
- **Input:**
  - 사용자 입력: 시작일, 종료일, 선택 항목 (생산/BSI/CCSI)
  - API 파라미터: `type=sentiment`, `itemCode=INDUSTRIAL_PRODUCTION|BSI|CCSI`, `cycle=M`, `startDate`, `endDate`
- **Process:**
  - 전년 동월 대비 변화율 계산
  - 지표 간 상관관계 계산 (선택적)
  - 경기 사이클 구간 표시 (호황/침체)
- **Output:**
  - 시계열 데이터: `{date: "202412", value: 105.2}`
  - 통계 요약: `{current: 105.2, yoy: 2.1, mom: 0.5, high: 110.5, low: 95.2}`

### 4.4 시각화 설계 (Visualization Design)

**차트 타입:**
- **메인 차트:** Multi-series Line Chart (3개 지표 동시 표시)
- **대시보드 뷰:** 3개의 작은 차트 (각 지표별)

**X축/Y축:**
- X축: 월 (예: "2024.01", "2024.02", ...)
- Y축: 지수 (기준년도 = 100 또는 기준선 = 100)

**다중 시리즈:**
- 산업생산지수, BSI, CCSI를 동시에 표시
- 각 시리즈별 색상 구분

**인터랙티브 요소:**
- 호버 툴팁: 날짜, 지수 값, 전년 동월 대비 변화율
- 범례 클릭: 시리즈 표시/숨김 토글
- 경기 사이클 구간 하이라이트 (선택적)

### 4.5 사용자 컨트롤 및 필터 (User Controls & Filters)

**날짜 범위 선택기:**
- 시작일/종료일 캘린더 선택
- 빠른 선택 버튼: "1년", "2년", "5년"

**항목 선택기:**
- 체크박스: "산업생산지수", "BSI", "CCSI" (다중 선택 가능)

**뷰 모드:**
- 통합 뷰 (기본): 3개 지표를 하나의 차트에 표시
- 대시보드 뷰: 3개의 작은 차트로 분리 표시
- 테이블 뷰: 월별 상세 데이터 표시

### 4.6 UI/UX 제안 (Wireframe Description)

**화면 구성 요소:**
1. **헤더 섹션:**
   - 제목: "경기 지표"
   - 현재값 (각 지표별), 전년 동월 대비 변화율
   - 통계 요약: 고점, 저점, 평균

2. **필터 섹션:**
   - 날짜 범위 선택기
   - 항목 선택기 (생산/BSI/CCSI)
   - 뷰 모드 토글 (통합/대시보드)

3. **차트 섹션:**
   - 메인 다중 시리즈 꺾은선 그래프 (통합 뷰)
   - 또는 3개의 작은 차트 (대시보드 뷰)
   - 범례

**레이아웃 구조:**
- Exchange Rate와 동일한 레이아웃 구조 유지
- 대시보드 뷰는 3열 그리드 레이아웃

### 4.7 개발 시 고려사항 (Tech Notes)

**API Rate Limit:**
- 월별 데이터이므로 호출 빈도 낮음
- 캐싱: 일일 1회 갱신

**에러 처리:**
- 일부 지표 데이터 부재 시: 해당 지표만 숨김 처리

**데이터 품질:**
- BSI, CCSI는 보통 매월 말에 전월 데이터 공개

**성능 최적화:**
- 다중 시리즈 렌더링 최적화

---

## 5. Balance of Payments (국제 수지) - 경상수지

### 5.1 개요 (Overview)

**기능 정의:** 경상수지, 상품수지, 서비스수지의 추이를 시각화하고, 적자/흑자 구간을 명확히 표시하는 기능

**해결하려는 문제:**
- 경상수지 적자/흑자 구간을 한눈에 파악하기 어려움
- 상품수지 vs 서비스수지 비교가 불편함
- 환율과의 상관관계 파악이 어려움

**비즈니스 가치:**
- 투자자: 외환 시장 동향 파악
- 무역 기업: 수출입 전략 수립
- 정책 분석가: 국제 수지 정책 분석

### 5.2 유저 스토리 (User Story)

- `As a 투자자, I want to view current account balance trends, So that I can assess foreign exchange market conditions`
- `As a 무역 기업 경영자, I want to compare goods balance vs services balance, So that I can plan trade strategies`
- `As a 정책 분석가, I want to see correlation between exchange rate and current account, So that I can analyze policy effects`

### 5.3 데이터 소스 및 API 매핑

**API Source:** 한국은행 ECOS API
- **통계표 코드:** `301Y002` (경상수지)
- **주기:** M (월별)
- **엔드포인트:** `/api/market/indices?type=balance`

**Key Metrics:**
- CURRENT_ACCOUNT: 경상수지 - 기본값
- TRADE_BALANCE: 상품수지
- SERVICE_BALANCE: 서비스수지

**Data Mapping:**
- **Input:**
  - 사용자 입력: 시작일, 종료일, 선택 항목 (경상수지/상품수지/서비스수지)
  - API 파라미터: `type=balance`, `itemCode=CURRENT_ACCOUNT|TRADE_BALANCE|SERVICE_BALANCE`, `cycle=M`, `startDate`, `endDate`
- **Process:**
  - 누적 경상수지 계산: 기간 내 합계
  - 적자/흑자 구간 식별: 양수/음수 구분
  - 전년 동월 대비 변화 계산
- **Output:**
  - 시계열 데이터: `{date: "202412", value: 5.2}` (억달러, 양수=흑자, 음수=적자)
  - 통계 요약: `{current: 5.2, yoy: 2.1, cumulative: 45.8, high: 8.5, low: -2.3}`

### 5.4 시각화 설계 (Visualization Design)

**차트 타입:**
- **메인 차트:** Bar Chart with Positive/Negative Colors (적자/흑자 구분)
- **비교 차트:** Multi-series Line Chart (3개 수지 동시 표시)
- **누적 차트:** Area Chart (누적 경상수지)

**X축/Y축:**
- X축: 월 (예: "2024.01", "2024.02", ...)
- Y축: 수지 (억달러, 0 기준선 표시)

**다중 시리즈:**
- 경상수지, 상품수지, 서비스수지를 동시에 표시
- 각 시리즈별 색상 구분
- 적자 구간은 빨간색, 흑자 구간은 파란색

**인터랙티브 요소:**
- 호버 툴팁: 날짜, 수지 값, 적자/흑자 표시
- 범례 클릭: 시리즈 표시/숨김 토글
- 0 기준선 강조 표시

### 5.5 사용자 컨트롤 및 필터 (User Controls & Filters)

**날짜 범위 선택기:**
- 시작일/종료일 캘린더 선택
- 빠른 선택 버튼: "1년", "2년", "5년"

**항목 선택기:**
- 체크박스: "경상수지", "상품수지", "서비스수지" (다중 선택 가능)

**차트 타입 토글:**
- "막대 그래프" vs "꺾은선 그래프" vs "누적 차트"

**뷰 모드:**
- 그래프 뷰 (기본)
- 테이블 뷰: 월별 상세 데이터 표시

### 5.6 UI/UX 제안 (Wireframe Description)

**화면 구성 요소:**
1. **헤더 섹션:**
   - 제목: "국제 수지 (경상수지)"
   - 현재값 (최신 월), 적자/흑자 표시, 전년 동월 대비 변화
   - 통계 요약: 고점, 저점, 평균, 누적 수지

2. **필터 섹션:**
   - 날짜 범위 선택기
   - 항목 선택기 (경상수지/상품수지/서비스수지)
   - 차트 타입 토글

3. **차트 섹션:**
   - 메인 차트 (막대 또는 꺾은선)
   - 0 기준선 강조
   - 범례

**레이아웃 구조:**
- Exchange Rate와 동일한 레이아웃 구조 유지

### 5.7 개발 시 고려사항 (Tech Notes)

**API Rate Limit:**
- 월별 데이터이므로 호출 빈도 낮음
- 캐싱: 일일 1회 갱신

**에러 처리:**
- 데이터 부재 시 안내 메시지

**데이터 품질:**
- 경상수지는 보통 매월 말에 전월 데이터 공개
- 수정 발표가 있을 수 있음

**성능 최적화:**
- 막대 그래프 렌더링 최적화

---

## 통합 고려사항

### 공통 UI/UX 패턴

모든 제품은 Exchange Rate와 Interest Rates와 동일한 UI 패턴을 따릅니다:

1. **제품 전환:** 좌측 사이드바에서 제품 선택
2. **필터 섹션:** 날짜 범위, 항목 선택, 빠른 기간 버튼
3. **차트 헤더:** 현재값, 변동률, 통계 요약
4. **차트 영역:** SVG 기반 인터랙티브 차트
5. **툴팁:** 마우스 호버 시 상세 정보 표시

### 백엔드 API 엔드포인트

모든 제품은 기존 `/api/market/indices` 엔드포인트를 사용하며, `type` 파라미터로 구분:

- `type=inflation` → 물가
- `type=gdp` → GDP
- `type=money` → 통화 공급량
- `type=sentiment` → 경기 지표
- `type=balance` → 국제 수지

### 프론트엔드 구현 순서

1. **Inflation (물가)** - Phase 1, 우선순위 높음
2. **GDP (국민소득)** - Phase 1, 우선순위 높음
3. **Economic Sentiment (경기)** - Phase 2
4. **Balance of Payments (국제 수지)** - Phase 2
5. **Money Supply (통화 및 금융)** - Phase 3

### 다음 단계

1. UI/UX Agent와 협의하여 디자인 일관성 확보
2. 백엔드 Agent와 API 응답 형식 확인
3. 프론트엔드 Agent와 구현 방법 협의
4. 각 제품별 우선순위에 따라 단계적 구현

