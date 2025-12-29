---
description: "차트 컴포넌트 UI/UX 표준 및 개발 가이드라인"
globs: ["frontend/**/*.html"]
alwaysApply: false
---

# 차트 컴포넌트 UI/UX 표준

## 1. SVG 구조 표준

### 1.1 viewBox 및 크기
- **viewBox**: `0 0 1200 400` (모든 차트 통일)
- **preserveAspectRatio**: `none` (반응형 유지)
- **클래스**: `chart-svg`

### 1.2 Padding 값
모든 차트에서 동일한 padding 값 사용:
```javascript
const padding = { 
    top: 20, 
    bottom: 30, 
    left: 40, 
    right: 20 
};
```

### 1.3 Grid Lines
- **클래스**: `chart-grid-line`
- **스타일**: `stroke: rgba(255,255,255,0.08)`, `stroke-width: 1`, `stroke-dasharray: 2, 2`
- **위치**: Y축 라벨과 정렬 (5개 그리드 라인)
- **좌표**: 
  - `x1="0"`, `x2="1200"`
  - `y1`, `y2`: 350, 280, 210, 140, 70

### 1.4 그룹 요소 ID 네이밍
- X축 라벨: `[chart-name]-x-axis-labels`
- Y축 라벨: `[chart-name]-y-axis-labels`
- 데이터 포인트: `[chart-name]-data-points`

예시:
- `inflation-x-axis-labels`
- `interest-y-axis-labels`
- `gdp-data-points`

## 2. 차트 렌더링 함수 표준

### 2.1 함수 네이밍 컨벤션
모든 차트는 다음 함수 구조를 따라야 합니다:

```javascript
// 초기화
function init[ChartName]() { }

// 데이터 가져오기
function fetch[ChartName]Data() { }

// 데이터 처리
function process[ChartName]Data(data) { }

// 차트 업데이트 (메인 함수)
function update[ChartName]Chart() { }

// X축 라벨 렌더링
function render[ChartName]XAxisLabels() { }

// Y축 라벨 렌더링
function render[ChartName]YAxisLabels() { }

// 차트 헤더/통계 업데이트
function update[ChartName]ChartHeader(stats) { }

// SVG 경로 생성
function generate[ChartName]SVGPath(data) { }

// 데이터 포인트 렌더링
function render[ChartName]DataPoints() { }

// 툴팁 표시
function show[ChartName]Tooltip(event, dataPoint) { }

// 툴팁 숨김
function hide[ChartName]Tooltip() { }
```

### 2.2 차트 업데이트 함수 구조
`update[ChartName]Chart()` 함수는 다음 순서로 실행되어야 합니다:

1. 데이터 유효성 검사
2. Y축 범위 계산 및 렌더링 (`render[ChartName]YAxisLabels()`)
3. X축 라벨 렌더링 (`render[ChartName]XAxisLabels()`)
4. 차트 경로 생성 및 렌더링 (`generate[ChartName]SVGPath()`)
5. 데이터 포인트 렌더링 (`render[ChartName]DataPoints()`)
6. 통계 계산 및 헤더 업데이트 (`update[ChartName]ChartHeader()`)

## 3. X축 라벨 표준

### 3.1 라벨 표시 규칙

#### 연도별 (A - Annual)
- **표시 주기**: 매년 1월, 4월, 7월, 10월만 표시 (분기별)
- **라벨 형식**: 
  - 연도가 바뀔 때: `YY.MM` (예: `21.01`, `22.01`)
  - 같은 연도 내: `MM월` (예: `4월`, `7월`, `10월`)
- **예시**: `21.01`, `4월`, `7월`, `10월`, `22.01`, `4월`, `7월`, `10월`

#### 월별 (M - Monthly)
- **표시 주기**: 매 2개월마다 표시
- **라벨 형식**: 항상 `YY.MM` 형식 (예: `21.01`, `21.03`, `21.05`)
- **첫 번째와 마지막 라벨은 항상 포함**

#### 분기별 (Q - Quarterly)
- **표시 주기**: 모든 분기 표시
- **라벨 형식**: `YYYYQn` 또는 `YYYY.nQ` (예: `2024Q1`, `2024.1Q`)

### 3.2 라벨 위치 계산
```javascript
const x = padding.left + (index / (data.length - 1 || 1)) * chartWidth;
```

### 3.3 라벨 스타일
- **text-anchor**: `middle`
- **dominant-baseline**: `middle`
- **클래스**: `chart-xaxis-label`
- **Y 위치**: `height - padding.bottom + 20`

