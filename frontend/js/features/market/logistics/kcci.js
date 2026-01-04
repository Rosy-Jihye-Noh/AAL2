/**
 * KCCI (Korea Container Freight Index) Visualization
 * 한국형 컨테이너선 운임지수 시각화 모듈
 * 
 * 요구사항: server/kcci/requirement.md
 */

// ============================================================
// MODULE MARKER
// ============================================================
window.kcciModuleLoaded = true;

/**
 * 툴팁을 body로 이동 (Portal 패턴 - exchange rate 스타일)
 */
function ensureKCCITooltipInBody() {
    const tooltip = document.getElementById('kcci-chart-tooltip');
    if (!tooltip) return;
    if (tooltip.parentElement !== document.body) {
        document.body.appendChild(tooltip);
    }
}

// ============================================================
// GLOBAL STATE
// ============================================================
const kcciState = {
    comprehensiveData: [],
    routeData: [],
    chartData: {
        comprehensive: { labels: [], values: [] },
        routes: {}
    },
    activePeriod: '6M', // 1W, 1M, 6M, 1Y, MAX
    activeRoutes: [], // 기본값: 빈 배열 (종합지수만 표시)
    currentWeekDate: null,
    hoveredDateIndex: null, // 현재 hover된 데이터 포인트 인덱스
    startValue: null, // 기간 시작 값 (상대 변화율 계산용)
    periodData: [] // 현재 선택된 기간의 데이터
};

// 항로 정보 매핑 (색상 포함)
const KCCI_ROUTES = {
    'KUWI': { name: 'USWC', group: 'Mainlane', weight: 15.0, color: '#3B82F6' },
    'KUEI': { name: 'USEC', group: 'Mainlane', weight: 10.0, color: '#10B981' },
    'KNEI': { name: 'Europe', group: 'Mainlane', weight: 10.0, color: '#8B5CF6' },
    'KMDI': { name: 'Mediterranean', group: 'Mainlane', weight: 5.0, color: '#F59E0B' },
    'KMEI': { name: 'Middle East', group: 'Non-Mainlane', weight: 5.0, color: '#EF4444' },
    'KAUI': { name: 'Australia', group: 'Non-Mainlane', weight: 5.0, color: '#06B6D4' },
    'KLEI': { name: 'Latin America East Coast', group: 'Non-Mainlane', weight: 5.0, color: '#EC4899' },
    'KLWI': { name: 'Latin America West Coast', group: 'Non-Mainlane', weight: 5.0, color: '#84CC16' },
    'KSAI': { name: 'South Africa', group: 'Non-Mainlane', weight: 2.5, color: '#F97316' },
    'KWAI': { name: 'West Africa', group: 'Non-Mainlane', weight: 2.5, color: '#6366F1' },
    'KCI': { name: 'China', group: 'Intra Asia', weight: 15.0, color: '#14B8A6' },
    'KJI': { name: 'Japan', group: 'Intra Asia', weight: 10.0, color: '#A855F7' },
    'KSEI': { name: 'South East Asia', group: 'Intra Asia', weight: 10.0, color: '#22C55E' }
};

// ============================================================
// API FUNCTIONS
// ============================================================

/**
 * KCCI 종합지수 데이터 가져오기
 */
async function fetchKCCIComprehensive() {
    try {
        const response = await fetch('/api/kcci/comprehensive?limit=500');
        const data = await response.json();
        
        if (data.success && data.data) {
            kcciState.comprehensiveData = data.data;
            return data.data;
        }
        return [];
    } catch (error) {
        console.error('Error fetching KCCI comprehensive:', error);
        return [];
    }
}

/**
 * 최신 항로별 지수 데이터 가져오기
 */
async function fetchKCCIRoutesLatest() {
    try {
        const response = await fetch('/api/kcci/routes/latest');
        const data = await response.json();
        
        if (data.success && data.data) {
            kcciState.routeData = data.data;
            kcciState.currentWeekDate = data.week_date;
            return data.data;
        }
        return [];
    } catch (error) {
        console.error('Error fetching KCCI routes:', error);
        return [];
    }
}

/**
 * 차트 데이터 가져오기
 */
async function fetchKCCIChartData(period = '6M', routeCodes = []) {
    try {
        // 기간 변환: 1W -> 3M, 1M -> 3M, 6M -> 6M, 1Y -> 1Y, MAX -> ALL
        let apiPeriod = '6M';
        if (period === '1W' || period === '1M') {
            apiPeriod = '3M'; // 1W, 1M은 3M 데이터로 가져오고 필터링
        } else if (period === '6M') {
            apiPeriod = '6M';
        } else if (period === '1Y') {
            apiPeriod = '1Y';
        } else if (period === 'MAX') {
            apiPeriod = 'ALL';
        }
        
        const includeRoutes = routeCodes.length > 0;
        const routeCodesParam = routeCodes.join(',');
        const url = `/api/kcci/chart-data?period=${apiPeriod}&include_routes=${includeRoutes}&route_codes=${routeCodesParam}`;
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.success) {
            let comprehensive = {
                labels: data.comprehensive.labels || [],
                values: data.comprehensive.values || []
            };
            
            // 기간 필터링
            if (period === '1W') {
                comprehensive = filterDataByDays(comprehensive, 7);
            } else if (period === '1M') {
                comprehensive = filterDataByDays(comprehensive, 31);
            }
            
            kcciState.chartData.comprehensive = comprehensive;
            kcciState.periodData = comprehensive.values; // 기간 데이터 저장
            
            if (data.routes) {
                kcciState.chartData.routes = {};
                data.routes.forEach(route => {
                    let routeData = {
                        labels: route.labels || [],
                        values: route.values || []
                    };
                    
                    // 기간 필터링
                    if (period === '1W') {
                        routeData = filterDataByDays(routeData, 7);
                    } else if (period === '1M') {
                        routeData = filterDataByDays(routeData, 31);
                    }
                    
                    kcciState.chartData.routes[route.route_code] = routeData;
                });
            }
            
            return {
                comprehensive: kcciState.chartData.comprehensive,
                routes: kcciState.chartData.routes
            };
        }
        return null;
    } catch (error) {
        console.error('Error fetching KCCI chart data:', error);
        return null;
    }
}

