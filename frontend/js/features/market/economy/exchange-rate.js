/**
 * AAL Application - Exchange Rate Module
 * 환율 관련 기능 모듈
 * 
 * 담당 패널: #economy-panel
 * 주요 기능: 환율 차트, 통화 비교, 환율 계산기
 */

// ============================================================
// MODULE MARKER - 이 모듈이 로드되었음을 표시
// ============================================================
window.exchangeRateModuleLoaded = true;

// ============================================================
// 전역 변수 (constants.js에서 이미 정의된 것들은 재사용)
// ============================================================
// exchangeRates, activeCurrencies, chartData, previousRates는 constants.js에서 정의됨

// 차트 관련 캐시 (인라인 스크립트와 공유를 위해 window 객체 사용)
// 중복 선언 방지: 이미 선언되어 있으면 재사용
if (typeof window.tooltipCache === 'undefined') {
    window.tooltipCache = { allDates: [], perCurrency: {} };
}
if (typeof window.currentRangeKey === 'undefined') {
    window.currentRangeKey = null; // '1W' | '1M' | '3M' | '1Y' | null
}

// ============================================================
// 향후 이동할 함수들 (현재는 인라인 스크립트에서 정의됨)
// ============================================================
// 이 파일로 이동 예정:
// - initDateInputs()
// - validateDateRange()
// - setDateRange()
// - handlePeriodClick()
// - fetchExchangeRateData()
// - fetchExchangeRateStats()
// - fetchAllCurrencyRates()
// - processExchangeRateData()
// - rebuildTooltipCache()
// - findClosestDate()
// - getSvgViewBoxSize()
// - generateSVGPath()
// - inferRangeKeyFromInputs()
// - getActiveRangeKey()
// - renderYAxisLabels()
// - renderXAxisLabels()
// - updateChart()
// - toggleCurrency()
// - formatDate()
// - getDateFromMouseX()
// - showTooltip()
// - hideTooltip()
// - ensureTooltipInBody()
// - setupChartInteractivity()
// - updateCurrencyRatesTable()
// - updateChartHeader()
// - updateCalculator()
// - calculate()

console.log('📈 Exchange Rate module loaded');

