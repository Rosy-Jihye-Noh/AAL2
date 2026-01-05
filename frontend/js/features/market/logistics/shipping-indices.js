/**
 * AAL Application - Shipping Indices Module
 * SCFI, CCFI, BDI 운임 지수 차트 모듈
 * 
 * SCFI: Shanghai Containerized Freight Index
 * CCFI: China Containerized Freight Index  
 * BDI: Baltic Dry Index
 */

// ============================================================
// CONSTANTS & STATE
// ============================================================

const SHIPPING_INDICES_API_BASE = '/api/shipping-indices';

const shippingIndicesState = {
    scfi: {
        data: null,
        activePeriod: '6M',
        loaded: false
    },
    ccfi: {
        data: null,
        activePeriod: '6M',
        loaded: false
    },
    bdi: {
        data: null,
        activePeriod: '6M',
        loaded: false
    }
};

// Index descriptions (English translation provided by user)
const INDEX_DESCRIPTIONS = {
    scfi: 'The Shanghai Containerized Freight Index (SCFI) has been published by the Shanghai Shipping Exchange (SSE) since December 7, 2005. It reflects spot freight rates for container shipping from Shanghai to 15 major destinations. Originally based on time charter rates, since October 16, 2009, it is calculated based on container freight rates in USD per TEU (20-foot equivalent unit). The index covers CY-CY shipping conditions for General Dry Cargo Containers. The freight rate for each route is the arithmetic average of all rates on that route, including surcharges related to maritime transport. Freight information is provided by panelists including liner carriers and forwarders from CCFI.',
    ccfi: 'The China Containerized Freight Index (CCFI) is compiled by the Shanghai Shipping Exchange under the supervision of China\'s Ministry of Transport. First published on April 13, 1998, it objectively reflects global container market conditions and serves as a key indicator of Chinese shipping market trends. The index uses January 1, 1998 as the base (1000). It covers 11 major routes from Chinese ports, with freight information from 16 shipping companies, published every Friday.',
    bdi: 'The Baltic Dry Index (BDI) has been used by the Baltic Exchange since November 1, 1999, replacing the BFI (Baltic Freight Index) which tracked dry cargo freight rates since 1985. Using January 4, 1985 as the base (1000), it is a composite index of time charter rates by vessel type: Baltic Capesize Index (BCI), Baltic Panamax Index (BPI), Baltic Supramax Index (BSI), and Baltic Handysize Index (BHSI). The BDI is calculated by averaging these four indices with equal weights and multiplying by the BDI factor.'
};

// Chart colors
const INDEX_COLORS = {
    scfi: '#3B82F6',  // Blue
    ccfi: '#10B981',  // Green
    bdi: '#F59E0B'    // Amber
};

// ============================================================
// API FUNCTIONS
// ============================================================

/**
 * Fetch chart data for a specific index
 */
async function fetchShippingIndexChartData(indexType, period) {
    try {
        const response = await fetch(
            `${SHIPPING_INDICES_API_BASE}/${indexType}/chart-data?period=${period}`
        );
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error(`Error fetching ${indexType.toUpperCase()} chart data:`, error);
        return null;
    }
}

// ============================================================
// CHART RENDERING
// ============================================================

/**
 * Render shipping index chart
 */