/**
 * 데이터를 일수로 필터링
 */
function filterDataByDays(data, days) {
    if (!data.labels || data.labels.length === 0) return data;
    
    const endDate = new Date(data.labels[data.labels.length - 1]);
    const startDate = new Date(endDate);
    startDate.setDate(startDate.getDate() - days);
    
    const filtered = {
        labels: [],
        values: []
    };
    
    data.labels.forEach((label, index) => {
        const labelDate = new Date(label);
        if (labelDate >= startDate) {
            filtered.labels.push(label);
            filtered.values.push(data.values[index]);
        }
    });
    
    return filtered;
}

// ============================================================
// UI UPDATE FUNCTIONS
// ============================================================

/**
 * 메인 인덱스 카드 업데이트 (기간 시작값 대비 증감 표시)
 */
function updateKCCIHeader(comprehensiveData, periodData) {
    if (!comprehensiveData || comprehensiveData.length === 0) {
        document.getElementById('kcci-chart-main-value').textContent = '-';
        document.getElementById('kcci-change-value').textContent = '0';
        document.getElementById('kcci-change-percent').textContent = '(0%)';
        document.getElementById('kcci-last-update').textContent = 'As of: -';
        return;
    }
    
    const latest = comprehensiveData[comprehensiveData.length - 1];
    const currentIndex = latest.current_index;
    
    // 기간 시작값 대비 증감 계산
    let change = 0;
    let changeRate = 0;
    
    if (periodData && periodData.length > 0) {
        const startValue = periodData[0];
        const endValue = periodData[periodData.length - 1];
        change = endValue - startValue;
        changeRate = startValue !== 0 ? ((endValue - startValue) / startValue) * 100 : 0;
    } else {
        // 기간 데이터가 없으면 전주 대비 사용
        change = latest.weekly_change || 0;
        changeRate = latest.weekly_change_rate || 0;
    }
    
    // 메인 값
    document.getElementById('kcci-chart-main-value').textContent = currentIndex.toLocaleString();
    
    // 변화량 배지
    const changeBadge = document.getElementById('kcci-change-badge');
    const changeValue = document.getElementById('kcci-change-value');
    const changePercent = document.getElementById('kcci-change-percent');
    
    changeValue.textContent = change > 0 ? `+${change.toFixed(0)}` : change.toFixed(0);
    changePercent.textContent = `(${changeRate > 0 ? '+' : ''}${changeRate.toFixed(2)}%)`;
    
    // 아이콘 및 색상
    const icon = changeBadge.querySelector('i');
    if (change > 0) {
        icon.className = 'fas fa-arrow-up';
        changeBadge.className = 'kcci-change-badge positive';
    } else if (change < 0) {
        icon.className = 'fas fa-arrow-down';
        changeBadge.className = 'kcci-change-badge negative';
    } else {
        icon.className = 'fas fa-minus';
        changeBadge.className = 'kcci-change-badge neutral';
    }
    
    // 기준일
    if (latest.week_date) {
        const date = new Date(latest.week_date);
        const dateStr = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
        document.getElementById('kcci-last-update').textContent = `As of: ${dateStr}`;
    }
}

/**
 * 통계 카드 업데이트 (선택된 기간 기준)
 */
function updateKCCIStats(periodData) {
    const highEl = document.getElementById('kcci-stat-high');
    const lowEl = document.getElementById('kcci-stat-low');
    const avgEl = document.getElementById('kcci-stat-average');
    
    if (!periodData || periodData.length === 0) {
        if (highEl) highEl.textContent = '-';
        if (lowEl) lowEl.textContent = '-';
        if (avgEl) avgEl.textContent = '-';
        return;
    }
    
    const values = periodData.filter(v => v != null);
    
    if (values.length > 0) {
        const high = Math.max(...values);
        const low = Math.min(...values);
        const average = values.reduce((a, b) => a + b, 0) / values.length;
        
        if (highEl) highEl.textContent = high.toLocaleString();
        if (lowEl) lowEl.textContent = low.toLocaleString();
        if (avgEl) avgEl.textContent = average.toLocaleString(undefined, { maximumFractionDigits: 0 });
    }
}

/**
 * 항로 색상 반환
 */
function getRouteColor(routeCode) {
    return KCCI_ROUTES[routeCode]?.color || '#6B7280';
}

/**
 * 항로별 테이블 렌더링 (활성화 시 그래프 색상 표시)
 */