## 4. Y축 라벨 표준

### 4.1 동적 범위 계산
```javascript
const allValues = [];
// 모든 데이터 시리즈의 값 수집
Object.values(chartData).forEach(data => {
    data.forEach(item => allValues.push(item.value));
});

const minValue = Math.min(...allValues);
const maxValue = Math.max(...allValues);
const range = maxValue - minValue || 1;

// 동적 padding (값 범위에 따라 조정)
const paddingPercent = range < 10 ? 0.01 : (range < 50 ? 0.005 : 0.003);
const paddedMin = Math.max(0, minValue - range * paddingPercent);
const paddedMax = maxValue + range * paddingPercent;
```

### 4.2 라벨 개수 및 간격
- **라벨 개수**: 5-6개
- **간격**: 동일한 간격으로 분할
```javascript
const steps = 5;
for (let i = 0; i <= steps; i++) {
    const value = paddedMax - (i / steps) * (paddedMax - paddedMin);
    // ...
}
```

### 4.3 소수점 표시 규칙
- **일반**: `value.toFixed(1)` (소수점 1자리)
- **정수 값**: 필요시 `value.toFixed(0)`
- **큰 값**: 천 단위 구분자 사용 (`toLocaleString()`)

### 4.4 라벨 스타일
- **text-anchor**: `end`
- **dominant-baseline**: `middle`
- **클래스**: `chart-yaxis-label`
- **X 위치**: `padding.left - 10`

## 5. 차트 타입 표준

### 5.1 Line Chart (꺾은선 그래프)
**조건**: 데이터 포인트가 2개 이상일 때

**특징**:
- SVG `<path>` 요소 사용
- 원형 마커 필수 (`<circle>` 요소)
- 마커 반지름: 4-5px
- 마커 색상: 선 색상과 동일
- 호버 시 마커 강조 (크기 증가)

### 5.2 Bar Chart (막대 그래프)
**조건**: 데이터 포인트가 1개 또는 2개 미만일 때

**특징**:
- SVG `<rect>` 요소 사용
- 막대 너비: `Math.min(60, chartWidth * 0.3)`
- 막대 위치: 차트 중앙
- X축 라벨: 중앙 정렬

### 5.3 차트 타입 결정 로직
```javascript
if (data.length === 1) {
    // Bar Chart
} else if (data.length < 2) {
    // Bar Chart (2개 미만)
} else {
    // Line Chart (2개 이상)
}
```

## 6. 색상 시스템 표준

### 6.1 CSS 변수 사용
모든 차트 색상은 CSS 변수로 정의되어야 합니다:

```css
:root {
    /* Exchange Rates */
    --c-usd: #3b82f6;
    --c-eur: #22c55e;
    /* ... */
    
    /* Inflation */
    --c-cpi-total: #3b82f6;
    --c-cpi-fresh: #22c55e;
    --c-cpi-industrial: #f59e0b;
    
    /* GDP */
    --c-gdp-total: #3b82f6;
    --c-gdp-consumption: #22c55e;
    --c-gdp-investment: #f59e0b;
    
    /* Interest Rates */
    --c-base-rate: #3b82f6;
}
```

### 6.2 선 색상 적용
```javascript
stroke="var(--c-[item-name])"
```

### 6.3 호버 효과
- **선 두께**: 기본 `2.5px` → 호버 시 `3.5px`
- **마커 크기**: 기본 `4px` → 호버 시 `6px`
- **전환**: `transition: all 0.2s ease`

### 6.4 활성/비활성 상태
- **활성**: `opacity: 1`, 선 표시
- **비활성**: `opacity: 0.3`, 선 표시 (클릭으로 토글)

## 7. 툴팁 표준

### 7.1 위치 및 스타일
- **position**: `fixed` (viewport 기준)
- **최대 너비**: `min(340px, calc(100vw - 20px))`
- **최대 높이**: `70vh` (스크롤 가능)
- **배경**: `rgba(20, 20, 22, 0.95)`
- **테두리**: `1px solid var(--border-color)`
- **border-radius**: `8px`
- **패딩**: `12px 16px`
- **z-index**: `1000`