function renderShippingIndexChart(indexType, chartData) {
    const svgId = `${indexType}-chart-svg`;
    const svg = document.getElementById(svgId);
    
    if (!svg || !chartData || !chartData.data || chartData.data.length === 0) {
        console.warn(`No data available for ${indexType.toUpperCase()} chart`);
        return;
    }
    
    const pathsGroup = document.getElementById(`${indexType}-paths-group`);
    const dataPointsGroup = document.getElementById(`${indexType}-data-points`);
    const yAxisLabels = document.getElementById(`${indexType}-y-axis-labels`);
    const xAxisLabels = document.getElementById(`${indexType}-x-axis-labels`);
    
    if (!pathsGroup) return;
    
    // Chart dimensions
    const width = 1200;
    const height = 400;
    const padding = { top: 40, right: 40, bottom: 60, left: 80 };
    const chartWidth = width - padding.left - padding.right;
    const chartHeight = height - padding.top - padding.bottom;
    
    const values = chartData.values;
    const labels = chartData.labels;
    
    if (values.length === 0) return;
    
    // Calculate min/max with padding
    const minValue = Math.min(...values);
    const maxValue = Math.max(...values);
    const valuePadding = (maxValue - minValue) * 0.1 || 100;
    const yMin = Math.floor((minValue - valuePadding) / 100) * 100;
    const yMax = Math.ceil((maxValue + valuePadding) / 100) * 100;
    
    // Y-axis scale
    const yScale = (value) => {
        return padding.top + chartHeight - ((value - yMin) / (yMax - yMin)) * chartHeight;
    };
    
    // X-axis scale
    const xScale = (index) => {
        return padding.left + (index / (values.length - 1)) * chartWidth;
    };
    
    // Build path
    let pathD = '';
    const points = [];
    
    values.forEach((value, index) => {
        const x = xScale(index);
        const y = yScale(value);
        points.push({ x, y, value, label: labels[index], index });
        
        if (index === 0) {
            pathD += `M ${x} ${y}`;
        } else {
            pathD += ` L ${x} ${y}`;
        }
    });
    
    // Clear existing content
    pathsGroup.innerHTML = '';
    if (dataPointsGroup) dataPointsGroup.innerHTML = '';
    if (yAxisLabels) yAxisLabels.innerHTML = '';
    if (xAxisLabels) xAxisLabels.innerHTML = '';
    
    // Render Y-axis labels
    if (yAxisLabels) {
        const ySteps = 5;
        const yStep = (yMax - yMin) / ySteps;
        
        for (let i = 0; i <= ySteps; i++) {
            const yValue = yMin + (yStep * i);
            const y = yScale(yValue);
            
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', padding.left - 10);
            text.setAttribute('y', y + 4);
            text.setAttribute('text-anchor', 'end');
            text.setAttribute('class', 'chart-axis-label');
            text.setAttribute('fill', '#9CA3AF');
            text.setAttribute('font-size', '12');
            text.textContent = yValue.toLocaleString();
            yAxisLabels.appendChild(text);
        }
    }
    
    // Render X-axis labels (show subset based on data length)
    if (xAxisLabels && labels.length > 0) {
        const maxLabels = 8;
        const step = Math.ceil(labels.length / maxLabels);
        
        for (let i = 0; i < labels.length; i += step) {
            const x = xScale(i);
            const label = labels[i];
            
            // Format date
            const formattedDate = formatChartDate(label, shippingIndicesState[indexType].activePeriod);
            
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', x);
            text.setAttribute('y', height - padding.bottom + 25);
            text.setAttribute('text-anchor', 'middle');
            text.setAttribute('class', 'chart-axis-label');
            text.setAttribute('fill', '#9CA3AF');
            text.setAttribute('font-size', '12');
            text.textContent = formattedDate;
            xAxisLabels.appendChild(text);
        }
    }
    
    // Create gradient
    const gradientId = `${indexType}-gradient`;
    const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    const gradient = document.createElementNS('http://www.w3.org/2000/svg', 'linearGradient');
    gradient.setAttribute('id', gradientId);
    gradient.setAttribute('x1', '0%');
    gradient.setAttribute('y1', '0%');
    gradient.setAttribute('x2', '0%');
    gradient.setAttribute('y2', '100%');
    
    const color = INDEX_COLORS[indexType] || '#3B82F6';
    
    const stop1 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
    stop1.setAttribute('offset', '0%');
    stop1.setAttribute('stop-color', color);
    stop1.setAttribute('stop-opacity', '0.3');
    
    const stop2 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
    stop2.setAttribute('offset', '100%');
    stop2.setAttribute('stop-color', color);
    stop2.setAttribute('stop-opacity', '0.05');
    
    gradient.appendChild(stop1);
    gradient.appendChild(stop2);
    defs.appendChild(gradient);
    pathsGroup.appendChild(defs);
    
    // Create area fill
    const areaPath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    const areaD = pathD + ` L ${xScale(values.length - 1)} ${height - padding.bottom} L ${xScale(0)} ${height - padding.bottom} Z`;
    areaPath.setAttribute('d', areaD);
    areaPath.setAttribute('fill', `url(#${gradientId})`);
    areaPath.setAttribute('class', 'chart-area-fill');
    pathsGroup.appendChild(areaPath);
    
    // Create line path
    const linePath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    linePath.setAttribute('d', pathD);
    linePath.setAttribute('stroke', color);
    linePath.setAttribute('stroke-width', '2');
    linePath.setAttribute('fill', 'none');
    linePath.setAttribute('class', 'chart-line');
    pathsGroup.appendChild(linePath);
    
    // Create invisible rect for mouse tracking
    const hitArea = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    hitArea.setAttribute('x', padding.left);
    hitArea.setAttribute('y', padding.top);
    hitArea.setAttribute('width', chartWidth);
    hitArea.setAttribute('height', chartHeight);
    hitArea.setAttribute('fill', 'transparent');
    hitArea.setAttribute('class', 'chart-hit-area');
    pathsGroup.appendChild(hitArea);
    
    // Store points for hover
    svg.dataset.points = JSON.stringify(points);
    svg.dataset.indexType = indexType;
    svg.dataset.color = color;
    
    // Add mouse event listeners
    hitArea.addEventListener('mousemove', (e) => handleShippingChartHover(e, svg, indexType));
    hitArea.addEventListener('mouseleave', () => hideShippingChartTooltip(indexType));
}