function renderKCCIRouteTable(routeData) {
    const tbody = document.getElementById('kcci-routes-tbody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (!routeData || routeData.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="7" style="text-align: center; padding: 2rem;">No data available.</td>';
        tbody.appendChild(row);
        return;
    }
    
    // 그룹별로 정렬
    const grouped = {};
    routeData.forEach(route => {
        const group = route.route_group || 'Unknown';
        if (!grouped[group]) {
            grouped[group] = [];
        }
        grouped[group].push(route);
    });
    
    const groupOrder = ['Mainlane', 'Non-Mainlane', 'Intra Asia'];
    
    groupOrder.forEach(groupName => {
        if (!grouped[groupName]) return;
        
        // 그룹 헤더
        const headerRow = document.createElement('tr');
        headerRow.className = 'kcci-route-group-header';
        headerRow.innerHTML = `<td colspan="7">${groupName}</td>`;
        tbody.appendChild(headerRow);
        
        // 그룹 내 항로들
        grouped[groupName].forEach(route => {
            const row = document.createElement('tr');
            row.className = 'kcci-route-table-row';
            row.style.cursor = 'pointer';
            row.dataset.routeCode = route.route_code;
            
            // 실제 값 사용 (API에서 올바르게 파싱된 값)
            const currentIndex = route.current_index;
            const previousIndex = route.previous_index;
            const weeklyChange = route.weekly_change || 0;
            const weeklyChangeRate = route.weekly_change_rate || 0;
            const weight = route.weight;
            const routeColor = getRouteColor(route.route_code);
            
            // + 초록색, - 빨간색
            const isPositive = weeklyChange > 0;
            const isNegative = weeklyChange < 0;
            const changeClass = isPositive ? 'positive' : (isNegative ? 'negative' : 'neutral');
            
            // 항로가 활성화되어 있는지 확인
            const isActive = kcciState.activeRoutes.includes(route.route_code);
            if (isActive) {
                row.classList.add('active-route');
                row.style.borderLeftColor = routeColor;
                row.style.backgroundColor = `${routeColor}15`; // 15% 투명도
            }
            
            row.innerHTML = `
                <td>${route.route_group || '-'}</td>
                <td>
                    <span class="route-code-badge" style="background: ${routeColor}20; color: ${routeColor}; border: 1px solid ${routeColor}40;">
                        ${route.route_code}
                    </span>
                </td>
                <td>${route.route_name || '-'}</td>
                <td>${weight ? weight + '%' : '-'}</td>
                <td>${currentIndex != null ? currentIndex.toLocaleString() : '-'}</td>
                <td>${previousIndex != null ? previousIndex.toLocaleString() : '-'}</td>
                <td class="${changeClass}">
                    ${isPositive ? '+' : ''}${weeklyChange.toLocaleString()} 
                    (${isPositive ? '+' : ''}${weeklyChangeRate.toFixed(2)}%)
                </td>
            `;
            
            // 행 클릭 이벤트: 항로 그래프 토글
            row.addEventListener('click', () => {
                toggleRouteSelection(route.route_code);
            });
            
            tbody.appendChild(row);
        });
    });
}

/**
 * 항로 선택 토글
 */
function toggleRouteSelection(routeCode) {
    const index = kcciState.activeRoutes.indexOf(routeCode);
    const routeColor = getRouteColor(routeCode);
    
    if (index > -1) {
        kcciState.activeRoutes.splice(index, 1);
    } else {
        kcciState.activeRoutes.push(routeCode);
    }
    
    // 테이블 행 업데이트
    const row = document.querySelector(`.kcci-route-table-row[data-route-code="${routeCode}"]`);
    if (row) {
        if (kcciState.activeRoutes.includes(routeCode)) {
            row.classList.add('active-route');
            row.style.borderLeftColor = routeColor;
            row.style.backgroundColor = `${routeColor}15`;
        } else {
            row.classList.remove('active-route');
            row.style.borderLeftColor = '';
            row.style.backgroundColor = '';
        }
    }
    
    // 칩 업데이트
    const chip = document.querySelector(`.kcci-route-chip[data-route-code="${routeCode}"]`);
    if (chip) {
        if (kcciState.activeRoutes.includes(routeCode)) {
            chip.classList.add('active');
            chip.style.backgroundColor = routeColor;
            chip.style.borderColor = routeColor;
            chip.style.color = '#FFFFFF';
        } else {
            chip.classList.remove('active');
            chip.style.backgroundColor = '';
            chip.style.borderColor = '';
            chip.style.color = '';
        }
    }
    
    updateKCCIChart();
}

/**
 * 항로 필터 칩 초기화
 */
function initKCCIRouteChips(routeData) {
    const chipsContainer = document.getElementById('kcci-route-chips');
    if (!chipsContainer) return;
    
    chipsContainer.innerHTML = '';
    
    if (!routeData || routeData.length === 0) return;
    
    // 그룹별로 정렬
    const grouped = {};
    routeData.forEach(route => {
        const group = route.route_group || 'Unknown';
        if (!grouped[group]) {
            grouped[group] = [];
        }
        grouped[group].push(route);
    });
    
    const groupOrder = ['Mainlane', 'Non-Mainlane', 'Intra Asia'];
    
    groupOrder.forEach(groupName => {
        if (!grouped[groupName]) return;
        
        grouped[groupName].forEach(route => {
            const chip = document.createElement('button');
            chip.className = 'kcci-route-chip';
            chip.dataset.routeCode = route.route_code;
            
            const routeColor = getRouteColor(route.route_code);
            
            // 색상 표시 도트 추가
            chip.innerHTML = `
                <span class="chip-color-dot" style="background: ${routeColor};"></span>
                ${route.route_code}
            `;
            
            chip.addEventListener('click', () => {
                toggleRouteSelection(route.route_code);
            });
            
            chipsContainer.appendChild(chip);
        });
    });
}

// ============================================================
// CHART FUNCTIONS
// ============================================================

/**
 * X축 레이블 최적화 (기간에 따라)
 */
