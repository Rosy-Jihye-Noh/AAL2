# 프론트엔드 통합 계획

## 개요

GDELT 백엔드의 Phase 2/3 기능을 프론트엔드에 통합하는 계획입니다.

## 구현된 기능 요약

### Phase 2: 필터링 및 정렬
- ✅ 국가별 필터링 (`country` 파라미터)
- ✅ 카테고리별 필터링 (`category` 파라미터)
- ✅ 중요도 필터링 (`min_articles` 파라미터)
- ✅ 정렬 기능 (`sort_by`: importance, date, tone, scale)

### Phase 3: 통계 및 분석
- ✅ 국가별 통계 API (`/api/global-alerts/stats/by-country`)
- ✅ 카테고리별 통계 API (`/api/global-alerts/stats/by-category`)
- ✅ 트렌드 분석 API (`/api/global-alerts/trends`)
- ✅ 캐싱 메커니즘 (자동, 5분 TTL)

### 추가된 데이터 필드
- `actor1_country`, `actor2_country`: 행위자 국가 정보
- `category`: 이벤트 카테고리
- `event_code`: CAMEO 이벤트 코드
- `location`: 위치 이름 (전체 주소)
- `country_code`: 국가 코드
- `avg_tone`: 평균 톤 값
- `num_articles`, `num_mentions`, `num_sources`: 중요도 지표
- `quad_class`: QuadClass 분류

## 프론트엔드 통합 단계

### Step 1: 기본 API 호출 업데이트

#### 1.1 필터링 UI 추가

**위치**: 지도/알림 목록 상단에 필터 패널 추가

**구현 요소**:
```javascript
// 필터 상태 관리
const [filters, setFilters] = useState({
  country: '',
  category: '',
  minArticles: null,
  sortBy: 'date'
});

// API 호출 업데이트
const fetchAlerts = async () => {
  const params = new URLSearchParams({
    threshold: '-5.0',
    max_alerts: '100',
    ...(filters.country && { country: filters.country }),
    ...(filters.category && { category: filters.category }),
    ...(filters.minArticles && { min_articles: filters.minArticles }),
    sort_by: filters.sortBy
  });
  
  const response = await fetch(`/api/global-alerts?${params}`);
  const data = await response.json();
  // ...
};
```

**UI 컴포넌트**:
- 국가 선택 드롭다운 (국가 코드 목록)
- 카테고리 선택 드롭다운 (Material Conflict, Verbal Conflict 등)
- 최소 기사 수 슬라이더
- 정렬 옵션 라디오 버튼

#### 1.2 정렬 UI 추가

**위치**: 필터 패널 내 또는 별도 정렬 버튼

**옵션**:
- 중요도 순 (기본값: num_articles + num_mentions)
- 날짜 순 (최신순)
- 톤 순 (부정적 톤 우선)
- 위험도 순 (Goldstein Scale 낮은 순)

### Step 2: 통계 대시보드 추가

#### 2.1 국가별 통계 차트

**API**: `GET /api/global-alerts/stats/by-country`

**표시 내용**:
- 국가별 이벤트 수 (막대 그래프)
- 국가별 평균 Goldstein Scale (히트맵)
- 국가별 카테고리 분포 (파이 차트)

**구현 예시**:
```javascript
const fetchCountryStats = async () => {
  const response = await fetch('/api/global-alerts/stats/by-country');
  const data = await response.json();
  
  // 차트 데이터 준비
  const chartData = Object.entries(data.stats).map(([country, stats]) => ({
    country,
    count: stats.count,
    avgGoldstein: stats.avg_goldstein,
    avgTone: stats.avg_tone
  }));
  
  // Chart.js 또는 D3.js로 렌더링
};
```

#### 2.2 카테고리별 통계 차트

**API**: `GET /api/global-alerts/stats/by-category`

**표시 내용**:
- 카테고리별 이벤트 수 (파이 차트)
- 카테고리별 평균 톤 (막대 그래프)
- 카테고리별 국가 분포

### Step 3: 트렌드 분석 추가

#### 3.1 시간대별 트렌드 차트

**API**: `GET /api/global-alerts/trends?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`

**표시 내용**:
- 일별 이벤트 수 추이 (라인 차트)
- 일별 평균 Goldstein Scale 추이
- 일별 카테고리 분포 (스택 영역 차트)

**구현 예시**:
```javascript
const fetchTrends = async (days = 7) => {
  const endDate = new Date();
  const startDate = new Date();
  startDate.setDate(endDate.getDate() - days);
  
  const params = new URLSearchParams({
    start_date: startDate.toISOString().split('T')[0],
    end_date: endDate.toISOString().split('T')[0]
  });
  
  const response = await fetch(`/api/global-alerts/trends?${params}`);
  const data = await response.json();
  
  // 라인 차트 데이터 준비
  const trendData = Object.values(data.trends).map(day => ({
    date: day.date,
    count: day.count,
    avgGoldstein: day.avg_goldstein
  }));
};
```

### Step 4: 알림 카드 개선

#### 4.1 추가 필드 표시

**기존 필드**:
- 위치 (lat/lng)
- 행위자 (actor1, actor2)
- 위험도 (goldstein_scale)

**추가할 필드**:
- 카테고리 배지 (Material Conflict, Verbal Conflict 등)
- 국가 플래그/코드
- 중요도 지표 (기사 수, 언급 수)
- 평균 톤 (색상으로 표시: 빨강=부정적, 파랑=긍정적)

