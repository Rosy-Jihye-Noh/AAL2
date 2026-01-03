/**
 * MyPage Module
 * 마이페이지 기능
 */

const MyPage = {
    API_BASE: 'http://localhost:8001/api',
    currentUser: null,
    currentSection: 'dashboard',
    
    /**
     * Initialize the module
     */
    init() {
        this.checkAuth();
        this.setupNavigation();
        this.loadDashboard();
    },
    
    /**
     * Check authentication status
     */
    checkAuth() {
        const userData = localStorage.getItem('shipperUser');
        if (userData) {
            this.currentUser = JSON.parse(userData);
            this.currentUser.userType = 'shipper';
            document.body.classList.add('user-shipper');
        } else {
            const forwarderData = localStorage.getItem('forwarderUser');
            if (forwarderData) {
                this.currentUser = JSON.parse(forwarderData);
                this.currentUser.userType = 'forwarder';
                document.body.classList.add('user-forwarder');
            }
        }
        
        if (!this.currentUser) {
            window.location.href = '../ai_studio_code_F2.html';
            return false;
        }
        
        this.updateProfile();
        this.updateNavigation();
        return true;
    },
    
    /**
     * Update profile display
     */
    updateProfile() {
        const avatar = document.getElementById('profileAvatar');
        const company = document.getElementById('profileCompany');
        const email = document.getElementById('profileEmail');
        const badge = document.getElementById('userTypeBadge');
        
        if (avatar) avatar.textContent = (this.currentUser.company || 'U').charAt(0);
        if (company) company.textContent = this.currentUser.company || 'User';
        if (email) email.textContent = this.currentUser.email || '';
        if (badge) {
            badge.textContent = this.currentUser.userType === 'shipper' ? '화주' : '포워더';
            if (this.currentUser.userType === 'forwarder') {
                badge.classList.add('forwarder');
            }
        }
        
        // Update settings form
        const settingsCompany = document.getElementById('settingsCompany');
        const settingsEmail = document.getElementById('settingsEmail');
        const settingsName = document.getElementById('settingsName');
        const settingsPhone = document.getElementById('settingsPhone');
        
        if (settingsCompany) settingsCompany.value = this.currentUser.company || '';
        if (settingsEmail) settingsEmail.value = this.currentUser.email || '';
        if (settingsName) settingsName.value = this.currentUser.name || '';
        if (settingsPhone) settingsPhone.value = this.currentUser.phone || '';
    },
    
    /**
     * Update navigation based on user type
     */
    updateNavigation() {
        const mainNav = document.getElementById('mainNav');
        if (!mainNav) return;
        
        // 로그인 여부, 사용자 타입에 관계없이 동일한 네비게이션
        mainNav.innerHTML = `
            <ul>
                <li><a href="quotation.html">Quotation</a></li>
                <li><a href="shipper-bidding.html">My Quotations</a></li>
                <li><a href="bidding-list.html">Bidding</a></li>
                <li><a href="market-data.html">Market Data</a></li>
                <li><a href="news-intelligence.html">News Intel</a></li>
                <li><a href="../ai_studio_code_F2.html#tools">Tools</a></li>
                <li><a href="report-insight.html">Report & Insight</a></li>
            </ul>
        `;
    },
    
    /**
     * Setup sidebar navigation
     */
    setupNavigation() {
        const navItems = document.querySelectorAll('.mypage-nav .nav-item');
        
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const section = item.dataset.section;
                this.switchSection(section);
            });
        });
        
        // Handle URL hash
        const hash = window.location.hash.replace('#', '');
        if (hash) {
            this.switchSection(hash);
        }
    },
    
    /**
     * Switch to a section
     */
    switchSection(section) {
        // Update nav
        document.querySelectorAll('.mypage-nav .nav-item').forEach(item => {
            item.classList.toggle('active', item.dataset.section === section);
        });
        
        // Update content
        document.querySelectorAll('.content-section').forEach(sec => {
            sec.classList.toggle('active', sec.id === `section-${section}`);
        });
        
        this.currentSection = section;
        window.location.hash = section;
        
        // Load section data
        this.loadSectionData(section);
    },
    
    /**
     * Load section data
     */
    loadSectionData(section) {
        switch (section) {
            case 'dashboard':
                this.loadDashboard();
                break;
            case 'history':
                this.loadHistory();
                break;
            case 'settlements':
                this.loadSettlements();
                break;
            case 'disputes':
                this.loadDisputes();
                break;
            case 'ratings':
                this.loadRatings();
                break;
            case 'messages':
                this.loadMessages();
                break;
            case 'favorites':
                this.loadFavorites();
                break;
            case 'templates':
                this.loadTemplates();
                break;
        }
    },
    
    /**
     * Load dashboard data
     */
    async loadDashboard() {
        await this.loadDashboardStats();
        await this.loadRecentActivity();
    },
    
    /**
     * Load dashboard statistics
     */
    async loadDashboardStats() {
        const statsGrid = document.getElementById('dashboardStats');
        if (!statsGrid) return;
        
        try {
            if (this.currentUser.userType === 'shipper') {
                // Load shipper stats
                const response = await fetch(
                    `${this.API_BASE}/shipper/biddings/stats?customer_id=${this.currentUser.id}`
                );
                const stats = await response.json();
                
                statsGrid.innerHTML = `
                    <div class="stat-card">
                        <div class="stat-value">${stats.total_biddings || 0}</div>
                        <div class="stat-label">총 비딩</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${stats.open_biddings || 0}</div>
                        <div class="stat-label">진행 중</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${stats.awarded_biddings || 0}</div>
                        <div class="stat-label">선정 완료</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${stats.total_bids_received || 0}</div>
                        <div class="stat-label">받은 입찰</div>
                    </div>
                `;
            } else {
                // Load forwarder stats
                const response = await fetch(
                    `${this.API_BASE}/analytics/forwarder/summary?forwarder_id=${this.currentUser.id}`
                );
                const stats = await response.json();
                
                statsGrid.innerHTML = `
                    <div class="stat-card">
                        <div class="stat-value">${stats.total_bids || 0}</div>
                        <div class="stat-label">총 입찰</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${stats.awarded_count || 0}</div>
                        <div class="stat-label">낙찰</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${stats.award_rate?.toFixed(1) || 0}%</div>
                        <div class="stat-label">낙찰률</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">₩${this.formatNumber(stats.total_revenue_krw || 0)}</div>
                        <div class="stat-label">총 수익</div>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error loading stats:', error);
            statsGrid.innerHTML = `
                <div class="stat-card">
                    <div class="stat-value">-</div>
                    <div class="stat-label">데이터 로딩 중</div>
                </div>
            `;
        }
    },
    
    /**
     * Load recent activity
     */
    async loadRecentActivity() {
        const activityList = document.getElementById('recentActivity');
        if (!activityList) return;
        
        try {
            // For now, show recent notifications as activity
            const response = await fetch(
                `${this.API_BASE}/notifications?user_type=${this.currentUser.userType === 'shipper' ? 'customer' : 'forwarder'}&user_id=${this.currentUser.id}&limit=5`
            );
            const data = await response.json();
            
            if (!data.notifications || data.notifications.length === 0) {
                activityList.innerHTML = `
                    <div class="empty-state">
                        <p>최근 활동이 없습니다.</p>
                    </div>
                `;
                return;
            }
            
            activityList.innerHTML = data.notifications.map(notif => `
                <div class="activity-item">
                    <div class="activity-icon ${notif.notification_type?.includes('bid') ? 'bid' : notif.notification_type?.includes('contract') ? 'contract' : 'message'}">
                        <i class="fas ${this.getActivityIcon(notif.notification_type)}"></i>
                    </div>
                    <div class="activity-content">
                        <div class="activity-title">${notif.title}</div>
                        <div class="activity-time">${this.formatDate(notif.created_at)}</div>
                    </div>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error loading activity:', error);
            activityList.innerHTML = `
                <div class="empty-state">
                    <p>활동 내역을 불러올 수 없습니다.</p>
                </div>
            `;
        }
    },
    
    /**
     * Get activity icon based on type
     */
    getActivityIcon(type) {
        if (type?.includes('bid')) return 'fa-gavel';
        if (type?.includes('contract')) return 'fa-file-contract';
        if (type?.includes('message')) return 'fa-envelope';
        if (type?.includes('shipment')) return 'fa-shipping-fast';
        return 'fa-bell';
    },
    
    /**
     * Load history
     */
    async loadHistory() {
        const historyList = document.getElementById('historyList');
        if (!historyList) return;
        
        historyList.innerHTML = `
            <div class="loading-state">
                <i class="fas fa-spinner fa-spin"></i>
            </div>
        `;
        
        try {
            const response = await fetch(
                `${this.API_BASE}/contracts?user_type=${this.currentUser.userType}&user_id=${this.currentUser.id}&limit=20`
            );
            const data = await response.json();
            
            if (!data.data || data.data.length === 0) {
                historyList.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-history"></i>
                        <p>이력이 없습니다.</p>
                    </div>
                `;
                return;
            }
            
            historyList.innerHTML = data.data.map(item => `
                <div class="history-item">
                    <div>
                        <strong>${item.contract_no}</strong>
                        <span style="color: var(--text-secondary); margin-left: 0.5rem;">${item.pol} → ${item.pod}</span>
                    </div>
                    <div style="text-align: right;">
                        <div>₩${this.formatNumber(item.total_amount_krw)}</div>
                        <span class="status-badge ${item.status}">${this.getStatusLabel(item.status)}</span>
                    </div>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error loading history:', error);
            historyList.innerHTML = `
                <div class="empty-state">
                    <p>이력을 불러올 수 없습니다.</p>
                </div>
            `;
        }
    },
    
    /**
     * Load settlements
     */
    async loadSettlements() {
        const settlementList = document.getElementById('settlementList');
        if (!settlementList) return;
        
        try {
            // Load summary
            const summaryResponse = await fetch(
                `${this.API_BASE}/settlements/summary?user_type=${this.currentUser.userType}&user_id=${this.currentUser.id}`
            );
            const summary = await summaryResponse.json();
            
            document.getElementById('settlementCompleted').textContent = `₩${this.formatNumber(summary.total_completed || 0)}`;
            document.getElementById('settlementPending').textContent = `₩${this.formatNumber(summary.total_pending || 0)}`;
            
            // Load list
            const response = await fetch(
                `${this.API_BASE}/settlements?user_type=${this.currentUser.userType}&user_id=${this.currentUser.id}&limit=20`
            );
            const data = await response.json();
            
            if (!data.data || data.data.length === 0) {
                settlementList.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-credit-card"></i>
                        <p>정산 내역이 없습니다.</p>
                    </div>
                `;
                return;
            }
            
            settlementList.innerHTML = data.data.map(item => {
                const serviceFee = item.service_fee || Math.round(item.total_amount_krw * 0.02);
                const feeRate = item.total_amount_krw > 0 ? ((serviceFee / item.total_amount_krw) * 100).toFixed(1) : 2;
                
                return `
                <div class="settlement-item" data-id="${item.id}">
                    <div class="settlement-main">
                        <div class="settlement-header">
                            <strong>${item.settlement_no}</strong>
                            <span class="contract-ref">${item.contract_no}</span>
                        </div>
                        <div class="settlement-details">
                            <div class="detail-row">
                                <span class="label">계약 금액</span>
                                <span class="value">₩${this.formatNumber(item.total_amount_krw)}</span>
                            </div>
                            <div class="detail-row fee-row">
                                <span class="label">플랫폼 수수료 (${feeRate}%)</span>
                                <span class="value fee">-₩${this.formatNumber(serviceFee)}</span>
                            </div>
                            <div class="detail-row net-row">
                                <span class="label">정산 금액</span>
                                <span class="value net">₩${this.formatNumber(item.net_amount)}</span>
                            </div>
                        </div>
                    </div>
                    <div class="settlement-actions">
                        <span class="status-badge ${item.status}">${this.getSettlementStatusLabel(item.status)}</span>
                        ${this.currentUser.userType === 'shipper' && ['pending', 'requested'].includes(item.status) ? `
                            <button class="btn-sm btn-outline" onclick="MyPage.openDisputeFileModal(${item.id}, '${item.settlement_no}', ${item.total_amount_krw})">
                                <i class="fas fa-gavel"></i> 분쟁
                            </button>
                        ` : ''}
                    </div>
                </div>
            `}).join('');
        } catch (error) {
            console.error('Error loading settlements:', error);
            settlementList.innerHTML = `
                <div class="empty-state">
                    <p>정산 내역을 불러올 수 없습니다.</p>
                </div>
            `;
        }
    },
    
    /**
     * Load ratings
     */
    async loadRatings() {
        const ratingList = document.getElementById('ratingList');
        const ratingOverview = document.getElementById('ratingOverview');
        if (!ratingList) return;
        
        if (this.currentUser.userType === 'forwarder') {
            try {
                const response = await fetch(
                    `${this.API_BASE}/ratings/forwarder/${this.currentUser.id}/stats`
                );
                const stats = await response.json();
                
                const avgRating = stats.average_rating || 3.0;
                const totalRatings = stats.total_ratings || 0;
                
                ratingOverview.innerHTML = `
                    <div class="rating-score">
                        <div class="big-score">${avgRating.toFixed(1)}</div>
                        <div class="stars">${this.renderStars(avgRating)}</div>
                        <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">
                            ${totalRatings}개의 평가
                        </div>
                    </div>
                    <div class="rating-breakdown">
                        ${[5,4,3,2,1].map(score => `
                            <div class="breakdown-row">
                                <span class="label">${score}점</span>
                                <div class="breakdown-bar">
                                    <div class="fill" style="width: ${this.getRatingPercent(score, stats)}%"></div>
                                </div>
                                <span class="count">${this.getRatingCount(score, stats)}</span>
                            </div>
                        `).join('')}
                    </div>
                `;
            } catch (error) {
                console.error('Error loading ratings:', error);
            }
        } else {
            ratingOverview.innerHTML = `
                <div style="text-align: center; width: 100%;">
                    <p>내가 남긴 평가 목록</p>
                </div>
            `;
        }
        
        // Placeholder for rating list
        ratingList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-star"></i>
                <p>평점 내역이 없습니다.</p>
            </div>
        `;
    },
    
    /**
     * Load messages
     */
    async loadMessages() {
        const messageThreads = document.getElementById('messageThreads');
        if (!messageThreads) return;
        
        try {
            const response = await fetch(
                `${this.API_BASE}/messages/unread?user_type=${this.currentUser.userType}&user_id=${this.currentUser.id}`
            );
            const data = await response.json();
            
            // Update unread badge
            const badge = document.getElementById('unreadBadge');
            if (badge) {
                if (data.total_unread > 0) {
                    badge.textContent = data.total_unread;
                    badge.style.display = 'inline';
                } else {
                    badge.style.display = 'none';
                }
            }
            
            if (!data.threads || data.threads.length === 0) {
                messageThreads.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-envelope"></i>
                        <p>메시지가 없습니다.</p>
                    </div>
                `;
                return;
            }
            
            messageThreads.innerHTML = data.threads.map(thread => `
                <div class="message-thread ${thread.unread_count > 0 ? 'unread' : ''}">
                    <div class="thread-header">
                        <span class="thread-title">
                            ${thread.bidding_no}
                            ${thread.unread_count > 0 ? `<span class="unread-count">${thread.unread_count}</span>` : ''}
                        </span>
                        <span class="thread-time">${this.formatDate(thread.messages[0]?.created_at)}</span>
                    </div>
                    <div class="thread-route">${thread.pol} → ${thread.pod}</div>
                    <div class="thread-preview">${thread.messages[0]?.content || ''}</div>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error loading messages:', error);
            messageThreads.innerHTML = `
                <div class="empty-state">
                    <p>메시지를 불러올 수 없습니다.</p>
                </div>
            `;
        }
    },
    
    /**
     * Load favorites
     */
    async loadFavorites() {
        const favoritesList = document.getElementById('favoritesList');
        if (!favoritesList || this.currentUser.userType !== 'shipper') return;
        
        try {
            const response = await fetch(
                `${this.API_BASE}/shipper/favorite-routes?customer_id=${this.currentUser.id}`
            );
            const data = await response.json();
            
            if (!data.data || data.data.length === 0) {
                favoritesList.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-heart"></i>
                        <p>즐겨찾기 구간이 없습니다.</p>
                    </div>
                `;
                return;
            }
            
            favoritesList.innerHTML = data.data.map(route => `
                <div class="favorite-item">
                    <div class="favorite-route">
                        <span class="route-badge">${route.pol}</span>
                        <i class="fas fa-arrow-right" style="color: var(--text-secondary);"></i>
                        <span class="route-badge">${route.pod}</span>
                        ${route.alias ? `<span style="color: var(--text-secondary); margin-left: 1rem;">${route.alias}</span>` : ''}
                    </div>
                    <button class="delete-btn" onclick="MyPage.deleteFavorite(${route.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error loading favorites:', error);
        }
    },
    
    /**
     * Load templates
     */
    async loadTemplates() {
        const templatesList = document.getElementById('templatesList');
        if (!templatesList || this.currentUser.userType !== 'forwarder') return;
        
        try {
            const response = await fetch(
                `${this.API_BASE}/forwarder/bid-templates?forwarder_id=${this.currentUser.id}`
            );
            const data = await response.json();
            
            if (!data.data || data.data.length === 0) {
                templatesList.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-file-alt"></i>
                        <p>입찰 템플릿이 없습니다.</p>
                    </div>
                `;
                return;
            }
            
            templatesList.innerHTML = data.data.map(template => `
                <div class="template-item">
                    <div class="template-info">
                        <div>
                            <div class="template-name">${template.name}</div>
                            <div class="template-details">
                                ${template.pol || '*'} → ${template.pod || '*'}
                                ${template.shipping_type ? ` | ${template.shipping_type.toUpperCase()}` : ''}
                            </div>
                        </div>
                    </div>
                    <button class="delete-btn" onclick="MyPage.deleteTemplate(${template.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error loading templates:', error);
        }
    },
    
    /**
     * Open add favorite modal
     */
    openAddFavoriteModal() {
        document.getElementById('addFavoriteModal').classList.add('active');
    },
    
    /**
     * Close add favorite modal
     */
    closeAddFavoriteModal() {
        document.getElementById('addFavoriteModal').classList.remove('active');
        document.getElementById('favoritePol').value = '';
        document.getElementById('favoritePod').value = '';
        document.getElementById('favoriteType').value = '';
        document.getElementById('favoriteAlias').value = '';
    },
    
    /**
     * Add favorite route
     */
    async addFavoriteRoute() {
        const pol = document.getElementById('favoritePol').value.trim();
        const pod = document.getElementById('favoritePod').value.trim();
        const shippingType = document.getElementById('favoriteType').value;
        const alias = document.getElementById('favoriteAlias').value.trim();
        
        if (!pol || !pod) {
            alert('출발지와 도착지를 입력해주세요.');
            return;
        }
        
        try {
            const response = await fetch(`${this.API_BASE}/shipper/favorite-routes`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    customer_id: this.currentUser.id,
                    pol,
                    pod,
                    shipping_type: shippingType || null,
                    alias: alias || null
                })
            });
            
            if (response.ok) {
                this.closeAddFavoriteModal();
                this.loadFavorites();
            } else {
                const error = await response.json();
                alert(error.detail || '구간 추가에 실패했습니다.');
            }
        } catch (error) {
            console.error('Error adding favorite:', error);
            alert('구간 추가 중 오류가 발생했습니다.');
        }
    },
    
    /**
     * Delete favorite route
     */
    async deleteFavorite(routeId) {
        if (!confirm('이 즐겨찾기 구간을 삭제하시겠습니까?')) return;
        
        try {
            await fetch(
                `${this.API_BASE}/shipper/favorite-routes/${routeId}?customer_id=${this.currentUser.id}`,
                { method: 'DELETE' }
            );
            this.loadFavorites();
        } catch (error) {
            console.error('Error deleting favorite:', error);
        }
    },
    
    /**
     * Open add template modal
     */
    openAddTemplateModal() {
        document.getElementById('addTemplateModal').classList.add('active');
    },
    
    /**
     * Close add template modal
     */
    closeAddTemplateModal() {
        document.getElementById('addTemplateModal').classList.remove('active');
        // Clear form
        document.getElementById('templateName').value = '';
        document.getElementById('templateType').value = '';
        document.getElementById('templatePol').value = '';
        document.getElementById('templatePod').value = '';
        document.getElementById('templateFreight').value = '';
        document.getElementById('templateLocal').value = '';
        document.getElementById('templateOther').value = '';
        document.getElementById('templateTransit').value = '';
        document.getElementById('templateCarrier').value = '';
        document.getElementById('templateRemark').value = '';
    },
    
    /**
     * Add template
     */
    async addTemplate() {
        const name = document.getElementById('templateName').value.trim();
        
        if (!name) {
            alert('템플릿 이름을 입력해주세요.');
            return;
        }
        
        try {
            const response = await fetch(`${this.API_BASE}/forwarder/bid-templates`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    forwarder_id: this.currentUser.id,
                    name,
                    pol: document.getElementById('templatePol').value.trim() || null,
                    pod: document.getElementById('templatePod').value.trim() || null,
                    shipping_type: document.getElementById('templateType').value || null,
                    base_freight: parseFloat(document.getElementById('templateFreight').value) || null,
                    base_local: parseFloat(document.getElementById('templateLocal').value) || null,
                    base_other: parseFloat(document.getElementById('templateOther').value) || null,
                    transit_time: document.getElementById('templateTransit').value.trim() || null,
                    carrier: document.getElementById('templateCarrier').value.trim() || null,
                    default_remark: document.getElementById('templateRemark').value.trim() || null
                })
            });
            
            if (response.ok) {
                this.closeAddTemplateModal();
                this.loadTemplates();
            } else {
                const error = await response.json();
                alert(error.detail || '템플릿 추가에 실패했습니다.');
            }
        } catch (error) {
            console.error('Error adding template:', error);
            alert('템플릿 추가 중 오류가 발생했습니다.');
        }
    },
    
    /**
     * Delete template
     */
    async deleteTemplate(templateId) {
        if (!confirm('이 템플릿을 삭제하시겠습니까?')) return;
        
        try {
            await fetch(
                `${this.API_BASE}/forwarder/bid-templates/${templateId}?forwarder_id=${this.currentUser.id}`,
                { method: 'DELETE' }
            );
            this.loadTemplates();
        } catch (error) {
            console.error('Error deleting template:', error);
        }
    },
    
    /**
     * Change password
     */
    async changePassword() {
        const current = document.getElementById('currentPassword').value;
        const newPass = document.getElementById('newPassword').value;
        const confirm = document.getElementById('confirmPassword').value;
        
        if (!current || !newPass || !confirm) {
            alert('모든 필드를 입력해주세요.');
            return;
        }
        
        if (newPass !== confirm) {
            alert('새 비밀번호가 일치하지 않습니다.');
            return;
        }
        
        if (newPass.length < 6) {
            alert('비밀번호는 6자 이상이어야 합니다.');
            return;
        }
        
        alert('비밀번호 변경 기능은 준비 중입니다.');
    },
    
    /**
     * Save settings
     */
    saveSettings() {
        alert('설정이 저장되었습니다.');
    },
    
    /**
     * Logout
     */
    logout() {
        localStorage.removeItem('shipperUser');
        localStorage.removeItem('forwarderUser');
        window.location.href = '../ai_studio_code_F2.html';
    },
    
    /**
     * Utility functions
     */
    formatNumber(num) {
        if (!num) return '0';
        return Math.round(num).toLocaleString('ko-KR');
    },
    
    formatDate(dateStr) {
        if (!dateStr) return '-';
        const date = new Date(dateStr);
        return date.toLocaleDateString('ko-KR', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },
    
    getStatusLabel(status) {
        const labels = {
            pending: '대기',
            confirmed: '확정',
            active: '진행중',
            completed: '완료',
            cancelled: '취소'
        };
        return labels[status] || status;
    },
    
    getSettlementStatusLabel(status) {
        const labels = {
            pending: '대기',
            requested: '요청됨',
            processing: '처리중',
            completed: '완료',
            disputed: '분쟁'
        };
        return labels[status] || status;
    },
    
    renderStars(rating) {
        const fullStars = Math.floor(rating);
        const halfStar = rating % 1 >= 0.5;
        let stars = '';
        
        for (let i = 0; i < fullStars; i++) {
            stars += '<i class="fas fa-star"></i>';
        }
        if (halfStar) {
            stars += '<i class="fas fa-star-half-alt"></i>';
        }
        for (let i = fullStars + (halfStar ? 1 : 0); i < 5; i++) {
            stars += '<i class="far fa-star"></i>';
        }
        
        return stars;
    },
    
    getRatingPercent(score, stats) {
        // Placeholder - would need actual breakdown data
        return score === 5 ? 60 : score === 4 ? 25 : score === 3 ? 10 : 5;
    },
    
    getRatingCount(score, stats) {
        // Placeholder - would need actual breakdown data
        return Math.floor((stats.total_ratings || 0) * (score === 5 ? 0.6 : score === 4 ? 0.25 : 0.1));
    },
    
    // ==========================================
    // DISPUTE FUNCTIONS
    // ==========================================
    
    /**
     * Load disputes list
     */
    async loadDisputes() {
        const container = document.getElementById('disputeList');
        const statusFilter = document.getElementById('disputeStatusFilter')?.value || 'all';
        
        if (!container) return;
        
        container.innerHTML = '<div class="loading-state"><i class="fas fa-spinner fa-spin"></i></div>';
        
        try {
            const params = new URLSearchParams({ status: statusFilter, limit: 20 });
            
            if (this.currentUser.userType === 'shipper') {
                params.append('customer_id', this.currentUser.id);
            } else {
                params.append('forwarder_id', this.currentUser.id);
            }
            
            const response = await fetch(`${this.API_BASE}/settlements/disputes?${params}`);
            
            if (!response.ok) {
                throw new Error('Failed to load disputes');
            }
            
            const data = await response.json();
            this.renderDisputes(data.disputes || []);
            
        } catch (error) {
            console.error('Error loading disputes:', error);
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-exclamation-circle"></i>
                    <p>분쟁 내역을 불러올 수 없습니다.</p>
                </div>
            `;
        }
    },
    
    /**
     * Render disputes list
     */
    renderDisputes(disputes) {
        const container = document.getElementById('disputeList');
        if (!container) return;
        
        if (disputes.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-check-circle"></i>
                    <p>분쟁 내역이 없습니다.</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = disputes.map(dispute => `
            <div class="dispute-item status-${dispute.status}">
                <div class="dispute-header">
                    <div class="dispute-title">${dispute.settlement_no}</div>
                    <span class="dispute-status ${dispute.status}">${this.getDisputeStatusLabel(dispute.status)}</span>
                </div>
                <div class="dispute-info">
                    <div class="dispute-info-item">
                        <span class="label">상대방</span>
                        <span class="value">${this.currentUser.userType === 'shipper' ? dispute.forwarder_name : dispute.customer_name}</span>
                    </div>
                    <div class="dispute-info-item">
                        <span class="label">금액</span>
                        <span class="value">₩${this.formatNumber(dispute.original_amount_krw)}</span>
                    </div>
                    <div class="dispute-info-item">
                        <span class="label">분쟁 제기일</span>
                        <span class="value">${this.formatDate(dispute.disputed_at)}</span>
                    </div>
                    <div class="dispute-info-item">
                        <span class="label">응답</span>
                        <span class="value">${dispute.has_response ? '✓ 응답 완료' : '⏳ 대기 중'}</span>
                    </div>
                </div>
                <div class="dispute-reason-preview">${dispute.dispute_reason || ''}</div>
                <div class="dispute-actions-row">
                    <button class="btn-secondary btn-sm" onclick="MyPage.openDisputeDetail(${dispute.settlement_id})">
                        <i class="fas fa-eye"></i> 상세 보기
                    </button>
                    ${this.currentUser.userType === 'forwarder' && dispute.status === 'disputed' && !dispute.has_response ? `
                        <button class="btn-warning btn-sm" onclick="MyPage.openDisputeResponseModal(${dispute.settlement_id})">
                            <i class="fas fa-reply"></i> 응답하기
                        </button>
                    ` : ''}
                </div>
            </div>
        `).join('');
    },
    
    getDisputeStatusLabel(status) {
        const labels = {
            disputed: '진행 중',
            completed: '해결됨',
            cancelled: '취소됨'
        };
        return labels[status] || status;
    },
    
    /**
     * Open dispute file modal (화주용)
     */
    openDisputeFileModal(settlementId, settlementNo, amount) {
        document.getElementById('disputeSettlementId').value = settlementId;
        document.getElementById('disputeSettlementNo').value = settlementNo;
        document.getElementById('disputeAmount').value = `₩${this.formatNumber(amount)}`;
        document.getElementById('disputeReasonType').value = '';
        document.getElementById('disputeReason').value = '';
        document.getElementById('disputeEvidence').value = '';
        
        document.getElementById('disputeFileModal').classList.add('active');
    },
    
    closeDisputeFileModal() {
        document.getElementById('disputeFileModal').classList.remove('active');
    },
    
    handleDisputeReasonChange() {
        const type = document.getElementById('disputeReasonType').value;
        const templates = {
            damage: '화물 파손이 발생했습니다.\n- 파손 위치: \n- 파손 정도: \n- 예상 피해 금액: ',
            loss: '화물이 분실되었습니다.\n- 분실 품목: \n- 수량: \n- 예상 피해 금액: ',
            delay: '배송이 지연되었습니다.\n- 예정 배송일: \n- 실제 배송일: \n- 지연으로 인한 손해: ',
            overcharge: '과다 청구가 발생했습니다.\n- 계약 금액: \n- 청구 금액: \n- 차액: ',
            quality: '서비스 품질에 문제가 있었습니다.\n- 문제 내용: \n',
            other: ''
        };
        
        if (templates[type]) {
            document.getElementById('disputeReason').value = templates[type];
        }
    },
    
    /**
     * Submit dispute (화주)
     */
    async submitDispute() {
        const settlementId = document.getElementById('disputeSettlementId').value;
        const reason = document.getElementById('disputeReason').value.trim();
        const evidence = document.getElementById('disputeEvidence').value.trim();
        
        if (!reason) {
            alert('분쟁 사유를 입력해주세요.');
            return;
        }
        
        if (!confirm('분쟁을 제기하시겠습니까?\n\n포워더에게 알림이 발송되며, 7일 내 응답이 없으면 귀하의 주장이 자동 인정됩니다.')) {
            return;
        }
        
        try {
            const params = new URLSearchParams({
                customer_id: this.currentUser.id,
                reason: reason,
                evidence: evidence || ''
            });
            
            const response = await fetch(`${this.API_BASE}/settlement/${settlementId}/dispute?${params}`, {
                method: 'POST'
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to file dispute');
            }
            
            const result = await response.json();
            alert(result.message);
            this.closeDisputeFileModal();
            this.loadSettlements();
            this.loadDisputes();
            
        } catch (error) {
            console.error('Error filing dispute:', error);
            alert('분쟁 제기에 실패했습니다: ' + error.message);
        }
    },
    
    /**
     * Open dispute response modal (포워더용)
     */
    async openDisputeResponseModal(settlementId) {
        try {
            const response = await fetch(`${this.API_BASE}/settlement/${settlementId}/dispute-detail`);
            if (!response.ok) throw new Error('Failed to load dispute detail');
            
            const data = await response.json();
            
            document.getElementById('responseSettlementId').value = settlementId;
            document.getElementById('responseSettlementNo').textContent = data.settlement_no;
            document.getElementById('responseOriginalAmount').textContent = `₩${this.formatNumber(data.original_amount_krw)}`;
            document.getElementById('responseDisputedAt').textContent = this.formatDate(data.disputed_at);
            document.getElementById('responseDisputeReason').textContent = data.dispute_reason;
            document.getElementById('responseDeadline').textContent = `${data.auto_resolve_in_days || 0}일`;
            
            document.getElementById('disputeResponseText').value = '';
            document.getElementById('proposedAmount').value = '';
            
            document.getElementById('disputeResponseModal').classList.add('active');
            
        } catch (error) {
            console.error('Error:', error);
            alert('분쟁 정보를 불러올 수 없습니다.');
        }
    },
    
    closeDisputeResponseModal() {
        document.getElementById('disputeResponseModal').classList.remove('active');
    },
    
    /**
     * Submit dispute response (포워더)
     */
    async submitDisputeResponse() {
        const settlementId = document.getElementById('responseSettlementId').value;
        const responseText = document.getElementById('disputeResponseText').value.trim();
        const proposedAmount = document.getElementById('proposedAmount').value;
        
        if (!responseText) {
            alert('응답 내용을 입력해주세요.');
            return;
        }
        
        if (!confirm('응답을 제출하시겠습니까?')) {
            return;
        }
        
        try {
            const params = new URLSearchParams({
                forwarder_id: this.currentUser.id,
                response: responseText
            });
            
            if (proposedAmount) {
                params.append('proposed_amount', proposedAmount);
            }
            
            const response = await fetch(`${this.API_BASE}/settlement/${settlementId}/respond?${params}`, {
                method: 'POST'
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to submit response');
            }
            
            const result = await response.json();
            alert(result.message);
            this.closeDisputeResponseModal();
            this.loadDisputes();
            
        } catch (error) {
            console.error('Error submitting response:', error);
            alert('응답 제출에 실패했습니다: ' + error.message);
        }
    },
    
    /**
     * Open dispute detail modal
     */
    async openDisputeDetail(settlementId) {
        try {
            const response = await fetch(`${this.API_BASE}/settlement/${settlementId}/dispute-detail`);
            if (!response.ok) throw new Error('Failed to load dispute detail');
            
            const data = await response.json();
            this.renderDisputeDetail(data);
            
            document.getElementById('disputeDetailModal').classList.add('active');
            
        } catch (error) {
            console.error('Error:', error);
            alert('분쟁 정보를 불러올 수 없습니다.');
        }
    },
    
    closeDisputeDetailModal() {
        document.getElementById('disputeDetailModal').classList.remove('active');
    },
    
    /**
     * Render dispute detail
     */
    renderDisputeDetail(data) {
        // Timeline
        const timeline = document.getElementById('disputeTimeline');
        timeline.innerHTML = `
            <div class="timeline-item completed">
                <div class="time">${this.formatDate(data.created_at)}</div>
                <div class="title">정산 생성</div>
                <div class="content">정산 금액: ₩${this.formatNumber(data.original_amount_krw)}</div>
            </div>
            ${data.disputed_at ? `
                <div class="timeline-item warning">
                    <div class="time">${this.formatDate(data.disputed_at)}</div>
                    <div class="title">분쟁 제기</div>
                    <div class="content">${data.customer_name}님이 분쟁을 제기했습니다.</div>
                </div>
            ` : ''}
            ${data.forwarder_response_at ? `
                <div class="timeline-item">
                    <div class="time">${this.formatDate(data.forwarder_response_at)}</div>
                    <div class="title">포워더 응답</div>
                    <div class="content">${data.forwarder_name}님이 응답했습니다.</div>
                </div>
            ` : ''}
            ${data.resolved_at ? `
                <div class="timeline-item completed">
                    <div class="time">${this.formatDate(data.resolved_at)}</div>
                    <div class="title">분쟁 해결</div>
                    <div class="content">${this.getResolutionTypeLabel(data.resolution_type)}</div>
                </div>
            ` : ''}
        `;
        
        // Detail content
        const content = document.getElementById('disputeDetailContent');
        content.innerHTML = `
            <div class="dispute-section">
                <h4><i class="fas fa-info-circle"></i> 기본 정보</h4>
                <div class="dispute-detail-view">
                    <div class="detail-row">
                        <span class="label">정산 번호</span>
                        <span class="value">${data.settlement_no}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">상태</span>
                        <span class="value">${this.getDisputeStatusLabel(data.status)}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">화주</span>
                        <span class="value">${data.customer_name}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">포워더</span>
                        <span class="value">${data.forwarder_name}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">원래 금액</span>
                        <span class="value">₩${this.formatNumber(data.original_amount_krw)}</span>
                    </div>
                    ${data.adjusted_amount_krw ? `
                        <div class="detail-row">
                            <span class="label">조정 금액</span>
                            <span class="value" style="color: var(--accent-primary)">₩${this.formatNumber(data.adjusted_amount_krw)}</span>
                        </div>
                    ` : ''}
                </div>
            </div>
            
            ${data.dispute_reason ? `
                <div class="dispute-section">
                    <h4><i class="fas fa-exclamation-triangle"></i> 분쟁 사유</h4>
                    <div class="content-box">${data.dispute_reason.replace(/\n/g, '<br>')}</div>
                    ${data.dispute_evidence ? `
                        <div class="content-box" style="margin-top: 0.5rem; font-size: 0.8rem; color: var(--text-secondary)">
                            <strong>증빙:</strong> ${data.dispute_evidence}
                        </div>
                    ` : ''}
                </div>
            ` : ''}
            
            ${data.forwarder_response ? `
                <div class="dispute-section">
                    <h4><i class="fas fa-reply"></i> 포워더 응답</h4>
                    <div class="content-box">${data.forwarder_response.replace(/\n/g, '<br>')}</div>
                </div>
            ` : ''}
            
            ${data.resolution_note ? `
                <div class="dispute-section">
                    <h4><i class="fas fa-check-circle"></i> 해결 내용</h4>
                    <div class="content-box">
                        <strong>${this.getResolutionTypeLabel(data.resolution_type)}</strong><br><br>
                        ${data.resolution_note.replace(/\n/g, '<br>')}
                    </div>
                </div>
            ` : ''}
        `;
    },
    
    getResolutionTypeLabel(type) {
        const labels = {
            agreement: '양측 합의',
            mediation: '관리자 중재',
            auto_customer_favor: '자동 처리 (포워더 무응답)',
            cancel: '취소'
        };
        return labels[type] || type;
    },
    
    /**
     * Add dispute button to settlement item
     */
    addDisputeButtonToSettlement(settlementId, settlementNo, amount, status) {
        if (this.currentUser.userType === 'shipper' && ['pending', 'requested'].includes(status)) {
            return `
                <button class="btn-danger btn-sm" onclick="MyPage.openDisputeFileModal(${settlementId}, '${settlementNo}', ${amount})">
                    <i class="fas fa-gavel"></i> 분쟁 제기
                </button>
            `;
        }
        return '';
    }
};
