# Dashboard 기능 최종 기획안

화주/포워더가 운송 이력을 분석하고 성과를 시각화하는 대시보드 기능의 종합 기획안입니다.

---

## 1. 기능 개요

### 1.1 정의

| 항목 | 내용 |
|------|------|
| 기능 정의 | 화주/포워더가 운송 이력을 분석하고 성과를 시각화하는 대시보드 |
| 해결 문제 | 분산된 운송 데이터를 통합하여 의사결정 지원 |
| 비즈니스 가치 | 비용 절감 인사이트, 운영 효율화, 경쟁력 분석 |

### 1.2 유저 스토리

**화주 (Shipper)**
```
As a 화주,
I want to view my shipping history, cost trends, and saving rate,
So that I can optimize logistics spending and select the best forwarders.
```

**포워더 (Forwarder)**
```
As a 포워더,
I want to analyze my bidding performance and route profitability,
So that I can improve competitiveness and increase win rate.
```

---

## 2. 화주 대시보드 설계

### 2.1 KPI Cards (4개)

| KPI | 설명 | 데이터 소스 |
|-----|------|------------|
| 총 요청 건수 | 기간 내 운송 요청 총 건수 | `biddings.count` |
| 낙찰률 | 요청 대비 선정 완료 비율 | `contracts / biddings` |
| 평균 입찰 참여 | 요청당 평균 입찰 수 | `bids / biddings` |
| 평균 절감률 | 시장 평균 대비 절감 비율 | `market_rates - contracts` |

### 2.2 차트 구성

```
+-------------------------------------------+---------------+
|                                           |               |
|  [Area Chart]                             | [Doughnut]    |
|  월별 물량 추이                            | 운송타입별     |
|  (TEU/CBM/KGS)                            | 비용 비중      |
|                                           |               |
+-------------------------------------------+---------------+
|                                           |               |
|  [Horizontal Bar]                         | [Table]       |
|  자주 이용하는 구간 TOP 10                 | 운송사 선정    |
|                                           | 순위          |
|                                           |               |
+-------------------------------------------+---------------+
|                                                           |
|  [Summary Card] 총 운송비용                               |
|                                                           |
+-----------------------------------------------------------+
```

### 2.3 추가 분석 지표

| 지표 | 시각화 | 설명 |
|------|--------|------|
| 주요 수출국 TOP 5 | Horizontal Bar | POL 기준 물량 집계 |
| 주요 수입국 TOP 5 | Horizontal Bar | POD 기준 물량 집계 |
| 주요 운송 품목 | Treemap / Bar | HS Code 기준 분류 |
| FCL 적재 효율 | Gauge / Progress | `실제중량 / 최대적재량` |

---

## 3. 포워더 대시보드 설계

### 3.1 KPI Cards (4개)

| KPI | 설명 | 데이터 소스 |
|-----|------|------------|
| 총 입찰 건수 | 제출된 입찰 총 건수 | `bids.count` |
| 낙찰률 | 입찰 대비 낙찰 비율 | `contracts / bids` |
| 평균 순위 | 가격 경쟁력 기준 순위 | `bid_rank avg` |
| 평균 평점 | 고객 평가 점수 | `ratings avg` |

### 3.2 구간별 낙찰 현황 (Table + Sparkline)

```
+----------------+--------+--------+---------+-----------+---------------+
| 구간           | 입찰   | 낙찰   | 낙찰률   | 총 수주액  | 월별 추이      |
+----------------+--------+--------+---------+-----------+---------------+
| 부산 → LA      | 15건   | 8건    | 53.3%   | ₩120M     | [sparkline]   |
| 부산 → 상하이   | 12건   | 5건    | 41.7%   | ₩45M      | [sparkline]   |
| 인천 → 나리타   | 8건    | 4건    | 50.0%   | ₩32M      | [sparkline]   |
+----------------+--------+--------+---------+-----------+---------------+
```

**Sparkline 특징:**
- 최근 6개월 월별 낙찰 건수 시각화
- 막대 그래프 형태 (width: 80px, height: 24px)
- 호버 시 상세 수치 툴팁

### 3.3 추가 분석 지표