### 7.2 동적 위치 조정
```javascript
// 화면 경계 체크
const tooltipWidth = tooltip.offsetWidth;
const tooltipHeight = tooltip.offsetHeight;
const viewportWidth = window.innerWidth;
const viewportHeight = window.innerHeight;

// X 위치 조정
if (event.clientX + tooltipWidth + 10 > viewportWidth) {
    tooltip.style.left = (event.clientX - tooltipWidth - 10) + 'px';
} else {
    tooltip.style.left = (event.clientX + 10) + 'px';
}

// Y 위치 조정
if (event.clientY + tooltipHeight + 10 > viewportHeight) {
    tooltip.style.top = (event.clientY - tooltipHeight - 10) + 'px';
} else {
    tooltip.style.top = (event.clientY + 10) + 'px';
}
```

### 7.3 표시 형식
```html
<div class="chart-tooltip">
    <div class="chart-tooltip-date">YYYY.MM.DD</div>
    <div class="chart-tooltip-value">값 (단위)</div>
    <div class="chart-tooltip-change">변화량 (+/-)</div>
</div>
```

## 8. HTML 구조 표준

### 8.1 차트 컨테이너
```html
<div class="chart-area" id="[chart-name]-chart-container">
    <svg class="chart-svg" id="[chart-name]-chart-svg" viewBox="0 0 1200 400" preserveAspectRatio="none">
        <!-- Grid Lines -->
        <line x1="0" y1="350" x2="1200" y2="350" class="chart-grid-line" />
        <!-- ... -->
        
        <!-- Y-axis labels -->
        <g id="[chart-name]-y-axis-labels"></g>
        
        <!-- Chart paths (for line charts) -->
        <path id="path-[item-name]" class="chart-path visible" stroke="var(--c-[item-name])" d="" />
        
        <!-- Data points (for line charts with markers) -->
        <g id="[chart-name]-data-points"></g>
        
        <!-- X-axis labels -->
        <g id="[chart-name]-x-axis-labels"></g>
    </svg>
</div>

<!-- Tooltip (차트 컨테이너 외부) -->
<div class="chart-tooltip" id="[chart-name]-chart-tooltip"></div>
```

### 8.2 차트 영역 스타일
```css
.chart-area {
    height: clamp(350px, 50vh, 500px);
    background: rgba(0,0,0,0.2);
    border-radius: 12px;
    border: 1px solid var(--border-color);
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: flex-end;
    padding: 20px 0 20px 40px;
}
```

## 9. 성능 최적화 표준

### 9.1 이벤트 리스너
- **mousemove**: `requestAnimationFrame`으로 스로틀링
- **mouseleave**: 즉시 툴팁 숨김
- **이벤트 리스너 정리**: 차트 업데이트 시 기존 리스너 제거

### 9.2 DOM 조작 최소화
- `innerHTML` 대신 `textContent` 또는 `createElement` 사용
- 그룹 요소(`<g>`) 활용하여 일괄 업데이트
- `requestAnimationFrame`으로 렌더링 최적화

### 9.3 렌더링 최적화
- GPU 가속: `transform: translate3d` 사용
- 불필요한 리렌더링 방지: 데이터 변경 시에만 업데이트

## 10. 접근성 표준

### 10.1 ARIA 속성
```html
<svg role="img" aria-label="차트 설명">
    <!-- ... -->
</svg>
```

### 10.2 키보드 네비게이션
- Tab 키로 차트 컨트롤 접근 가능
- Enter/Space 키로 항목 선택/해제

### 10.3 색상 대비
- 모든 텍스트와 배경의 대비 비율: 4.5:1 이상 (WCAG 2.1 AA)

## 11. 검증 체크리스트

새로운 차트를 추가하거나 기존 차트를 수정할 때 다음 항목을 확인:

- [ ] viewBox가 `0 0 1200 400`인가?
- [ ] padding 값이 표준과 일치하는가?
- [ ] 함수 네이밍이 표준을 따르는가?
- [ ] X축 라벨 형식이 주기에 맞게 표시되는가?
- [ ] Y축 라벨이 동적 범위로 계산되는가?
- [ ] 차트 타입(Line/Bar)이 데이터 개수에 맞게 결정되는가?
- [ ] 색상이 CSS 변수로 정의되어 있는가?
- [ ] 툴팁이 화면 경계를 벗어나지 않는가?
- [ ] HTML 구조가 표준을 따르는가?
- [ ] 성능 최적화가 적용되어 있는가?
- [ ] 접근성이 고려되어 있는가?

## 참고 파일

- `.cursor/rules/uiux-rule/RULE.md` - 전체 UI/UX 규칙
- `.cursor/rules/frontend-rule/RULE.md` - 프론트엔드 개발 규칙
- `frontend/ai_studio_code_F2.html` - 메인 프론트엔드 파일