**구현 예시**:
```jsx
<div className="alert-card">
  <div className="alert-header">
    <span className="category-badge">{alert.category}</span>
    <span className="country-code">{alert.country_code}</span>
  </div>
  
  <h3>{alert.name}</h3>
  <p className="location">{alert.location}</p>
  
  <div className="alert-metrics">
    <span>📰 {alert.num_articles} articles</span>
    <span>💬 {alert.num_mentions} mentions</span>
    <span className={`tone-${alert.avg_tone < 0 ? 'negative' : 'positive'}`}>
      Tone: {alert.avg_tone?.toFixed(1)}
    </span>
  </div>
  
  <div className="alert-footer">
    <span>Risk: {alert.goldstein_scale}</span>
    <a href={alert.url} target="_blank">Read more</a>
  </div>
</div>
```

### Step 5: 성능 최적화

#### 5.1 캐싱 활용

**자동 캐싱**: 백엔드에서 5분 TTL로 자동 캐싱되므로 추가 작업 불필요

**프론트엔드 캐싱** (선택사항):
```javascript
// React Query 또는 SWR 사용
import useSWR from 'swr';

const { data, error } = useSWR(
  `/api/global-alerts?${params}`,
  fetcher,
  { revalidateOnFocus: false, refreshInterval: 300000 } // 5분
);
```

#### 5.2 무한 스크롤 또는 페이지네이션

**현재**: `max_alerts` 파라미터로 제한

**개선안**: 페이지네이션 추가
```javascript
const [page, setPage] = useState(1);
const pageSize = 50;

const fetchAlerts = async () => {
  const params = new URLSearchParams({
    threshold: '-5.0',
    max_alerts: pageSize.toString(),
    offset: ((page - 1) * pageSize).toString(),
    // ... filters
  });
  // ...
};
```

## UI/UX 개선 제안

### 1. 필터 패널 디자인

```
┌─────────────────────────────────────┐
│  필터 및 정렬                        │
├─────────────────────────────────────┤
│ 국가: [US ▼]  카테고리: [전체 ▼]    │
│ 최소 기사 수: [━━━━●━━━━] 5개      │
│ 정렬: ○ 중요도  ○ 날짜  ○ 톤  ○ 위험도│
│ [필터 적용] [초기화]                │
└─────────────────────────────────────┘
```

### 2. 통계 대시보드 레이아웃

```
┌─────────────────┬─────────────────┐
│ 국가별 통계      │ 카테고리별 통계  │
│ [막대 그래프]    │ [파이 차트]      │
└─────────────────┴─────────────────┘
┌─────────────────────────────────────┐
│ 시간대별 트렌드                       │
│ [라인 차트 - 최근 7일]               │
└─────────────────────────────────────┘
```

### 3. 알림 카드 개선

```
┌─────────────────────────────────────┐
│ [Material Conflict] [US]            │
│ POLICE - UNITED STATES               │
│ 📍 Lee County, Iowa, United States   │
├─────────────────────────────────────┤
│ 📰 2 articles  💬 2 mentions         │
│ Tone: -12.5 (부정적)                 │
├─────────────────────────────────────┤
│ Risk: -5.0  [Read more →]           │
└─────────────────────────────────────┘
```

## 구현 우선순위

### Phase 1: 필수 기능 (1주)
1. ✅ 필터링 UI 추가 (국가, 카테고리)
2. ✅ 정렬 옵션 추가
3. ✅ 추가 필드 표시 (카테고리, 국가, 중요도)

### Phase 2: 통계 기능 (1주)
1. ✅ 국가별 통계 차트
2. ✅ 카테고리별 통계 차트
3. ✅ 통계 대시보드 페이지 추가

### Phase 3: 고급 기능 (1주)
1. ✅ 트렌드 분석 차트
2. ✅ 알림 카드 개선
3. ✅ 성능 최적화 (캐싱, 페이지네이션)

## API 엔드포인트 요약

### 기본 알림
```
GET /api/global-alerts
Query Parameters:
  - threshold: float (기본값: -5.0)
  - max_alerts: int (기본값: 1000)
  - start_date: string (YYYY-MM-DD, 선택)
  - end_date: string (YYYY-MM-DD, 선택)
  - country: string (국가 코드, 선택)
  - category: string (카테고리, 선택)
  - min_articles: int (최소 기사 수, 선택)
  - sort_by: string (importance|date|tone|scale, 기본값: date)
```

### 통계 API
```
GET /api/global-alerts/stats/by-country
Query Parameters:
  - threshold: float (기본값: -5.0)

GET /api/global-alerts/stats/by-category
Query Parameters:
  - threshold: float (기본값: -5.0)

GET /api/global-alerts/trends
Query Parameters:
  - start_date: string (YYYY-MM-DD, 필수)
  - end_date: string (YYYY-MM-DD, 필수)
  - threshold: float (기본값: -5.0)
```

### 캐시 관리
```
POST /api/global-alerts/cache/clear
```

## 테스트 체크리스트

- [ ] 필터링 기능 테스트 (국가, 카테고리, 중요도)
- [ ] 정렬 기능 테스트 (모든 옵션)
- [ ] 통계 API 테스트 (국가별, 카테고리별)
- [ ] 트렌드 API 테스트 (다양한 날짜 범위)
- [ ] 캐싱 동작 확인
- [ ] 에러 처리 테스트
- [ ] 성능 테스트 (대량 데이터)

## 참고 자료

- Chart.js: https://www.chartjs.org/
- D3.js: https://d3js.org/
- React Query: https://tanstack.com/query
- SWR: https://swr.vercel.app/