/**
 * Format chart date based on period
 */
function formatChartDate(dateStr, period) {
    if (!dateStr) return '';
    
    const date = new Date(dateStr);
    
    if (period === '1W' || period === '1M') {
        return `${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`;
    } else if (period === '3M' || period === '6M') {
        return `${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`;
    } else if (period === '1Y') {
        return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}`;
    } else {
        // ALL
        return `${date.getFullYear()}`;
    }
}

/**
 * Handle chart hover
 */
function handleShippingChartHover(event, svg, indexType) {
    const points = JSON.parse(svg.dataset.points || '[]');
    if (points.length === 0) return;
    
    const rect = svg.getBoundingClientRect();
    const scaleX = 1200 / rect.width;
    const mouseX = (event.clientX - rect.left) * scaleX;
    
    // Find closest point
    let closestPoint = points[0];
    let closestDist = Math.abs(mouseX - points[0].x);
    
    for (const point of points) {
        const dist = Math.abs(mouseX - point.x);
        if (dist < closestDist) {
            closestDist = dist;
            closestPoint = point;
        }
    }
    
    showShippingChartTooltip(indexType, closestPoint, svg.dataset.color, event);
}

/**
 * Show tooltip
 */
function showShippingChartTooltip(indexType, point, color, event) {
    const tooltip = document.getElementById(`${indexType}-chart-tooltip`);
    if (!tooltip) return;
    
    const dateEl = document.getElementById(`${indexType}-tooltip-date`);
    const contentEl = document.getElementById(`${indexType}-tooltip-content`);
    
    if (dateEl) {
        dateEl.textContent = point.label;
    }
    
    if (contentEl) {
        contentEl.innerHTML = `
            <div style="display: flex; align-items: center; gap: 8px; margin-top: 4px;">
                <span style="width: 10px; height: 10px; background: ${color}; border-radius: 50%;"></span>
                <span style="color: #E5E7EB; font-weight: 600;">${point.value.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} pt</span>
            </div>
        `;
    }
    
    tooltip.style.display = 'block';
    tooltip.style.left = `${event.clientX + 15}px`;
    tooltip.style.top = `${event.clientY - 30}px`;
}

/**
 * Hide tooltip
 */
function hideShippingChartTooltip(indexType) {
    const tooltip = document.getElementById(`${indexType}-chart-tooltip`);
    if (tooltip) {
        tooltip.style.display = 'none';
    }
}

// ============================================================
// UI UPDATE FUNCTIONS
// ============================================================

/**
 * Update header and stats for an index
 */
function updateShippingIndexUI(indexType, chartData) {
    if (!chartData || !chartData.stats) return;
    
    const stats = chartData.stats;
    const data = chartData.data || [];
    const latest = data.length > 0 ? data[data.length - 1] : null;
    
    // Update main value
    const mainValueEl = document.getElementById(`${indexType}-chart-main-value`);
    if (mainValueEl && latest) {
        mainValueEl.textContent = latest.current_index.toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }
    
    // Update last update date
    const lastUpdateEl = document.getElementById(`${indexType}-last-update`);
    if (lastUpdateEl && latest) {
        lastUpdateEl.textContent = `기준일: ${latest.index_date}`;
    }
    
    // Update stats
    const highEl = document.getElementById(`${indexType}-stat-high`);
    if (highEl && stats.high !== undefined) {
        highEl.textContent = stats.high.toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }
    
    const lowEl = document.getElementById(`${indexType}-stat-low`);
    if (lowEl && stats.low !== undefined) {
        lowEl.textContent = stats.low.toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }
    
    const avgEl = document.getElementById(`${indexType}-stat-avg`);
    if (avgEl && stats.average !== undefined) {
        avgEl.textContent = stats.average.toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }
}

/**
 * Update chart for an index
 */
async function updateShippingIndexChart(indexType) {
    const period = shippingIndicesState[indexType].activePeriod;
    
    const chartData = await fetchShippingIndexChartData(indexType, period);
    
    if (chartData && chartData.success) {
        shippingIndicesState[indexType].data = chartData;
        updateShippingIndexUI(indexType, chartData);
        renderShippingIndexChart(indexType, chartData);
    }
}

// ============================================================
// INITIALIZATION
// ============================================================

/**
 * Initialize period buttons for an index
 */
function initShippingIndexPeriodSelector(indexType) {
    const buttons = document.querySelectorAll(`.${indexType}-period-btn`);
    
    buttons.forEach(btn => {
        btn.addEventListener('click', async (e) => {
            // Remove active from all
            buttons.forEach(b => b.classList.remove('active'));
            
            // Add active to clicked
            e.target.classList.add('active');
            
            // Update state and chart
            shippingIndicesState[indexType].activePeriod = e.target.dataset.period;
            await updateShippingIndexChart(indexType);
        });
    });
}

/**
 * Initialize SCFI module
 */
async function initSCFI() {
    console.log('📊 Initializing SCFI module...');
    
    if (shippingIndicesState.scfi.loaded) {
        console.log('SCFI already loaded');
        return;
    }
    
    try {
        initShippingIndexPeriodSelector('scfi');
        await updateShippingIndexChart('scfi');
        
        shippingIndicesState.scfi.loaded = true;
        console.log('✅ SCFI module initialized');
    } catch (error) {
        console.error('Error initializing SCFI:', error);
    }
}

/**
 * Initialize CCFI module
 */
async function initCCFI() {
    console.log('📊 Initializing CCFI module...');
    
    if (shippingIndicesState.ccfi.loaded) {
        console.log('CCFI already loaded');
        return;
    }
    
    try {
        initShippingIndexPeriodSelector('ccfi');
        await updateShippingIndexChart('ccfi');
        
        shippingIndicesState.ccfi.loaded = true;
        console.log('✅ CCFI module initialized');
    } catch (error) {
        console.error('Error initializing CCFI:', error);
    }
}

/**
 * Initialize BDI module
 */
async function initBDI() {
    console.log('📊 Initializing BDI module...');
    
    if (shippingIndicesState.bdi.loaded) {
        console.log('BDI already loaded');
        return;
    }
    
    try {
        initShippingIndexPeriodSelector('bdi');
        await updateShippingIndexChart('bdi');
        
        shippingIndicesState.bdi.loaded = true;
        console.log('✅ BDI module initialized');
    } catch (error) {
        console.error('Error initializing BDI:', error);
    }
}

// ============================================================
// GLOBAL EXPORTS
// ============================================================

window.initSCFI = initSCFI;
window.initCCFI = initCCFI;
window.initBDI = initBDI;
window.shippingIndicesState = shippingIndicesState;
window.INDEX_DESCRIPTIONS = INDEX_DESCRIPTIONS;

console.log('📦 Shipping Indices module loaded');

