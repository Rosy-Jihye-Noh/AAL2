/**
 * Dashboard Module
 * 화주/포워더용 대시보드
 */

// API Base URL
const QUOTE_API_BASE = 'http://localhost:8001';

export const Dashboard = {
    // State
    userType: 'shipper', // 'shipper' or 'forwarder'
    userEmail: null,
    userId: null,
    currentPeriod: '6m',
    charts: {},
    volumeType: 'teu', // teu, cbm, kgs
    
    // Date range
    fromDate: null,
    toDate: null,
    
    /**
     * Initialize Dashboard
     */
    init(userType = 'shipper') {
        console.log(`🚀 Dashboard init: ${userType}`);
        this.userType = userType;
        this.loadSession();
        this.setupEventListeners();
        this.calculateDateRange(this.currentPeriod);
        
        if (this.userEmail) {
            this.showDashboard();
            this.loadAllData();
        } else {
            this.showLoginRequired();
        }
    },
    
    /**
     * Load user session
     */
    loadSession() {
        // Check Auth module first
        if (window.Auth && Auth.user) {
            this.userEmail = Auth.user.email;
            this.userId = Auth.user.id;
            this.updateAuthUI(Auth.user);
            return;
        }
        
        // Fallback to localStorage
        const sessionKey = this.userType === 'shipper' ? 'shipperSession' : 'forwarderSession';
        const session = localStorage.getItem(sessionKey);
        
        if (session) {
            try {
                const data = JSON.parse(session);
                this.userEmail = data.email;
                this.userId = data.id;
                this.updateAuthUI(data);
            } catch (e) {
                console.error('Session parse error:', e);
            }
        }
        
        // Also check unified auth session
        const authSession = localStorage.getItem('authSession');
        if (authSession && !this.userEmail) {
            try {
                const data = JSON.parse(authSession);
                if (data.user_type === this.userType) {
                    this.userEmail = data.email;
                    this.userId = data.id;
                    this.updateAuthUI(data);
                }
            } catch (e) {
                console.error('Auth session parse error:', e);
            }
        }
    },
    
    /**
     * Update auth UI in header
     */
    updateAuthUI(userData) {
        const authContainer = document.getElementById('headerAuthContainer');
        if (authContainer && userData) {
            authContainer.innerHTML = `
                <div class="user-info">
                    <span class="user-name">${userData.company || userData.name || userData.email}</span>
                    <button class="header-auth-btn" onclick="Dashboard.logout()">
                        <i class="fas fa-sign-out-alt"></i>
                    </button>
                </div>
            `;
        }
    },
    
    /**
     * Logout
     */
    logout() {
        localStorage.removeItem('shipperSession');
        localStorage.removeItem('forwarderSession');
        localStorage.removeItem('authSession');
        if (window.Auth) {
            Auth.logout();
        }
        window.location.reload();
    },
    
    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Period buttons
        document.querySelectorAll('.period-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.period-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.currentPeriod = e.target.dataset.period;
                this.calculateDateRange(this.currentPeriod);
                this.loadAllData();
            });
        });
        
        // Volume type toggle (shipper only)
        const volumeToggle = document.getElementById('volumeTypeToggle');
        if (volumeToggle) {
            volumeToggle.querySelectorAll('.chart-toggle-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    volumeToggle.querySelectorAll('.chart-toggle-btn').forEach(b => b.classList.remove('active'));
                    e.target.classList.add('active');
                    this.volumeType = e.target.dataset.type;
                    this.updateVolumeTrendChart();
                });
            });
        }
    },
    
    /**
     * Calculate date range based on period
     */
    calculateDateRange(period) {
        const now = new Date();
        this.toDate = now.toISOString().split('T')[0];
        
        let fromDate = new Date();
        switch (period) {
            case '1m':
                fromDate.setMonth(fromDate.getMonth() - 1);
                break;
            case '3m':
                fromDate.setMonth(fromDate.getMonth() - 3);
                break;
            case '6m':
                fromDate.setMonth(fromDate.getMonth() - 6);
                break;
            case '1y':
                fromDate.setFullYear(fromDate.getFullYear() - 1);
                break;
            case 'all':
                fromDate = new Date(2020, 0, 1);
                break;
        }
        
        this.fromDate = fromDate.toISOString().split('T')[0];
    },
    
    /**
     * Show login required panel
     */
    showLoginRequired() {
        const loginPanel = document.getElementById('loginRequired');
        const dashboardContent = document.getElementById('dashboardContent');
        
        if (loginPanel) loginPanel.style.display = 'block';
        if (dashboardContent) dashboardContent.style.display = 'none';
    },
    
    /**
     * Show dashboard content
     */
    showDashboard() {
        const loginPanel = document.getElementById('loginRequired');
        const dashboardContent = document.getElementById('dashboardContent');
        
        if (loginPanel) loginPanel.style.display = 'none';
        if (dashboardContent) dashboardContent.style.display = 'block';
    },
    
    /**
     * Load all data
     */
    async loadAllData() {
        if (!this.userEmail) return;
        
        console.log(`📊 Loading dashboard data for: ${this.userEmail}`);
        
        try {
            if (this.userType === 'shipper') {
                await Promise.all([
                    this.loadShipperSummary(),
                    this.loadVolumeTrend(),
                    this.loadCostByType(),
                    this.loadTopCountries(),
                    this.loadRouteStats(),
                    this.loadForwarderRanking(),
                    this.loadContainerEfficiency()
                ]);
            } else {
                await Promise.all([
                    this.loadForwarderSummary(),
                    this.loadForwarderMonthlyTrend(),
                    this.loadForwarderBidStats(),
                    this.loadForwarderRouteStats(),
                    this.loadForwarderCompetitiveness(),
                    this.loadForwarderRatingTrend()
                ]);
            }
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    },
    
    // ==========================================
    // SHIPPER APIs
    // ==========================================
    
    /**
     * Load shipper summary (KPIs)
     */
    async loadShipperSummary() {
        const url = `${QUOTE_API_BASE}/api/analytics/shipper/summary?customer_email=${encodeURIComponent(this.userEmail)}&from_date=${this.fromDate}&to_date=${this.toDate}`;
        
        try {
            const response = await fetch(url);
            if (!response.ok) {
                // Use mock data if API not available
                this.renderShipperSummaryMock();
                return;
            }
            const data = await response.json();
            
            // Update KPI cards
            document.getElementById('kpiTotalRequests').textContent = data.total_requests?.toLocaleString() || '-';
            document.getElementById('kpiAwardRate').textContent = data.award_rate ? `${data.award_rate}%` : '-';
            document.getElementById('kpiAvgBids').textContent = data.avg_bids_per_request?.toFixed(1) || '-';
            document.getElementById('kpiSavingRate').textContent = data.avg_saving_rate ? `${data.avg_saving_rate}%` : '-';
            
            // Update total cost
            if (document.getElementById('totalCostValue')) {
                document.getElementById('totalCostValue').textContent = `KRW ${(data.total_cost_krw || 0).toLocaleString()}`;
            }
            if (document.getElementById('summaryPeriod') && data.period) {
                document.getElementById('summaryPeriod').textContent = 
                    `${data.period.from_date} ~ ${data.period.to_date} 선정된 운송 건 합계`;
            }
            
            // Update saving amount
            if (document.getElementById('totalSavingAmount') && data.total_saved_krw) {
                document.getElementById('totalSavingAmount').textContent = `₩${data.total_saved_krw.toLocaleString()}`;
            }
            
        } catch (error) {
            console.error('Error loading shipper summary:', error);
            this.renderShipperSummaryMock();
        }
    },
    
    /**
     * Render mock data for shipper summary
     */
    renderShipperSummaryMock() {
        document.getElementById('kpiTotalRequests').textContent = '24';
        document.getElementById('kpiAwardRate').textContent = '75%';
        document.getElementById('kpiAvgBids').textContent = '4.2';
        document.getElementById('kpiSavingRate').textContent = '8.5%';
        
        if (document.getElementById('totalCostValue')) {
            document.getElementById('totalCostValue').textContent = 'KRW 156,780,000';
        }
        if (document.getElementById('totalSavingAmount')) {
            document.getElementById('totalSavingAmount').textContent = '₩14,250,000';
        }
    },
    
    /**
     * Load volume trend data
     */
    async loadVolumeTrend() {
        const url = `${QUOTE_API_BASE}/api/dashboard/shipper/volume-trend?customer_email=${encodeURIComponent(this.userEmail)}&from_date=${this.fromDate}&to_date=${this.toDate}`;
        
        try {
            const response = await fetch(url);
            if (!response.ok) {
                this.renderVolumeTrendMock();
                return;
            }
            const data = await response.json();
            this.volumeTrendData = data.data;
            this.updateVolumeTrendChart();
        } catch (error) {
            console.error('Error loading volume trend:', error);
            this.renderVolumeTrendMock();
        }
    },
    
    /**
     * Render mock volume trend chart
     */
    renderVolumeTrendMock() {
        this.volumeTrendData = [
            { month: '2024-07', teu: 45, cbm: 320, kgs: 28500 },
            { month: '2024-08', teu: 52, cbm: 380, kgs: 32000 },
            { month: '2024-09', teu: 48, cbm: 350, kgs: 29800 },
            { month: '2024-10', teu: 61, cbm: 420, kgs: 35600 },
            { month: '2024-11', teu: 58, cbm: 400, kgs: 34200 },
            { month: '2024-12', teu: 65, cbm: 450, kgs: 38500 }
        ];
        this.updateVolumeTrendChart();
    },
    
    /**
     * Update volume trend chart with current type
     */
    updateVolumeTrendChart() {
        const canvas = document.getElementById('volumeTrendChart');
        if (!canvas || !this.volumeTrendData) return;
        
        if (this.charts.volumeTrend) {
            this.charts.volumeTrend.destroy();
        }
        
        const labels = this.volumeTrendData.map(d => d.month);
        const values = this.volumeTrendData.map(d => d[this.volumeType]);
        
        const typeLabels = {
            teu: 'TEU',
            cbm: 'CBM',
            kgs: 'KGS'
        };
        
        this.charts.volumeTrend = new Chart(canvas, {
            type: 'line',
            data: {
                labels,
                datasets: [{
                    label: typeLabels[this.volumeType],
                    data: values,
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: this.getChartOptions('물량')
        });
    },
    
    /**
     * Load cost by shipping type
     */
    async loadCostByType() {
        const url = `${QUOTE_API_BASE}/api/analytics/shipper/cost-by-type?customer_email=${encodeURIComponent(this.userEmail)}&from_date=${this.fromDate}&to_date=${this.toDate}`;
        
        try {
            const response = await fetch(url);
            if (!response.ok) {
                this.renderCostByTypeMock();
                return;
            }
            const data = await response.json();
            this.renderCostByTypeChart(data.data);
        } catch (error) {
            console.error('Error loading cost by type:', error);
            this.renderCostByTypeMock();
        }
    },
    
    /**
     * Render mock cost by type chart
     */
    renderCostByTypeMock() {
        const mockData = [
            { shipping_type: 'ocean', total_cost_krw: 85000000, count: 12, percentage: 54 },
            { shipping_type: 'air', total_cost_krw: 45000000, count: 8, percentage: 29 },
            { shipping_type: 'truck', total_cost_krw: 26780000, count: 4, percentage: 17 }
        ];
        this.renderCostByTypeChart(mockData);
    },
    
    /**
     * Render cost by type doughnut chart
     */
    renderCostByTypeChart(data) {
        const canvas = document.getElementById('costByTypeChart');
        if (!canvas) return;
        
        if (this.charts.costByType) {
            this.charts.costByType.destroy();
        }
        
        const colors = {
            'ocean': '#3b82f6',
            'air': '#8b5cf6',
            'truck': '#10b981',
            'rail': '#f59e0b'
        };
        
        const typeLabels = {
            'ocean': 'Ocean',
            'air': 'Air',
            'truck': 'Truck',
            'rail': 'Rail'
        };
        
        this.charts.costByType = new Chart(canvas, {
            type: 'doughnut',
            data: {
                labels: data.map(d => typeLabels[d.shipping_type] || d.shipping_type),
                datasets: [{
                    data: data.map(d => d.total_cost_krw),
                    backgroundColor: data.map(d => colors[d.shipping_type] || '#6366f1'),
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '65%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: 'rgba(255, 255, 255, 0.7)',
                            usePointStyle: true,
                            padding: 15
                        }
                    }
                }
            }
        });
        
        // Render summary
        const summaryEl = document.getElementById('costByTypeSummary');
        if (summaryEl) {
            summaryEl.innerHTML = `
                <div class="cost-type-items">
                    ${data.map(d => `
                        <div class="cost-type-item">
                            <span class="type-label">${typeLabels[d.shipping_type] || d.shipping_type}</span>
                            <span class="type-value">${d.count}건</span>
                            <span class="type-percentage">${d.percentage}%</span>
                        </div>
                    `).join('')}
                </div>
            `;
        }
    },
    
    /**
     * Load top countries (export/import)
     */
    async loadTopCountries() {
        // Export countries
        const exportUrl = `${QUOTE_API_BASE}/api/dashboard/shipper/top-export?customer_email=${encodeURIComponent(this.userEmail)}&from_date=${this.fromDate}&to_date=${this.toDate}&limit=5`;
        const importUrl = `${QUOTE_API_BASE}/api/dashboard/shipper/top-import?customer_email=${encodeURIComponent(this.userEmail)}&from_date=${this.fromDate}&to_date=${this.toDate}&limit=5`;
        
        try {
            const [exportRes, importRes] = await Promise.all([
                fetch(exportUrl).catch(() => null),
                fetch(importUrl).catch(() => null)
            ]);
            
            if (!exportRes?.ok || !importRes?.ok) {
                this.renderTopCountriesMock();
                return;
            }
            
            const exportData = await exportRes.json();
            const importData = await importRes.json();
            
            this.renderTopExportChart(exportData.data);
            this.renderTopImportChart(importData.data);
        } catch (error) {
            console.error('Error loading top countries:', error);
            this.renderTopCountriesMock();
        }
    },
    
    /**
     * Render mock top countries
     */
    renderTopCountriesMock() {
        const exportMock = [
            { country: '중국', count: 15, volume: 120 },
            { country: '미국', count: 12, volume: 95 },
            { country: '일본', count: 8, volume: 65 },
            { country: '베트남', count: 6, volume: 48 },
            { country: '태국', count: 4, volume: 32 }
        ];
        
        const importMock = [
            { country: '독일', count: 10, volume: 85 },
            { country: '미국', count: 8, volume: 72 },
            { country: '중국', count: 7, volume: 58 },
            { country: '일본', count: 5, volume: 42 },
            { country: '프랑스', count: 3, volume: 25 }
        ];
        
        this.renderTopExportChart(exportMock);
        this.renderTopImportChart(importMock);
    },
    
    /**
     * Render top export chart
     */
    renderTopExportChart(data) {
        const canvas = document.getElementById('topExportChart');
        if (!canvas) return;
        
        if (this.charts.topExport) {
            this.charts.topExport.destroy();
        }
        
        this.charts.topExport = new Chart(canvas, {
            type: 'bar',
            data: {
                labels: data.map(d => d.country),
                datasets: [{
                    label: '건수',
                    data: data.map(d => d.count),
                    backgroundColor: 'rgba(99, 102, 241, 0.7)',
                    borderRadius: 6
                }]
            },
            options: {
                ...this.getChartOptions('건'),
                indexAxis: 'y',
                plugins: { legend: { display: false } }
            }
        });
    },
    
    /**
     * Render top import chart
     */
    renderTopImportChart(data) {
        const canvas = document.getElementById('topImportChart');
        if (!canvas) return;
        
        if (this.charts.topImport) {
            this.charts.topImport.destroy();
        }
        
        this.charts.topImport = new Chart(canvas, {
            type: 'bar',
            data: {
                labels: data.map(d => d.country),
                datasets: [{
                    label: '건수',
                    data: data.map(d => d.count),
                    backgroundColor: 'rgba(139, 92, 246, 0.7)',
                    borderRadius: 6
                }]
            },
            options: {
                ...this.getChartOptions('건'),
                indexAxis: 'y',
                plugins: { legend: { display: false } }
            }
        });
    },
    
    /**
     * Load route stats
     */
    async loadRouteStats() {
        const url = `${QUOTE_API_BASE}/api/analytics/shipper/route-stats?customer_email=${encodeURIComponent(this.userEmail)}&from_date=${this.fromDate}&to_date=${this.toDate}&limit=10`;
        
        try {
            const response = await fetch(url);
            if (!response.ok) {
                this.renderRouteStatsMock();
                return;
            }
            const data = await response.json();
            this.renderRouteStatsChart(data.data);
        } catch (error) {
            console.error('Error loading route stats:', error);
            this.renderRouteStatsMock();
        }
    },
    
    /**
     * Render mock route stats
     */
    renderRouteStatsMock() {
        const mockData = [
            { pol: '부산', pod: 'LA', count: 8, avg_bid_price_krw: 12500000 },
            { pol: '부산', pod: '상하이', count: 6, avg_bid_price_krw: 3200000 },
            { pol: '인천', pod: '나리타', count: 5, avg_bid_price_krw: 1800000 },
            { pol: '광양', pod: '로테르담', count: 4, avg_bid_price_krw: 18500000 },
            { pol: '부산', pod: '싱가포르', count: 3, avg_bid_price_krw: 8200000 }
        ];
        this.renderRouteStatsChart(mockData);
    },
    
    /**
     * Render route stats chart
     */
    renderRouteStatsChart(data) {
        const canvas = document.getElementById('routeStatsChart');
        if (!canvas) return;
        
        if (this.charts.routeStats) {
            this.charts.routeStats.destroy();
        }
        
        const labels = data.map(d => `${d.pol} → ${d.pod}`);
        
        this.charts.routeStats = new Chart(canvas, {
            type: 'bar',
            data: {
                labels,
                datasets: [{
                    label: '평균 운임 (KRW)',
                    data: data.map(d => d.avg_bid_price_krw),
                    backgroundColor: 'rgba(99, 102, 241, 0.7)',
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: { legend: { display: false } },
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.5)',
                            callback: (value) => `₩${(value / 1000000).toFixed(0)}M`
                        }
                    },
                    y: {
                        grid: { display: false },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)',
                            font: { size: 11 }
                        }
                    }
                }
            }
        });
    },
    
    /**
     * Load forwarder ranking
     */
    async loadForwarderRanking() {
        const url = `${QUOTE_API_BASE}/api/analytics/shipper/forwarder-ranking?customer_email=${encodeURIComponent(this.userEmail)}&from_date=${this.fromDate}&to_date=${this.toDate}&limit=10`;
        
        try {
            const response = await fetch(url);
            if (!response.ok) {
                this.renderForwarderRankingMock();
                return;
            }
            const data = await response.json();
            this.renderForwarderRankingTable(data.data);
        } catch (error) {
            console.error('Error loading forwarder ranking:', error);
            this.renderForwarderRankingMock();
        }
    },
    
    /**
     * Render mock forwarder ranking
     */
    renderForwarderRankingMock() {
        const mockData = [
            { rank: 1, company_masked: 'A** 물류', awarded_count: 8, total_amount_krw: 65000000, avg_rating: 4.5, rating_count: 6 },
            { rank: 2, company_masked: 'B** 로지스틱스', awarded_count: 5, total_amount_krw: 42000000, avg_rating: 4.2, rating_count: 4 },
            { rank: 3, company_masked: 'C** 익스프레스', awarded_count: 4, total_amount_krw: 35000000, avg_rating: 4.0, rating_count: 3 },
            { rank: 4, company_masked: 'D** 포워딩', awarded_count: 3, total_amount_krw: 28000000, avg_rating: 3.8, rating_count: 2 },
            { rank: 5, company_masked: 'E** 물류', awarded_count: 2, total_amount_krw: 18000000, avg_rating: 4.0, rating_count: 2 }
        ];
        this.renderForwarderRankingTable(mockData);
    },
    
    /**
     * Render forwarder ranking table
     */
    renderForwarderRankingTable(data) {
        const tbody = document.getElementById('forwarderRankingBody');
        if (!tbody) return;
        
        if (!data || data.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" style="text-align: center; padding: 2rem; color: rgba(255,255,255,0.5);">
                        데이터가 없습니다
                    </td>
                </tr>
            `;
            return;
        }
        
        tbody.innerHTML = data.map(item => `
            <tr>
                <td>
                    <span class="rank-badge ${this.getRankClass(item.rank)}">${item.rank}</span>
                </td>
                <td>${item.company_masked}</td>
                <td>${item.awarded_count}회</td>
                <td>₩${(item.total_amount_krw / 1000000).toFixed(1)}M</td>
                <td>
                    ${this.renderStars(item.avg_rating)}
                    <span style="margin-left: 4px; color: rgba(255,255,255,0.5); font-size: 0.75rem;">
                        (${item.rating_count || 0})
                    </span>
                </td>
            </tr>
        `).join('');
    },
    
    /**
     * Load container efficiency (FCL only)
     */
    async loadContainerEfficiency() {
        const url = `${QUOTE_API_BASE}/api/dashboard/shipper/container-efficiency?customer_email=${encodeURIComponent(this.userEmail)}&from_date=${this.fromDate}&to_date=${this.toDate}`;
        
        try {
            const response = await fetch(url);
            if (!response.ok) {
                this.renderContainerEfficiencyMock();
                return;
            }
            const data = await response.json();
            this.renderContainerEfficiency(data.data);
        } catch (error) {
            console.error('Error loading container efficiency:', error);
            this.renderContainerEfficiencyMock();
        }
    },
    
    /**
     * Render mock container efficiency
     */
    renderContainerEfficiencyMock() {
        const mockData = [
            { container_type: "20'GP", efficiency: 82, count: 15 },
            { container_type: "40'GP", efficiency: 75, count: 12 },
            { container_type: "40'HC", efficiency: 88, count: 8 },
            { container_type: "20'RF", efficiency: 65, count: 3 }
        ];
        this.renderContainerEfficiency(mockData);
    },
    
    /**
     * Render container efficiency grid
     */
    renderContainerEfficiency(data) {
        const grid = document.getElementById('containerEfficiencyGrid');
        if (!grid) return;
        
        if (!data || data.length === 0) {
            grid.innerHTML = `
                <div style="text-align: center; padding: 2rem; color: rgba(255,255,255,0.5); grid-column: 1 / -1;">
                    FCL 운송 데이터가 없습니다
                </div>
            `;
            return;
        }
        
        grid.innerHTML = data.map(item => {
            const effClass = item.efficiency >= 80 ? 'high' : (item.efficiency >= 60 ? 'medium' : 'low');
            return `
                <div class="efficiency-card">
                    <div class="container-type">${item.container_type}</div>
                    <div class="efficiency-value ${effClass}">${item.efficiency}%</div>
                    <div class="efficiency-label">${item.count}건 평균</div>
                </div>
            `;
        }).join('');
    },
    
    // ==========================================
    // FORWARDER APIs
    // ==========================================
    
    /**
     * Load forwarder summary
     */
    async loadForwarderSummary() {
        const url = `${QUOTE_API_BASE}/api/analytics/forwarder/summary?forwarder_email=${encodeURIComponent(this.userEmail)}&from_date=${this.fromDate}&to_date=${this.toDate}`;
        
        try {
            const response = await fetch(url);
            if (!response.ok) {
                this.renderForwarderSummaryMock();
                return;
            }
            const data = await response.json();
            
            document.getElementById('kpiTotalBids').textContent = data.total_bids?.toLocaleString() || '-';
            document.getElementById('kpiAwardRate').textContent = data.award_rate ? `${data.award_rate}%` : '-';
            document.getElementById('kpiAwardCounts').textContent = `선정 ${data.awarded_count || 0} / 탈락 ${data.rejected_count || 0}`;
            document.getElementById('kpiAvgRank').textContent = data.avg_rank > 0 ? `#${data.avg_rank.toFixed(1)}` : '-';
            document.getElementById('kpiAvgRating').textContent = data.avg_rating?.toFixed(1) || '-';
            
            if (document.getElementById('totalRevenueValue')) {
                document.getElementById('totalRevenueValue').textContent = `KRW ${(data.total_revenue_krw || 0).toLocaleString()}`;
            }
        } catch (error) {
            console.error('Error loading forwarder summary:', error);
            this.renderForwarderSummaryMock();
        }
    },
    
    /**
     * Render mock forwarder summary
     */
    renderForwarderSummaryMock() {
        if (document.getElementById('kpiTotalBids')) {
            document.getElementById('kpiTotalBids').textContent = '42';
        }
        if (document.getElementById('kpiAwardRate')) {
            document.getElementById('kpiAwardRate').textContent = '38%';
        }
        if (document.getElementById('kpiAwardCounts')) {
            document.getElementById('kpiAwardCounts').textContent = '선정 16 / 탈락 26';
        }
        if (document.getElementById('kpiAvgRank')) {
            document.getElementById('kpiAvgRank').textContent = '#2.3';
        }
        if (document.getElementById('kpiAvgRating')) {
            document.getElementById('kpiAvgRating').textContent = '4.2';
        }
        if (document.getElementById('totalRevenueValue')) {
            document.getElementById('totalRevenueValue').textContent = 'KRW 185,000,000';
        }
    },
    
    /**
     * Load forwarder monthly trend
     */
    async loadForwarderMonthlyTrend() {
        const url = `${QUOTE_API_BASE}/api/analytics/forwarder/monthly-trend?forwarder_email=${encodeURIComponent(this.userEmail)}&from_date=${this.fromDate}&to_date=${this.toDate}`;
        
        try {
            const response = await fetch(url);
            if (!response.ok) {
                this.renderForwarderMonthlyTrendMock();
                return;
            }
            const data = await response.json();
            this.renderForwarderMonthlyTrendChart(data.data);
        } catch (error) {
            console.error('Error loading forwarder monthly trend:', error);
            this.renderForwarderMonthlyTrendMock();
        }
    },
    
    /**
     * Render mock forwarder monthly trend
     */
    renderForwarderMonthlyTrendMock() {
        const mockData = [
            { month: '2024-07', bid_count: 6, awarded_count: 2, rejected_count: 4 },
            { month: '2024-08', bid_count: 8, awarded_count: 3, rejected_count: 5 },
            { month: '2024-09', bid_count: 7, awarded_count: 3, rejected_count: 4 },
            { month: '2024-10', bid_count: 9, awarded_count: 4, rejected_count: 5 },
            { month: '2024-11', bid_count: 6, awarded_count: 2, rejected_count: 4 },
            { month: '2024-12', bid_count: 6, awarded_count: 2, rejected_count: 4 }
        ];
        this.renderForwarderMonthlyTrendChart(mockData);
    },
    
    /**
     * Render forwarder monthly trend chart
     */
    renderForwarderMonthlyTrendChart(data) {
        const canvas = document.getElementById('monthlyTrendChart');
        if (!canvas) return;
        
        if (this.charts.monthlyTrend) {
            this.charts.monthlyTrend.destroy();
        }
        
        this.charts.monthlyTrend = new Chart(canvas, {
            type: 'line',
            data: {
                labels: data.map(d => d.month),
                datasets: [
                    {
                        label: '입찰',
                        data: data.map(d => d.bid_count),
                        borderColor: '#6366f1',
                        backgroundColor: 'rgba(99, 102, 241, 0.1)',
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: '낙찰',
                        data: data.map(d => d.awarded_count),
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: '탈락',
                        data: data.map(d => d.rejected_count),
                        borderColor: '#ef4444',
                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                        fill: true,
                        tension: 0.4
                    }
                ]
            },
            options: this.getChartOptions('건')
        });
    },
    
    /**
     * Load forwarder bid stats by type
     */
    async loadForwarderBidStats() {
        // Implementation similar to shipper cost by type
    },
    
    /**
     * Load forwarder route stats with sparkline
     */
    async loadForwarderRouteStats() {
        const url = `${QUOTE_API_BASE}/api/dashboard/forwarder/route-stats?forwarder_email=${encodeURIComponent(this.userEmail)}&from_date=${this.fromDate}&to_date=${this.toDate}&limit=10`;
        
        try {
            const response = await fetch(url);
            if (!response.ok) {
                this.renderForwarderRouteStatsMock();
                return;
            }
            const data = await response.json();
            this.renderForwarderRouteStatsTable(data.data);
        } catch (error) {
            console.error('Error loading forwarder route stats:', error);
            this.renderForwarderRouteStatsMock();
        }
    },
    
    /**
     * Render mock forwarder route stats
     */
    renderForwarderRouteStatsMock() {
        const mockData = [
            { route: '부산 → LA', bids: 15, awards: 8, award_rate: 53.3, total_revenue_krw: 120000000, sparkline: [3, 5, 2, 4, 6, 3] },
            { route: '부산 → 상하이', bids: 12, awards: 5, award_rate: 41.7, total_revenue_krw: 45000000, sparkline: [2, 3, 4, 3, 5, 4] },
            { route: '인천 → 나리타', bids: 8, awards: 4, award_rate: 50.0, total_revenue_krw: 32000000, sparkline: [1, 2, 1, 2, 1, 2] },
            { route: '부산 → 싱가포르', bids: 10, awards: 2, award_rate: 20.0, total_revenue_krw: 28000000, sparkline: [0, 1, 0, 1, 0, 1] },
            { route: '광양 → 로테르담', bids: 6, awards: 3, award_rate: 50.0, total_revenue_krw: 54000000, sparkline: [1, 1, 0, 2, 1, 1] }
        ];
        this.renderForwarderRouteStatsTable(mockData);
    },
    
    /**
     * Render forwarder route stats table with sparkline
     */
    renderForwarderRouteStatsTable(data) {
        const tbody = document.getElementById('routeStatsBody');
        if (!tbody) return;
        
        if (!data || data.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" style="text-align: center; padding: 2rem; color: rgba(255,255,255,0.5);">
                        데이터가 없습니다
                    </td>
                </tr>
            `;
            return;
        }
        
        tbody.innerHTML = data.map(item => {
            const rateClass = item.award_rate >= 50 ? 'high' : (item.award_rate >= 30 ? 'medium' : 'low');
            const maxSparkline = Math.max(...item.sparkline, 1);
            
            return `
                <tr>
                    <td class="route-cell">${item.route}</td>
                    <td>${item.bids}건</td>
                    <td>${item.awards}건</td>
                    <td><span class="award-rate ${rateClass}">${item.award_rate}%</span></td>
                    <td>₩${(item.total_revenue_krw / 1000000).toFixed(0)}M</td>
                    <td>
                        <div class="sparkline-container">
                            ${item.sparkline.map(val => `
                                <div class="sparkline-bar" style="height: ${(val / maxSparkline) * 24}px;" title="${val}건"></div>
                            `).join('')}
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
    },
    
    /**
     * Load forwarder competitiveness
     */
    async loadForwarderCompetitiveness() {
        // Implementation for competitiveness chart
    },
    
    /**
     * Load forwarder rating trend
     */
    async loadForwarderRatingTrend() {
        // Implementation for rating trend chart
    },
    
    // ==========================================
    // UTILITY FUNCTIONS
    // ==========================================
    
    /**
     * Get common chart options
     */
    getChartOptions(yAxisLabel = '') {
        return {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: 'rgba(255, 255, 255, 0.7)',
                        usePointStyle: true,
                        padding: 20
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: 'rgba(255, 255, 255, 0.5)' }
                },
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: 'rgba(255, 255, 255, 0.5)' }
                }
            }
        };
    },
    
    /**
     * Get rank badge class
     */
    getRankClass(rank) {
        if (rank === 1) return 'gold';
        if (rank === 2) return 'silver';
        if (rank === 3) return 'bronze';
        return 'normal';
    },
    
    /**
     * Render star rating
     */
    renderStars(rating) {
        const fullStars = Math.floor(rating || 0);
        const hasHalf = (rating || 0) - fullStars >= 0.5;
        const emptyStars = 5 - fullStars - (hasHalf ? 1 : 0);
        
        let html = '<span class="rating-stars">';
        
        for (let i = 0; i < fullStars; i++) {
            html += '<i class="fas fa-star"></i>';
        }
        
        if (hasHalf) {
            html += '<i class="fas fa-star-half-alt"></i>';
        }
        
        for (let i = 0; i < emptyStars; i++) {
            html += '<i class="far fa-star"></i>';
        }
        
        html += '</span>';
        return html;
    },
    
    /**
     * Export data
     */
    exportData() {
        const type = this.userType === 'shipper' ? '화주' : '운송사';
        alert(`${type} 대시보드 데이터 내보내기 기능은 준비 중입니다.`);
    }
};

// Export for global access
window.Dashboard = Dashboard;