function getOptimalXLabels(labels, period) {
    const days = getPeriodDays(period);
    const result = [];
    
    if (labels.length === 0) return result;
    
    if (days <= 31) {
        // 1W, 1M: 모든 데이터 포인트 표시 (최대 10개)
        const step = Math.max(1, Math.ceil(labels.length / 10));
        for (let i = 0; i < labels.length; i += step) {
            result.push({ index: i, label: formatDateLabel(labels[i], period) });
        }
        // 마지막 포인트 추가
        if (result.length > 0 && result[result.length - 1].index !== labels.length - 1) {
            result.push({ index: labels.length - 1, label: formatDateLabel(labels[labels.length - 1], period) });
        }
    } else if (days <= 365) {
        // 6M, 1Y: 월별로 그룹화하여 각 월의 첫 데이터 포인트만 표시
        const monthMap = new Map();
        labels.forEach((label, index) => {
            const date = new Date(label);
            const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
            if (!monthMap.has(monthKey)) {
                monthMap.set(monthKey, { index, label: monthKey });
            }
        });
        monthMap.forEach(value => result.push(value));
    } else {
        // MAX: 연도별 또는 분기별
        const yearMap = new Map();
        labels.forEach((label, index) => {
            const date = new Date(label);
            const year = date.getFullYear();
            const quarter = Math.floor(date.getMonth() / 3) + 1;
            const key = labels.length > 100 ? `${year}` : `${year}Q${quarter}`;
            if (!yearMap.has(key)) {
                yearMap.set(key, { index, label: key });
            }
        });
        yearMap.forEach(value => result.push(value));
    }
    
    return result;
}

/**
 * 날짜 형식 변환 (요구사항에 따른 X축 표시)
 */
