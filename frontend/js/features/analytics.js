/**
 * Analytics Dashboard Module
 * 화주/운송사용 분석 대시보드
 */

import { API_BASE_URL } from '../config/api.js';

export const Analytics = {
    // State
    userType: 'shipper', // 'shipper' or 'forwarder'
    userId: null,
    currentPeriod: '6m',
    charts: {},
    
    // Date range
    fromDate: null,
    toDate: null,
    
    /**
     * Initialize Analytics
     */
    init(userType = 'shipper') {
        this.userType = userType;
        this.loadSession();
        this.setupEventListeners();
        this.calculateDateRange(this.currentPeriod);
        
        if (this.userId) {
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
        const sessionKey = this.userType === 'shipper' ? 'shipperSession' : 'forwarderSession';
        const session = localStorage.getItem(sessionKey);
        
        if (session) {
            try {
                const data = JSON.parse(session);
                this.userId = data.id;
                this.updateAuthUI(data);
            } catch (e) {
                console.error('Session parse error:', e);
            }
        }
    },
    
    /**
     * Update auth UI
     */
    updateAuthUI(userData) {
        const authContainer = document.getElementById('headerAuthContainer');
        if (authContainer) {
            authContainer.innerHTML = `
                <div class="user-info">
                    <span class="user-name">${userData.company || userData.name}</span>
                    <button class="header-auth-btn" onclick="Analytics.logout()">
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
        const sessionKey = this.userType === 'shipper' ? 'shipperSession' : 'forwarderSession';
        localStorage.removeItem(sessionKey);
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
                fromDate = new Date(2020, 0, 1); // Since 2020
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
     * Show dashboard
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
        if (!this.userId) return;
        
        try {
            if (this.userType === 'shipper') {
                await Promise.all([
                    this.loadShipperSummary(),
                    this.loadShipperMonthlyTrend(),
                    this.loadShipperCostByType(),
                    this.loadShipperRouteStats(),
                    this.loadShipperForwarderRanking()
                ]);
            } else {
                await Promise.all([
                    this.loadForwarderSummary(),
                    this.loadForwarderMonthlyTrend(),
                    this.loadForwarderBidStats(),
                    this.loadForwarderCompetitiveness(),
                    this.loadForwarderRatingTrend()
                ]);
            }
        } catch (error) {
            console.error('Error loading analytics data:', error);
        }
    },
    
    // ==========================================
    // SHIPPER APIs
    // ==========================================
    
    /**
     * Load shipper summary
     */
    async loadShipperSummary() {
        const idParam = `customer_id=${this.userId}`;
        const url = `${API_BASE_URL}/api/analytics/shipper/summary?${idParam}&from_date=${this.fromDate}&to_date=${this.toDate}`;
        
        try {
            const response = await fetch(url);
            const data = await response.json();
            
            // Update KPI cards
            document.getElementById('kpiTotalRequests').textContent = data.total_requests.toLocaleString();
            document.getElementById('kpiAwardRate').textContent = `${data.award_rate}%`;
            document.getElementById('kpiAvgBids').textContent = data.avg_bids_per_request.toFixed(1);
            document.getElementById('kpiSavingRate').textContent = `${data.avg_saving_rate}%`;
            
            // Update total cost
            document.getElementById('totalCostValue').textContent = `KRW ${data.total_cost_krw.toLocaleString()}`;
            document.getElementById('summaryPeriod').textContent = 
                `${data.period.from_date} ~ ${data.period.to_date} 선정된 운송 건 합계`;
            
        } catch (error) {
            console.error('Error loading shipper summary:', error);
        }
    },
    
    /**
     * Load shipper monthly trend
     */
    async loadShipperMonthlyTrend() {
        const url = `${API_BASE_URL}/api/analytics/shipper/monthly-trend?customer_id=${this.userId}&from_date=${this.fromDate}&to_date=${this.toDate}`;
        
        try {
            const response = await fetch(url);
            const data = await response.json();
            
            this.renderMonthlyTrendChart(data.data, 'shipper');
        } catch (error) {
            console.error('Error loading monthly trend:', error);
        }
    },
    
    /**
     * Load shipper cost by type
     */
    async loadShipperCostByType() {
        const url = `${API_BASE_URL}/api/analytics/shipper/cost-by-type?customer_id=${this.userId}&from_date=${this.fromDate}&to_date=${this.toDate}`;
        
        try {
            const response = await fetch(url);
            const data = await response.json();
            
            this.renderCostByTypeChart(data.data);
        } catch (error) {
            console.error('Error loading cost by type:', error);
        }
    },
    
    /**
     * Load shipper route stats
     */
    async loadShipperRouteStats() {
        const url = `${API_BASE_URL}/api/analytics/shipper/route-stats?customer_id=${this.userId}&from_date=${this.fromDate}&to_date=${this.toDate}&limit=10`;
        
        try {
            const response = await fetch(url);
            const data = await response.json();
            
            this.renderRouteStatsChart(data.data);
        } catch (error) {
            console.error('Error loading route stats:', error);
        }
    },
    
    /**
     * Load shipper forwarder ranking
     */
    async loadShipperForwarderRanking() {
        const url = `${API_BASE_URL}/api/analytics/shipper/forwarder-ranking?customer_id=${this.userId}&from_date=${this.fromDate}&to_date=${this.toDate}&limit=10`;
        
        try {
            const response = await fetch(url);
            const data = await response.json();
            
            this.renderForwarderRankingTable(data.data);
        } catch (error) {
            console.error('Error loading forwarder ranking:', error);
        }
    },
    
    // ==========================================
    // FORWARDER APIs
    // ==========================================
    
    /**
     * Load forwarder summary
     */
    async loadForwarderSummary() {
        const url = `${API_BASE_URL}/api/analytics/forwarder/summary?forwarder_id=${this.userId}&from_date=${this.fromDate}&to_date=${this.toDate}`;
        
        try {
            const response = await fetch(url);
            const data = await response.json();
            
            // Update KPI cards
            document.getElementById('kpiTotalBids').textContent = data.total_bids.toLocaleString();
            document.getElementById('kpiAwardRate').textContent = `${data.award_rate}%`;
            document.getElementById('kpiAwardCounts').textContent = `선정 ${data.awarded_count} / 탈락 ${data.rejected_count}`;
            document.getElementById('kpiAvgRank').textContent = data.avg_rank > 0 ? `#${data.avg_rank.toFixed(1)}` : '-';
            document.getElementById('kpiAvgRating').textContent = data.avg_rating.toFixed(1);
            
            // Update total revenue
            document.getElementById('totalRevenueValue').textContent = `KRW ${data.total_revenue_krw.toLocaleString()}`;
            document.getElementById('summaryPeriod').textContent = 
                `${data.period.from_date} ~ ${data.period.to_date} 낙찰된 건 합계`;
            
        } catch (error) {
            console.error('Error loading forwarder summary:', error);
        }
    },
    
    /**
     * Load forwarder monthly trend
     */
    async loadForwarderMonthlyTrend() {
        const url = `${API_BASE_URL}/api/analytics/forwarder/monthly-trend?forwarder_id=${this.userId}&from_date=${this.fromDate}&to_date=${this.toDate}`;
        
        try {
            const response = await fetch(url);
            const data = await response.json();
            
            this.renderMonthlyTrendChart(data.data, 'forwarder');
        } catch (error) {
            console.error('Error loading monthly trend:', error);
        }
    },
    
    /**
     * Load forwarder bid stats
     */
    async loadForwarderBidStats() {
        const url = `${API_BASE_URL}/api/analytics/forwarder/bid-stats?forwarder_id=${this.userId}&from_date=${this.fromDate}&to_date=${this.toDate}`;
        
        try {
            const response = await fetch(url);
            const data = await response.json();
            
            this.renderBidStatsByTypeChart(data.data);
        } catch (error) {
            console.error('Error loading bid stats:', error);
        }
    },
    
    /**
     * Load forwarder competitiveness
     */
    async loadForwarderCompetitiveness() {
        const url = `${API_BASE_URL}/api/analytics/forwarder/competitiveness?forwarder_id=${this.userId}&from_date=${this.fromDate}&to_date=${this.toDate}`;
        
        try {
            const response = await fetch(url);
            const data = await response.json();
            
            this.renderCompetitivenessChart(data.data);
        } catch (error) {
            console.error('Error loading competitiveness:', error);
        }
    },
    
    /**
     * Load forwarder rating trend
     */
    async loadForwarderRatingTrend() {
        const url = `${API_BASE_URL}/api/analytics/forwarder/rating-trend?forwarder_id=${this.userId}&from_date=${this.fromDate}&to_date=${this.toDate}`;
        
        try {
            const response = await fetch(url);
            const data = await response.json();
            
            this.renderRatingTrendChart(data.data);
            this.updateRatingSummary(data.current_rating, data.total_ratings);
        } catch (error) {
            console.error('Error loading rating trend:', error);
        }
    },
    
    // ==========================================
    // CHART RENDERING
    // ==========================================
    
    /**
     * Render monthly trend chart
     */
    renderMonthlyTrendChart(data, type) {
        const canvas = document.getElementById('monthlyTrendChart');
        if (!canvas) return;
        
        // Destroy existing chart
        if (this.charts.monthlyTrend) {
            this.charts.monthlyTrend.destroy();
        }
        
        const labels = data.map(d => d.month);
        
        let datasets = [];
        if (type === 'shipper') {
            datasets = [
                {
                    label: '요청 건수',
                    data: data.map(d => d.request_count),
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    fill: true,
                    tension: 0.4
                },
                {
                    label: '입찰 건수',
                    data: data.map(d => d.bid_count),
                    borderColor: '#8b5cf6',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    fill: true,
                    tension: 0.4
                },
                {
                    label: '낙찰 건수',
                    data: data.map(d => d.awarded_count),
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    fill: true,
                    tension: 0.4
                }
            ];
        } else {
            datasets = [
                {
                    label: '입찰 건수',
                    data: data.map(d => d.bid_count),
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    fill: true,
                    tension: 0.4
                },
                {
                    label: '낙찰 건수',
                    data: data.map(d => d.awarded_count),
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    fill: true,
                    tension: 0.4
                },
                {
                    label: '탈락 건수',
                    data: data.map(d => d.rejected_count),
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    fill: true,
                    tension: 0.4
                }
            ];
        }
        
        this.charts.monthlyTrend = new Chart(canvas, {
            type: 'line',
            data: { labels, datasets },
            options: {
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
            }
        });
    },
    
    /**
     * Render cost by type chart (Shipper)
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
     * Render route stats chart (Shipper)
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
                    label: '평균 입찰가 (KRW)',
                    data: data.map(d => d.avg_bid_price_krw),
                    backgroundColor: 'rgba(99, 102, 241, 0.7)',
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {
                    legend: { display: false }
                },
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
     * Render forwarder ranking table (Shipper)
     */
    renderForwarderRankingTable(data) {
        const tbody = document.getElementById('forwarderRankingBody');
        if (!tbody) return;
        
        if (data.length === 0) {
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
                        (${item.rating_count})
                    </span>
                </td>
            </tr>
        `).join('');
    },
    
    /**
     * Render bid stats by type chart (Forwarder)
     */
    renderBidStatsByTypeChart(data) {
        const canvas = document.getElementById('bidStatsByTypeChart');
        if (!canvas) return;
        
        if (this.charts.bidStats) {
            this.charts.bidStats.destroy();
        }
        
        const typeLabels = {
            'ocean': 'Ocean',
            'air': 'Air',
            'truck': 'Truck',
            'rail': 'Rail'
        };
        
        this.charts.bidStats = new Chart(canvas, {
            type: 'doughnut',
            data: {
                labels: data.map(d => typeLabels[d.shipping_type] || d.shipping_type),
                datasets: [{
                    data: data.map(d => d.bid_count),
                    backgroundColor: ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b'],
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
        const summaryEl = document.getElementById('bidStatsSummary');
        if (summaryEl) {
            summaryEl.innerHTML = `
                <div class="cost-type-items">
                    ${data.map(d => `
                        <div class="cost-type-item">
                            <span class="type-label">${typeLabels[d.shipping_type] || d.shipping_type}</span>
                            <span class="type-value">${d.bid_count}건 / ${d.awarded_count}낙찰</span>
                            <span class="type-percentage">${d.award_rate}%</span>
                        </div>
                    `).join('')}
                </div>
            `;
        }
    },
    
    /**
     * Render competitiveness chart (Forwarder)
     */
    renderCompetitivenessChart(data) {
        const canvas = document.getElementById('competitivenessChart');
        if (!canvas) return;
        
        if (this.charts.competitiveness) {
            this.charts.competitiveness.destroy();
        }
        
        this.charts.competitiveness = new Chart(canvas, {
            type: 'bar',
            data: {
                labels: ['내 평균', '시장 평균', '낙찰 평균'],
                datasets: [{
                    label: '입찰가 (KRW)',
                    data: [data.my_avg_bid_krw, data.market_avg_bid_krw, data.winning_avg_bid_krw],
                    backgroundColor: ['#6366f1', '#8b5cf6', '#10b981'],
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { color: 'rgba(255, 255, 255, 0.7)' }
                    },
                    y: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.5)',
                            callback: (value) => `₩${(value / 1000000).toFixed(0)}M`
                        }
                    }
                }
            }
        });
        
        // Update summary
        const priceComp = document.getElementById('priceCompetitiveness');
        const winRate = document.getElementById('winRateVsMarket');
        
        if (priceComp) {
            priceComp.textContent = `${data.price_competitiveness > 0 ? '+' : ''}${data.price_competitiveness}%`;
            priceComp.className = `comp-value ${data.price_competitiveness >= 0 ? 'positive' : 'negative'}`;
        }
        
        if (winRate) {
            winRate.textContent = `${data.win_rate_vs_market > 0 ? '+' : ''}${data.win_rate_vs_market}%`;
            winRate.className = `comp-value ${data.win_rate_vs_market >= 0 ? 'positive' : 'negative'}`;
        }
    },
    
    /**
     * Render rating trend chart (Forwarder)
     */
    renderRatingTrendChart(data) {
        const canvas = document.getElementById('ratingTrendChart');
        if (!canvas) return;
        
        if (this.charts.ratingTrend) {
            this.charts.ratingTrend.destroy();
        }
        
        this.charts.ratingTrend = new Chart(canvas, {
            type: 'line',
            data: {
                labels: data.map(d => d.month),
                datasets: [{
                    label: '평균 평점',
                    data: data.map(d => d.avg_score),
                    borderColor: '#fbbf24',
                    backgroundColor: 'rgba(251, 191, 36, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: 'rgba(255, 255, 255, 0.5)' }
                    },
                    y: {
                        min: 0,
                        max: 5,
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: 'rgba(255, 255, 255, 0.5)' }
                    }
                }
            }
        });
    },
    
    /**
     * Update rating summary
     */
    updateRatingSummary(currentRating, totalRatings) {
        const starsEl = document.getElementById('ratingStars');
        const scoreEl = document.getElementById('currentRating');
        const countEl = document.getElementById('totalRatings');
        
        if (starsEl) {
            starsEl.innerHTML = this.renderStars(currentRating);
        }
        
        if (scoreEl) {
            scoreEl.textContent = currentRating.toFixed(1);
        }
        
        if (countEl) {
            countEl.textContent = `(${totalRatings}개 평가)`;
        }
    },
    
    // ==========================================
    // UTILITY FUNCTIONS
    // ==========================================
    
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
        const fullStars = Math.floor(rating);
        const hasHalf = rating - fullStars >= 0.5;
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
        // Simple CSV export
        const type = this.userType === 'shipper' ? '화주' : '운송사';
        alert(`${type} 분석 데이터 내보내기 기능은 준비 중입니다.`);
    }
};

// Export for global access
window.Analytics = Analytics;