| 지표 | 시각화 | 설명 |
|------|--------|------|
| 월별 입찰 현황 | Line Chart | 입찰/낙찰/탈락 추이 |
| 운송타입별 실적 | Doughnut | FCL/LCL/AIR/TRUCK 비율 |
| 경쟁력 분석 | Bar Chart | 내 평균 vs 시장 평균 vs 낙찰 평균 |
| 평점 추이 | Line Chart | 월별 평균 평점 변화 |

---

## 4. 시장 평균 절감률 시스템 설계

### 4.1 개요
시장 평균 요율을 집계하여 화주의 실제 계약가와 비교, 절감률을 산출합니다.

### 4.2 데이터베이스 스키마

```sql
CREATE TABLE route_market_rates (
    id              INTEGER PRIMARY KEY,
    pol             VARCHAR(50) NOT NULL,
    pod             VARCHAR(50) NOT NULL,
    shipping_type   VARCHAR(20) NOT NULL,  -- ocean, air, truck
    load_type       VARCHAR(10),           -- FCL, LCL (ocean only)
    avg_rate_krw    FLOAT NOT NULL,
    sample_count    INTEGER DEFAULT 0,
    period_start    DATE NOT NULL,
    period_end      DATE NOT NULL,
    created_at      DATETIME,
    updated_at      DATETIME
);
```

### 4.3 집계 로직

```
1. 스케줄러 실행 (월 1회 또는 주 1회)
2. 낙찰된 계약 데이터 조회 (최근 6개월)
3. 구간별/운송타입별 평균 요율 계산
4. route_market_rates 테이블 갱신
5. 최소 샘플 수 미달 시 상위 지역 평균 사용
```

### 4.4 절감률 계산 공식

```
절감률(%) = ((시장평균요율 - 실제계약가) / 시장평균요율) × 100
```

### 4.5 데이터 신뢰도 기준

| 샘플 수 | 신뢰도 |
|---------|--------|
| 10건 이상 | 높음 (정상 표시) |
| 5-9건 | 보통 (참고값 표시) |
| 5건 미만 | 낮음 (N/A 또는 상위 지역 평균) |

---

## 5. API 설계

### 5.1 화주 대시보드 API

| Endpoint | Method | 설명 |
|----------|--------|------|
| `/api/dashboard/shipper/summary` | GET | KPI 요약 데이터 |
| `/api/dashboard/shipper/volume-trend` | GET | 물량 추이 (월별) |
| `/api/dashboard/shipper/saving-rate` | GET | 시장 대비 절감률 |
| `/api/dashboard/shipper/top-export` | GET | 주요 수출국 TOP N |
| `/api/dashboard/shipper/top-import` | GET | 주요 수입국 TOP N |
| `/api/dashboard/shipper/container-efficiency` | GET | 컨테이너 적재 효율 |
| `/api/analytics/shipper/cost-by-type` | GET | 운송타입별 비용 (기존) |
| `/api/analytics/shipper/route-stats` | GET | 구간별 통계 (기존) |

### 5.2 포워더 대시보드 API

| Endpoint | Method | 설명 |
|----------|--------|------|
| `/api/dashboard/forwarder/summary` | GET | KPI 요약 데이터 |
| `/api/dashboard/forwarder/route-stats` | GET | 구간별 낙찰 현황 + Sparkline |
| `/api/analytics/forwarder/competitiveness` | GET | 경쟁력 분석 (기존) |
| `/api/analytics/forwarder/rating-trend` | GET | 평점 추이 (기존) |

### 5.3 API 응답 형식 (예시)

```json
// GET /api/dashboard/shipper/saving-rate
{
  "success": true,
  "data": {
    "saving_rate_percent": 8.5,
    "total_saved_krw": 12500000,
    "comparison_count": 15,
    "reliability": "high"
  }
}

// GET /api/dashboard/forwarder/route-stats
{
  "success": true,
  "data": [
    {
      "route": "부산 → LA",
      "bids": 15,
      "awards": 8,
      "award_rate": 53.3,
      "total_revenue_krw": 120000000,
      "sparkline": [3, 5, 2, 4, 6, 3]
    }
  ]
}
```

---

## 6. 프론트엔드 구조

### 6.1 파일 구조

```
frontend/
├── pages/
│   ├── dashboard-shipper.html   (신규)
│   └── dashboard-forwarder.html (신규)
├── js/features/
│   └── dashboard.js             (신규)
└── css/sections/
    └── dashboard.css            (신규)
```