function formatDateLabel(dateStr, period) {
    const date = new Date(dateStr);
    const days = getPeriodDays(period);
    
    if (days <= 31) {
        // 1W, 1M: MM-DD
        return `${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
    } else if (days <= 365) {
        // 6M, 1Y: YYYY-MM
        return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
    } else {
        // 1Y 초과: YYYY
        return `${date.getFullYear()}`;
    }
}

/**
 * 기간 일수 계산
 */
function getPeriodDays(period) {
    switch (period) {
        case '1W': return 7;
        case '1M': return 31;
        case '6M': return 180;
        case '1Y': return 365;
        case 'MAX': return 10000; // 충분히 큰 값
        default: return 180;
    }
}

/**
 * 상대 변화율 계산 (기간 시작 대비)
 */
function calculateChangeRate(currentValue, startValue) {
    if (!startValue || startValue === 0) return 0;
    return ((currentValue - startValue) / startValue) * 100;
}

/**
 * KCCI 차트 업데이트
 */
async function updateKCCIChart() {
    const period = kcciState.activePeriod;
    const routeCodes = kcciState.activeRoutes;
    
    const chartData = await fetchKCCIChartData(period, routeCodes);
    
    if (!chartData) {
        console.error('Failed to fetch chart data');
        return;
    }
    
    // 기간 데이터로 통계 및 헤더 업데이트
    const periodValues = chartData.comprehensive.values;
    kcciState.periodData = periodValues;
    updateKCCIStats(periodValues);
    updateKCCIHeader(kcciState.comprehensiveData, periodValues);
    
    const svg = document.getElementById('kcci-chart-svg');
    if (!svg) return;
    
    const comprehensive = chartData.comprehensive;
    
    if (!comprehensive || !comprehensive.values || comprehensive.values.length === 0) {
        const pathsGroup = document.getElementById('kcci-paths-group');
        if (pathsGroup) {
            pathsGroup.innerHTML = `
                <text x="600" y="200" text-anchor="middle" fill="#FFFFFF" font-size="16">
                    No data available.
                </text>
            `;
        }
        return;
    }
    
    const width = 1200;
    const height = 400;
    const padding = { top: 40, right: 40, bottom: 60, left: 80 };
    const chartWidth = width - padding.left - padding.right;
    const chartHeight = height - padding.top - padding.bottom;
    
    const values = comprehensive.values;
    const labels = comprehensive.labels;
    
    if (values.length === 0) return;
    
    // 기간 시작 값 저장 (상대 변화율 계산용)
    kcciState.startValue = values[0];
    
    // 복수 지수 선택 시: 상대 변화율(%)로 변환
    const useRelativeChange = routeCodes.length > 0;
    let displayValues = values;
    let routeDisplayValues = {};
    
    if (useRelativeChange) {
        // 종합지수 상대 변화율
        displayValues = values.map(v => calculateChangeRate(v, kcciState.startValue));
        
        // 항로별 상대 변화율
        if (chartData.routes) {
            routeCodes.forEach(routeCode => {
                const route = chartData.routes[routeCode];
                if (route && route.values && route.values.length > 0) {
                    const routeStartValue = route.values[0];
                    routeDisplayValues[routeCode] = route.values.map(v => 
                        calculateChangeRate(v, routeStartValue)
                    );
                }
            });
        }
    }
    
    // 모든 값 수집 (스케일 계산용)
    let allValues = [...displayValues];
    if (useRelativeChange && Object.keys(routeDisplayValues).length > 0) {
        Object.values(routeDisplayValues).forEach(routeVals => {
            allValues = allValues.concat(routeVals);
        });
    } else if (!useRelativeChange && chartData.routes) {
        routeCodes.forEach(routeCode => {
            const route = chartData.routes[routeCode];
            if (route && route.values && route.values.length > 0) {
                allValues = allValues.concat(route.values);
            }
        });
    }
    
    const minValue = Math.min(...allValues);
    const maxValue = Math.max(...allValues);
    const valueRange = maxValue - minValue || 1;
    
    // Y축 스케일
    const yScale = (value) => {
        return padding.top + chartHeight - ((value - minValue) / valueRange) * chartHeight;
    };
    
    // X축 스케일
    const xScale = (index) => {
        return padding.left + (index / (values.length - 1 || 1)) * chartWidth;
    };
    
    // SVG 그룹 초기화
    const pathsGroup = document.getElementById('kcci-paths-group');
    const dataPointsGroup = document.getElementById('kcci-data-points');
    let crosshairGroup = document.getElementById('kcci-crosshair-group');
    
    if (!crosshairGroup) {
        crosshairGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        crosshairGroup.id = 'kcci-crosshair-group';
        svg.appendChild(crosshairGroup);
    }
    
    if (!pathsGroup || !dataPointsGroup) return;
    
    pathsGroup.innerHTML = '';
    dataPointsGroup.innerHTML = '';
    crosshairGroup.innerHTML = '';
    
    // 종합지수 경로
    let pathData = '';
    displayValues.forEach((value, index) => {
        const x = xScale(index);
        const y = yScale(value);
        if (index === 0) {
            pathData += `M ${x} ${y} `;
        } else {
            pathData += `L ${x} ${y} `;
        }
    });
    
    const comprehensivePath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    comprehensivePath.setAttribute('d', pathData);
    comprehensivePath.setAttribute('stroke', '#3B82F6');
    comprehensivePath.setAttribute('stroke-width', '3');
    comprehensivePath.setAttribute('fill', 'none');
    comprehensivePath.setAttribute('class', 'kcci-comprehensive-line');
    comprehensivePath.setAttribute('stroke-linecap', 'round');
    comprehensivePath.setAttribute('stroke-linejoin', 'round');
    pathsGroup.appendChild(comprehensivePath);
    
    // 항로별 라인 추가
    if (routeCodes.length > 0 && chartData.routes) {
        routeCodes.forEach(routeCode => {
            const route = chartData.routes[routeCode];
            if (!route || !route.values || route.values.length === 0) return;
            
            const routeDataMap = new Map();
            route.labels.forEach((date, idx) => {
                routeDataMap.set(date, route.values[idx]);
            });
            
            let routePathData = '';
            let routeStartValue = route.values[0];
            labels.forEach((date, index) => {
                const value = routeDataMap.get(date);
                if (value != null) {
                    const displayValue = useRelativeChange ? 
                        calculateChangeRate(value, routeStartValue) : 
                        value;
                    const x = xScale(index);
                    const y = yScale(displayValue);
                    if (routePathData === '') {
                        routePathData += `M ${x} ${y} `;
                    } else {
                        routePathData += `L ${x} ${y} `;
                    }
                }
            });
            
            if (routePathData) {
                const routePath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                routePath.setAttribute('d', routePathData);
                routePath.setAttribute('stroke', getRouteColor(routeCode));
                routePath.setAttribute('stroke-width', '2.5');
                routePath.setAttribute('fill', 'none');
                routePath.setAttribute('class', 'kcci-route-line');
                routePath.setAttribute('opacity', '0.9');
                routePath.dataset.routeCode = routeCode;
                pathsGroup.appendChild(routePath);
            }
        });
    }
    
    // 데이터 포인트 (기본 숨김, hover 시 표시)
    const dataPoints = [];
    displayValues.forEach((value, index) => {
        const x = xScale(index);
        const y = yScale(value);
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', x);
        circle.setAttribute('cy', y);
        circle.setAttribute('r', 0); // 기본 숨김
        circle.setAttribute('fill', '#3B82F6');
        circle.setAttribute('class', 'kcci-data-point');
        circle.setAttribute('opacity', '0');
        circle.setAttribute('pointer-events', 'none'); // 이벤트 무시
        circle.dataset.index = index;
        circle.dataset.value = useRelativeChange ? values[index] : value;
        circle.dataset.date = labels[index];
        circle.dataset.displayValue = value;
        dataPoints.push(circle);
        dataPointsGroup.appendChild(circle);
    });
    
    // 항로별 데이터 포인트
    if (routeCodes.length > 0 && chartData.routes) {
        routeCodes.forEach(routeCode => {
            const route = chartData.routes[routeCode];
            if (!route || !route.values || route.values.length === 0) return;
            
            const routeDataMap = new Map();
            route.labels.forEach((date, idx) => {
                routeDataMap.set(date, route.values[idx]);
            });
            
            const routeStartValue = route.values[0];
            
            labels.forEach((date, index) => {
                const value = routeDataMap.get(date);
                if (value != null) {
                    const displayValue = useRelativeChange ? 
                        calculateChangeRate(value, routeStartValue) : 
                        value;
                    const x = xScale(index);
                    const y = yScale(displayValue);
                    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                    circle.setAttribute('cx', x);
                    circle.setAttribute('cy', y);
                    circle.setAttribute('r', 0); // 기본 숨김
                    circle.setAttribute('fill', getRouteColor(routeCode));
                    circle.setAttribute('class', 'kcci-route-data-point');
                    circle.setAttribute('opacity', '0');
                    circle.setAttribute('pointer-events', 'none'); // 이벤트 무시
                    circle.dataset.index = index;
                    circle.dataset.value = value;
                    circle.dataset.date = date;
                    circle.dataset.routeCode = routeCode;
                    circle.dataset.displayValue = displayValue;
                    dataPoints.push(circle);
                    dataPointsGroup.appendChild(circle);
                }
            });
        });
    }
    
    // 투명한 인터랙션 영역 생성 (마우스 이벤트 캡처용) - 가장 마지막에 추가하여 최상위에 위치
    const interactionRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    interactionRect.setAttribute('x', padding.left);
    interactionRect.setAttribute('y', padding.top);
    interactionRect.setAttribute('width', chartWidth);
    interactionRect.setAttribute('height', chartHeight);
    interactionRect.setAttribute('fill', 'transparent');
    interactionRect.setAttribute('class', 'kcci-interaction-rect');
    interactionRect.style.cursor = 'crosshair';
    dataPointsGroup.appendChild(interactionRect);
    
    // SVG에 마우스 이벤트 추가 (마우스 위치 기준 가장 가까운 데이터 포인트)
    interactionRect.addEventListener('mousemove', (e) => {
        const svgRect = svg.getBoundingClientRect();
        const svgWidth = svgRect.width;
        
        // SVG 좌표로 변환 (viewBox 기준)
        const mouseX = ((e.clientX - svgRect.left) / svgWidth) * 1200;
        
        // 가장 가까운 데이터 인덱스 찾기
        let closestIndex = -1;
        let minDistance = Infinity;
        
        for (let i = 0; i < values.length; i++) {
            const pointX = xScale(i);
            const distance = Math.abs(mouseX - pointX);
            if (distance < minDistance) {
                minDistance = distance;
                closestIndex = i;
            }
        }
        
        if (closestIndex >= 0) {
            // 해당 인덱스의 모든 포인트 표시
            showDataPointsForIndex(closestIndex, dataPoints);
            showCrosshair(closestIndex, xScale, height, padding, crosshairGroup);
            
            // 툴팁 표시 (exchange rate 스타일 - visibility + transform 사용)
            const tooltip = document.getElementById('kcci-chart-tooltip');
            if (tooltip) {
                // 툴팁 내용 업데이트
                const dateEl = tooltip.querySelector('.chart-tooltip-date');
                const contentEl = tooltip.querySelector('#kcci-tooltip-content');
                
                if (dateEl && contentEl) {
                    const date = new Date(labels[closestIndex]);
                    dateEl.textContent = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
                    
                    // KCCI 시작값 대비 변화율 계산
                    const kcciStartValue = values[0];
                    const kcciCurrentValue = values[closestIndex];
                    const kcciChangeRate = calculateChangeRate(kcciCurrentValue, kcciStartValue);
                    const kcciChangeClass = kcciChangeRate >= 0 ? 'up' : 'down';
                    const kcciChangeSign = kcciChangeRate >= 0 ? '+' : '';
                    
                    let html = `
                        <div class="tooltip-item">
                            <span class="tooltip-color-dot" style="background: #3B82F6;"></span>
                            <span class="tooltip-label">KCCI</span>
                            <span class="tooltip-value">${kcciCurrentValue.toLocaleString()}</span>
                            <span class="tooltip-change ${kcciChangeClass}">${kcciChangeSign}${kcciChangeRate.toFixed(2)}%</span>
                        </div>
                    `;
                    
                    // 항로별 지수
                    if (routeCodes.length > 0 && chartData.routes) {
                        routeCodes.forEach(routeCode => {
                            const route = chartData.routes[routeCode];
                            if (!route || !route.values || !route.labels) return;
                            
                            const routeDataMap = new Map();
                            route.labels.forEach((d, idx) => routeDataMap.set(d, route.values[idx]));
                            
                            const routeValue = routeDataMap.get(labels[closestIndex]);
                            if (routeValue != null) {
                                // 항로 시작값 대비 변화율 계산
                                const routeStartValue = route.values[0];
                                const routeChangeRate = calculateChangeRate(routeValue, routeStartValue);
                                const routeChangeClass = routeChangeRate >= 0 ? 'up' : 'down';
                                const routeChangeSign = routeChangeRate >= 0 ? '+' : '';
                                
                                html += `
                                    <div class="tooltip-item">
                                        <span class="tooltip-color-dot" style="background: ${getRouteColor(routeCode)};"></span>
                                        <span class="tooltip-label">${routeCode}</span>
                                        <span class="tooltip-value">${routeValue.toLocaleString()}</span>
                                        <span class="tooltip-change ${routeChangeClass}">${routeChangeSign}${routeChangeRate.toFixed(2)}%</span>
                                    </div>
                                `;
                            }
                        });
                    }
                    
                    contentEl.innerHTML = html;
                    
                    // Exchange Rate 스타일: 먼저 크기 측정을 위해 visibility hidden으로 표시
                    tooltip.style.visibility = 'hidden';
                    tooltip.classList.add('visible');
                    
                    const tooltipRect = tooltip.getBoundingClientRect();
                    const viewportWidth = window.innerWidth;
                    const viewportHeight = window.innerHeight;
                    const tooltipPadding = 15;
                    
                    // 기본 위치 (마우스 오른쪽 아래)
                    let left = e.clientX + tooltipPadding;
                    let top = e.clientY + tooltipPadding;
                    
                    // 우측 경계 체크
                    if (left + tooltipRect.width > viewportWidth - tooltipPadding) {
                        left = e.clientX - tooltipRect.width - tooltipPadding;
                    }
                    if (left < tooltipPadding) left = tooltipPadding;
                    
                    // 하단 경계 체크
                    if (top + tooltipRect.height > viewportHeight - tooltipPadding) {
                        top = e.clientY - tooltipRect.height - tooltipPadding;
                    }
                    if (top < tooltipPadding) top = tooltipPadding;
                    
                    // transform으로 위치 이동 (exchange rate 스타일)
                    tooltip.style.transform = `translate3d(${left}px, ${top}px, 0)`;
                    tooltip.style.visibility = 'visible';
                }
            }
            
            kcciState.hoveredDateIndex = closestIndex;
        }
    });
    
    interactionRect.addEventListener('mouseleave', () => {
        hideDataPoints(dataPoints);
        hideCrosshair(crosshairGroup);
        // Exchange Rate 스타일: visibility hidden + remove visible class
        const tooltip = document.getElementById('kcci-chart-tooltip');
        if (tooltip) {
            tooltip.classList.remove('visible');
            tooltip.style.visibility = 'hidden';
        }
        kcciState.hoveredDateIndex = null;
    });
    
    // Y축 레이블 (하얀색)
    const yAxisLabels = document.getElementById('kcci-y-axis-labels');
    if (yAxisLabels) {
        yAxisLabels.innerHTML = '';
        const ySteps = 5;
        for (let i = 0; i <= ySteps; i++) {
            const value = minValue + (valueRange * i / ySteps);
            const y = yScale(value);
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', padding.left - 10);
            text.setAttribute('y', y + 5);
            text.setAttribute('text-anchor', 'end');
            text.setAttribute('fill', '#FFFFFF');
            text.setAttribute('font-size', '12');
            if (useRelativeChange) {
                text.textContent = `${value > 0 ? '+' : ''}${value.toFixed(1)}%`;
            } else {
                text.textContent = value.toLocaleString(undefined, { maximumFractionDigits: 0 });
            }
            yAxisLabels.appendChild(text);
        }
    }
    
    // X축 레이블 (최적화된 형식, 하얀색)
    const xAxisLabels = document.getElementById('kcci-x-axis-labels');
    if (xAxisLabels) {
        xAxisLabels.innerHTML = '';
        const optimalLabels = getOptimalXLabels(labels, period);
        
        optimalLabels.forEach(item => {
            const x = xScale(item.index);
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', x);
            text.setAttribute('y', height - padding.bottom + 20);
            text.setAttribute('text-anchor', 'middle');
            text.setAttribute('fill', '#FFFFFF');
            text.setAttribute('font-size', '11');
            text.textContent = item.label;
            xAxisLabels.appendChild(text);
        });
    }
}

/**
 * 특정 인덱스의 데이터 포인트 표시
 */
function showDataPointsForIndex(index, dataPoints) {
    dataPoints.forEach(point => {
        if (parseInt(point.dataset.index) === index) {
            point.setAttribute('r', 5);
            point.setAttribute('opacity', '1');
        } else {
            point.setAttribute('r', 0);
            point.setAttribute('opacity', '0');
        }
    });
}

/**
 * 데이터 포인트 숨기기
 */
function hideDataPoints(dataPoints) {
    dataPoints.forEach(point => {
        point.setAttribute('r', 0);
        point.setAttribute('opacity', '0');
    });
}

/**
 * Crosshair 표시
 */
function showCrosshair(index, xScale, height, padding, crosshairGroup) {
    crosshairGroup.innerHTML = '';
    const x = xScale(index);
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute('x1', x);
    line.setAttribute('y1', padding.top);
    line.setAttribute('x2', x);
    line.setAttribute('y2', height - padding.bottom);
    line.setAttribute('stroke', '#DADCE0');
    line.setAttribute('stroke-width', '1');
    line.setAttribute('stroke-dasharray', '4,4');
    line.setAttribute('class', 'kcci-crosshair');
    crosshairGroup.appendChild(line);
}

/**
 * Crosshair 숨기기
 */
function hideCrosshair(crosshairGroup) {
    crosshairGroup.innerHTML = '';
}

/**
 * Tooltip 표시 (모든 선택된 지수 포함) - Exchange Rate 스타일
 */
function showKCCITooltip(index, labels, values, chartData, routeCodes, useRelativeChange, event) {
    let tooltip = document.getElementById('kcci-chart-tooltip');
    
    // 툴팁이 없으면 생성하고 body에 추가
    if (!tooltip) {
        tooltip = document.createElement('div');
        tooltip.id = 'kcci-chart-tooltip';
        tooltip.className = 'chart-tooltip';
        tooltip.innerHTML = `
            <div class="chart-tooltip-date" id="kcci-tooltip-date"></div>
            <div id="kcci-tooltip-content"></div>
        `;
        document.body.appendChild(tooltip);
    }
    
    // 툴팁이 body에 없으면 이동
    if (tooltip.parentElement !== document.body) {
        document.body.appendChild(tooltip);
    }
    
    const dateEl = document.getElementById('kcci-tooltip-date');
    const contentEl = document.getElementById('kcci-tooltip-content');
    
    if (!dateEl || !contentEl) return;
    
    const date = new Date(labels[index]);
    const dateStr = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
    dateEl.textContent = dateStr;
    
    let html = '';
    
    // 종합지수 (항상 표시)
    const currentValue = values[index];
    const changeRate = useRelativeChange ? 
        calculateChangeRate(currentValue, kcciState.startValue) : 
        null;
    
    html += `
        <div class="tooltip-item">
            <span class="tooltip-color-dot" style="background: #3B82F6;"></span>
            <span class="tooltip-label">KCCI</span>
            <span class="tooltip-value">${currentValue.toLocaleString()}</span>
            ${changeRate !== null ? `<span class="tooltip-change ${changeRate >= 0 ? 'up' : 'down'}">${changeRate > 0 ? '+' : ''}${changeRate.toFixed(2)}%</span>` : ''}
        </div>
    `;
    
    // 항로별 지수
    if (routeCodes.length > 0 && chartData.routes) {
        routeCodes.forEach(routeCode => {
            const route = chartData.routes[routeCode];
            if (!route || !route.values || !route.labels) return;
            
            const routeDataMap = new Map();
            route.labels.forEach((date, idx) => {
                routeDataMap.set(date, route.values[idx]);
            });
            
            const routeValue = routeDataMap.get(labels[index]);
            if (routeValue == null) return;
            
            const routeStartValue = route.values[0];
            const routeChangeRate = useRelativeChange ? 
                calculateChangeRate(routeValue, routeStartValue) : 
                null;
            
            const routeColor = getRouteColor(routeCode);
            
            html += `
                <div class="tooltip-item">
                    <span class="tooltip-color-dot" style="background: ${routeColor};"></span>
                    <span class="tooltip-label">${routeCode}</span>
                    <span class="tooltip-value">${routeValue.toLocaleString()}</span>
                    ${routeChangeRate !== null ? `<span class="tooltip-change ${routeChangeRate >= 0 ? 'up' : 'down'}">${routeChangeRate > 0 ? '+' : ''}${routeChangeRate.toFixed(2)}%</span>` : ''}
                </div>
            `;
        });
    }
    
    contentEl.innerHTML = html;
    
    // Exchange Rate 스타일: visibility hidden으로 먼저 크기 측정
    tooltip.style.visibility = 'hidden';
    tooltip.classList.add('visible');
    
    const tooltipRect = tooltip.getBoundingClientRect();
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    const tooltipPadding = 15;
    
    // 기본 위치 (마우스 오른쪽 아래)
    let left = event.clientX + tooltipPadding;
    let top = event.clientY + tooltipPadding;
    
    // 우측 경계 체크
    if (left + tooltipRect.width > viewportWidth - tooltipPadding) {
        left = event.clientX - tooltipRect.width - tooltipPadding;
    }
    if (left < tooltipPadding) left = tooltipPadding;
    
    // 하단 경계 체크
    if (top + tooltipRect.height > viewportHeight - tooltipPadding) {
        top = event.clientY - tooltipRect.height - tooltipPadding;
    }
    if (top < tooltipPadding) top = tooltipPadding;
    
    // transform으로 위치 이동 (exchange rate 스타일)
    tooltip.style.transform = `translate3d(${left}px, ${top}px, 0)`;
    tooltip.style.visibility = 'visible';
}

/**
 * Tooltip 숨기기 - Exchange Rate 스타일
 */
function hideKCCITooltip() {
    const tooltip = document.getElementById('kcci-chart-tooltip');
    if (tooltip) {
        tooltip.classList.remove('visible');
        tooltip.style.visibility = 'hidden';
    }
}

// ============================================================
// PERIOD SELECTOR
// ============================================================

/**
 * 기간 선택 버튼 초기화
 */
function initKCCIPeriodSelector() {
    const periodButtons = document.querySelectorAll('.kcci-period-btn[data-period]');
    periodButtons.forEach(btn => {
        // SCFI, CCFI, BDI 버튼은 제외
        if (btn.classList.contains('scfi-period-btn') || 
            btn.classList.contains('ccfi-period-btn') || 
            btn.classList.contains('bdi-period-btn')) {
            return;
        }
        
        btn.addEventListener('click', () => {
            // 같은 그룹의 버튼만 토글
            const siblings = btn.parentElement.querySelectorAll('.kcci-period-btn');
            siblings.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            kcciState.activePeriod = btn.dataset.period;
            updateKCCIChart();
        });
    });
}

// ============================================================
// MAIN INITIALIZATION
// ============================================================

/**
 * KCCI 모듈 초기화
 */
async function initKCCI() {
    console.log('🚢 Initializing KCCI module...');
    
    if (window.kcciDataLoaded) {
        console.log('KCCI already loaded');
        return;
    }
    
    try {
        // 툴팁을 body로 이동 (Exchange Rate 스타일)
        ensureKCCITooltipInBody();
        
        // 데이터 로드
        const [comprehensiveData, routeData] = await Promise.all([
            fetchKCCIComprehensive(),
            fetchKCCIRoutesLatest()
        ]);
        
        // UI 업데이트
        renderKCCIRouteTable(routeData);
        initKCCIRouteChips(routeData);
        initKCCIPeriodSelector();
        
        // 차트 초기화 (통계와 헤더도 업데이트됨)
        await updateKCCIChart();
        
        window.kcciDataLoaded = true;
        console.log('✅ KCCI module initialized');
        
    } catch (error) {
        console.error('Error initializing KCCI:', error);
    }
}

/**
 * 수동 데이터 수집 트리거
 */
async function triggerKCCICollection() {
    const btn = document.getElementById('kcci-collect-btn');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    }
    
    try {
        const response = await fetch('/api/kcci/collect', {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            window.kcciDataLoaded = false;
            await initKCCI();
            alert('Data collection completed.');
        } else {
            alert('Data collection failed: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error triggering collection:', error);
        alert('Error during data collection.');
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-sync-alt"></i>';
        }
    }
}

// ============================================================
// GLOBAL EXPORTS
// ============================================================

window.initKCCI = initKCCI;
window.triggerKCCICollection = triggerKCCICollection;
window.updateKCCIChart = updateKCCIChart;

console.log('🚢 KCCI module loaded');