### 6.2 기존 코드 재사용

- `analytics-shipper.html` 기반 확장
- `analytics.js` 모듈 상속
- `analytics.css` 스타일 확장

### 6.3 함수 네이밍 컨벤션

```javascript
// 초기화
initDashboard()

// 데이터 로드
fetchDashboardData()
loadVolumeTrend()
loadSavingRate()

// 차트 렌더링
updateVolumeChart()
renderSparkline(data)

// 툴팁
showVolumeTooltip(event, dataPoint)
hideVolumeTooltip()
```

---

## 7. UI/UX 표준

### 7.1 디자인 시스템 (CSS 변수)

```css
--bg-color: #0b0b0d;
--card-bg: #141416;
--text-main: #ffffff;
--text-sub: #949494;
--accent-color: #3b82f6;
--border-color: rgba(255, 255, 255, 0.08);
```

### 7.2 반응형 브레이크포인트

| 화면 | KPI 그리드 | 차트 레이아웃 |
|------|-----------|-------------|
| Desktop (1024px+) | 4컬럼 | 2:1 비율 |
| Tablet (768-1024px) | 2컬럼 | 1컬럼 |
| Mobile (768px-) | 1컬럼 | 1컬럼 |

### 7.3 차트 표준 (Chart.js 사용)

- 기존 `analytics.js`와 동일한 Chart.js 라이브러리 사용
- 색상 팔레트: `#6366f1`, `#8b5cf6`, `#10b981`, `#f59e0b`
- 툴팁 스타일: 어두운 배경, 흰색 텍스트

---

## 8. 구현 완료 항목

### Phase 1: 기본 구조 (완료)
- [x] `dashboard-shipper.html` 생성
- [x] `dashboard-forwarder.html` 생성
- [x] `dashboard.css` 스타일 시스템
- [x] `dashboard.js` 프론트엔드 모듈

### Phase 2: 화주 대시보드 (완료)
- [x] KPI Cards (총 요청, 낙찰률, 평균 입찰, 절감률)
- [x] 물량 추이 차트 (TEU/CBM/KGS 토글)
- [x] 운송타입별 비용 비중
- [x] 주요 수출국/수입국 TOP 5
- [x] 자주 이용하는 구간 TOP 10
- [x] 운송사 선정 순위
- [x] 컨테이너 적재 효율

### Phase 3: 포워더 대시보드 (완료)
- [x] KPI Cards (입찰, 낙찰률, 순위, 평점)
- [x] 월별 입찰 현황
- [x] 구간별 낙찰 현황 + Sparkline
- [x] 경쟁력 분석
- [x] 평점 추이

### Phase 4: 백엔드 API (완료)
- [x] `/api/dashboard/shipper/volume-trend`
- [x] `/api/dashboard/shipper/top-export`
- [x] `/api/dashboard/shipper/top-import`
- [x] `/api/dashboard/shipper/container-efficiency`
- [x] `/api/dashboard/forwarder/route-stats` (Sparkline 포함)

### Phase 5: 네비게이션 연동 (완료)
- [x] 주요 페이지 nav에 Dashboard 링크 추가

---

## 9. 향후 확장 계획

### 시장 평균 절감률 시스템
- [ ] `route_market_rates` 테이블 생성
- [ ] 데이터 집계 스케줄러 구현
- [ ] 절감률 계산 API 구현
- [ ] 프론트엔드 연동

### 추가 분석 기능
- [ ] 주요 운송 품목 분석 (HS Code 기반)
- [ ] 월별 비용 추이 차트
- [ ] 포워더별 성과 비교
- [ ] 데이터 내보내기 (CSV/PDF)

---

## 10. 검증 체크리스트

### 10.1 기능 검증
- [ ] API 응답 정상 확인
- [ ] 차트 렌더링 정상 확인
- [ ] 필터 (기간) 동작 확인
- [ ] 내보내기 기능 확인

### 10.2 UI/UX 검증
- [ ] 반응형 레이아웃 확인
- [ ] 색상 대비 4.5:1 이상
- [ ] 키보드 네비게이션 가능
- [ ] 로딩 상태 표시

### 10.3 성능 검증
- [ ] 페이지 로드 3초 이내
- [ ] 차트 애니메이션 60fps
- [ ] 메모리 누수 없음
