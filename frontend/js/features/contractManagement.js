/**
 * Contract Management Module
 * 계약 관리 기능
 */

const ContractManagement = {
    API_BASE: 'http://localhost:8001/api',
    currentPage: 1,
    limit: 10,
    currentUser: null,
    currentContract: null,
    
    /**
     * Initialize the module
     */
    init() {
        this.checkAuth();
        this.loadContracts();
    },
    
    /**
     * Check authentication status
     */
    checkAuth() {
        const userData = localStorage.getItem('shipperUser');
        if (userData) {
            this.currentUser = JSON.parse(userData);
            this.currentUser.userType = 'shipper';
        } else {
            const forwarderData = localStorage.getItem('forwarderUser');
            if (forwarderData) {
                this.currentUser = JSON.parse(forwarderData);
                this.currentUser.userType = 'forwarder';
            }
        }
        
        if (!this.currentUser) {
            document.getElementById('contractList').innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-lock"></i>
                    <p>계약 관리 기능을 사용하려면 로그인이 필요합니다.</p>
                </div>
            `;
            return false;
        }
        
        return true;
    },
    
    /**
     * Load contracts from API
     */
    async loadContracts() {
        if (!this.currentUser) return;
        
        const listContainer = document.getElementById('contractList');
        listContainer.innerHTML = `
            <div class="loading-state">
                <i class="fas fa-spinner fa-spin"></i>
                <p>계약 목록을 불러오는 중...</p>
            </div>
        `;
        
        try {
            const status = document.getElementById('filterStatus').value;
            const search = document.getElementById('filterSearch').value;
            
            let url = `${this.API_BASE}/contracts?user_type=${this.currentUser.userType}&user_id=${this.currentUser.id}&page=${this.currentPage}&limit=${this.limit}`;
            
            if (status) {
                url += `&status=${status}`;
            }
            
            const response = await fetch(url);
            const data = await response.json();
            
            this.renderContracts(data);
            this.renderPagination(data.total);
            this.loadStats();
            
        } catch (error) {
            console.error('Error loading contracts:', error);
            listContainer.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>계약 목록을 불러오는 중 오류가 발생했습니다.</p>
                </div>
            `;
        }
    },
    
    /**
     * Render contracts list
     */
    renderContracts(data) {
        const listContainer = document.getElementById('contractList');
        
        if (!data.data || data.data.length === 0) {
            listContainer.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-file-contract"></i>
                    <p>계약 내역이 없습니다.</p>
                </div>
            `;
            return;
        }
        
        listContainer.innerHTML = data.data.map(contract => this.renderContractCard(contract)).join('');
    },
    
    /**
     * Render single contract card
     */
    renderContractCard(contract) {
        const statusLabels = {
            pending: '확정 대기',
            confirmed: '계약 확정',
            active: '배송 진행',
            completed: '완료',
            cancelled: '취소됨'
        };
        
        const shippingTypeIcons = {
            ocean: 'fa-ship',
            air: 'fa-plane',
            truck: 'fa-truck'
        };
        
        return `
            <div class="contract-card" onclick="ContractManagement.openDetail(${contract.id})">
                <div class="contract-main">
                    <div class="contract-number">
                        <div class="contract-no">${contract.contract_no}</div>
                        <div class="bidding-no">${contract.bidding_no}</div>
                    </div>
                    <div class="contract-route">
                        <div class="route-point">
                            <div class="code">${contract.pol}</div>
                            <div class="type">${contract.shipping_type.toUpperCase()}</div>
                        </div>
                        <div class="route-arrow">
                            <i class="fas ${shippingTypeIcons[contract.shipping_type] || 'fa-arrow-right'}"></i>
                        </div>
                        <div class="route-point">
                            <div class="code">${contract.pod}</div>
                        </div>
                    </div>
                    <div class="contract-amount">
                        <div class="amount">₩${this.formatNumber(contract.total_amount_krw)}</div>
                        <div class="label">계약 금액</div>
                    </div>
                </div>
                <div class="contract-actions">
                    <span class="contract-status ${contract.status}">${statusLabels[contract.status] || contract.status}</span>
                    <div class="confirm-badges">
                        <span class="confirm-badge ${contract.shipper_confirmed ? 'confirmed' : 'pending'}" title="화주 확정">
                            <i class="fas ${contract.shipper_confirmed ? 'fa-check' : 'fa-clock'}"></i>
                        </span>
                        <span class="confirm-badge ${contract.forwarder_confirmed ? 'confirmed' : 'pending'}" title="운송사 확정">
                            <i class="fas ${contract.forwarder_confirmed ? 'fa-check' : 'fa-clock'}"></i>
                        </span>
                    </div>
                </div>
            </div>
        `;
    },
    
    /**
     * Load contract statistics
     */
    async loadStats() {
        if (!this.currentUser) return;
        
        try {
            const statuses = ['pending', 'confirmed', 'active', 'completed'];
            
            for (const status of statuses) {
                const response = await fetch(
                    `${this.API_BASE}/contracts?user_type=${this.currentUser.userType}&user_id=${this.currentUser.id}&status=${status}&limit=1`
                );
                const data = await response.json();
                
                const elementId = `stat${status.charAt(0).toUpperCase() + status.slice(1)}`;
                const element = document.getElementById(elementId);
                if (element) {
                    element.textContent = data.total || 0;
                }
            }
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    },
    
    /**
     * Open contract detail modal
     */
    async openDetail(contractId) {
        try {
            const response = await fetch(`${this.API_BASE}/contract/${contractId}`);
            const contract = await response.json();
            
            this.currentContract = contract;
            this.renderDetailModal(contract);
            
            document.getElementById('contractDetailModal').classList.add('active');
            
        } catch (error) {
            console.error('Error loading contract detail:', error);
            alert('계약 정보를 불러오는 중 오류가 발생했습니다.');
        }
    },
    
    /**
     * Render contract detail modal content
     */
    renderDetailModal(contract) {
        const statusLabels = {
            pending: '확정 대기',
            confirmed: '계약 확정',
            active: '배송 진행',
            completed: '완료',
            cancelled: '취소됨'
        };
        
        const content = document.getElementById('contractDetailContent');
        content.innerHTML = `
            <div class="contract-detail-header">
                <div class="contract-detail-info">
                    <h3>${contract.contract_no}</h3>
                    <div class="contract-detail-route">
                        <span>${contract.pol}</span>
                        <i class="fas fa-long-arrow-alt-right"></i>
                        <span>${contract.pod}</span>
                    </div>
                    <div style="margin-top: 0.5rem; color: var(--text-secondary); font-size: 0.875rem;">
                        Bidding: ${contract.bidding_no || '-'}
                    </div>
                </div>
                <div class="contract-detail-status">
                    <span class="contract-status ${contract.status}">
                        ${statusLabels[contract.status] || contract.status}
                    </span>
                    <div class="contract-confirm-status">
                        <div class="confirm-item ${contract.shipper_confirmed ? 'confirmed' : 'pending'}">
                            <i class="fas ${contract.shipper_confirmed ? 'fa-check' : 'fa-clock'}"></i>
                            <span>화주 ${contract.shipper_confirmed ? '확정' : '대기'}</span>
                        </div>
                        <div class="confirm-item ${contract.forwarder_confirmed ? 'confirmed' : 'pending'}">
                            <i class="fas ${contract.forwarder_confirmed ? 'fa-check' : 'fa-clock'}"></i>
                            <span>운송사 ${contract.forwarder_confirmed ? '확정' : '대기'}</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="contract-detail-grid">
                <div class="detail-section">
                    <h4>계약 금액</h4>
                    <div class="detail-row">
                        <span class="label">총 금액</span>
                        <span class="value highlight">₩${this.formatNumber(contract.total_amount_krw)}</span>
                    </div>
                    ${contract.freight_charge ? `
                    <div class="detail-row">
                        <span class="label">운임</span>
                        <span class="value">₩${this.formatNumber(contract.freight_charge)}</span>
                    </div>
                    ` : ''}
                    ${contract.local_charge ? `
                    <div class="detail-row">
                        <span class="label">로컬비</span>
                        <span class="value">₩${this.formatNumber(contract.local_charge)}</span>
                    </div>
                    ` : ''}
                    ${contract.other_charge ? `
                    <div class="detail-row">
                        <span class="label">기타비용</span>
                        <span class="value">₩${this.formatNumber(contract.other_charge)}</span>
                    </div>
                    ` : ''}
                </div>
                
                <div class="detail-section">
                    <h4>운송 정보</h4>
                    <div class="detail-row">
                        <span class="label">운송 유형</span>
                        <span class="value">${(contract.shipping_type || '').toUpperCase()}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">운송사</span>
                        <span class="value">${contract.carrier || '-'}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">소요 시간</span>
                        <span class="value">${contract.transit_time || '-'}</span>
                    </div>
                </div>
                
                <div class="detail-section">
                    <h4>거래 당사자</h4>
                    <div class="detail-row">
                        <span class="label">화주</span>
                        <span class="value">${contract.customer_company || '-'}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">운송사</span>
                        <span class="value">${contract.forwarder_company || '-'}</span>
                    </div>
                </div>
                
                <div class="detail-section">
                    <h4>일정</h4>
                    <div class="detail-row">
                        <span class="label">계약 생성</span>
                        <span class="value">${this.formatDate(contract.created_at)}</span>
                    </div>
                    ${contract.confirmed_at ? `
                    <div class="detail-row">
                        <span class="label">계약 확정</span>
                        <span class="value">${this.formatDate(contract.confirmed_at)}</span>
                    </div>
                    ` : ''}
                    ${contract.cancelled_at ? `
                    <div class="detail-row">
                        <span class="label">취소일</span>
                        <span class="value">${this.formatDate(contract.cancelled_at)}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">취소 사유</span>
                        <span class="value">${contract.cancel_reason || '-'}</span>
                    </div>
                    ` : ''}
                </div>
            </div>
        `;
        
        // Render action buttons based on status and user type
        this.renderModalActions(contract);
    },
    
    /**
     * Render modal action buttons
     */
    renderModalActions(contract) {
        const footer = document.getElementById('contractModalFooter');
        let buttons = '';
        
        if (contract.status === 'pending') {
            // Check if current user needs to confirm
            const isShipper = this.currentUser.userType === 'shipper';
            const needsConfirm = (isShipper && !contract.shipper_confirmed) || 
                                (!isShipper && !contract.forwarder_confirmed);
            
            if (needsConfirm) {
                buttons += `
                    <button class="btn-danger" onclick="ContractManagement.openCancelModal()">
                        <i class="fas fa-times"></i> 계약 취소
                    </button>
                    <button class="btn-primary" onclick="ContractManagement.confirmContract()">
                        <i class="fas fa-check"></i> 계약 확정
                    </button>
                `;
            } else {
                buttons += `
                    <button class="btn-danger" onclick="ContractManagement.openCancelModal()">
                        <i class="fas fa-times"></i> 계약 취소
                    </button>
                    <span style="color: var(--text-secondary); font-size: 0.875rem;">
                        상대방의 확정을 기다리는 중...
                    </span>
                `;
            }
        } else if (contract.status === 'confirmed' || contract.status === 'active') {
            buttons += `
                <button class="btn-primary" onclick="location.href='shipment-tracking.html'">
                    <i class="fas fa-shipping-fast"></i> 배송 추적
                </button>
            `;
        }
        
        buttons = `<button class="btn-secondary" onclick="ContractManagement.closeModal()">닫기</button>` + buttons;
        footer.innerHTML = buttons;
    },
    
    /**
     * Confirm contract
     */
    async confirmContract() {
        if (!this.currentContract) return;
        
        try {
            const response = await fetch(
                `${this.API_BASE}/contract/${this.currentContract.id}/confirm`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_type: this.currentUser.userType,
                        user_id: this.currentUser.id
                    })
                }
            );
            
            const result = await response.json();
            
            if (result.success) {
                alert('계약이 확정되었습니다.');
                this.closeModal();
                this.loadContracts();
            } else {
                alert(result.detail || '계약 확정에 실패했습니다.');
            }
            
        } catch (error) {
            console.error('Error confirming contract:', error);
            alert('계약 확정 중 오류가 발생했습니다.');
        }
    },
    
    /**
     * Open cancel reason modal
     */
    openCancelModal() {
        document.getElementById('cancelReasonModal').classList.add('active');
    },
    
    /**
     * Close cancel reason modal
     */
    closeCancelModal() {
        document.getElementById('cancelReasonModal').classList.remove('active');
        document.getElementById('cancelReason').value = '';
    },
    
    /**
     * Confirm contract cancellation
     */
    async confirmCancel() {
        if (!this.currentContract) return;
        
        const reason = document.getElementById('cancelReason').value;
        
        try {
            const response = await fetch(
                `${this.API_BASE}/contract/${this.currentContract.id}/cancel`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_type: this.currentUser.userType,
                        user_id: this.currentUser.id,
                        reason: reason
                    })
                }
            );
            
            const result = await response.json();
            
            if (result.success) {
                alert('계약이 취소되었습니다.');
                this.closeCancelModal();
                this.closeModal();
                this.loadContracts();
            } else {
                alert(result.detail || '계약 취소에 실패했습니다.');
            }
            
        } catch (error) {
            console.error('Error cancelling contract:', error);
            alert('계약 취소 중 오류가 발생했습니다.');
        }
    },
    
    /**
     * Close detail modal
     */
    closeModal() {
        document.getElementById('contractDetailModal').classList.remove('active');
        this.currentContract = null;
    },
    
    /**
     * Apply filters
     */
    applyFilters() {
        this.currentPage = 1;
        this.loadContracts();
    },
    
    /**
     * Render pagination
     */
    renderPagination(total) {
        const totalPages = Math.ceil(total / this.limit);
        const pagination = document.getElementById('pagination');
        
        if (totalPages <= 1) {
            pagination.innerHTML = '';
            return;
        }
        
        let html = '';
        
        html += `<button onclick="ContractManagement.goToPage(${this.currentPage - 1})" 
                        ${this.currentPage === 1 ? 'disabled' : ''}>
                    <i class="fas fa-chevron-left"></i>
                </button>`;
        
        for (let i = 1; i <= totalPages; i++) {
            if (i === 1 || i === totalPages || (i >= this.currentPage - 2 && i <= this.currentPage + 2)) {
                html += `<button onclick="ContractManagement.goToPage(${i})" 
                                class="${i === this.currentPage ? 'active' : ''}">${i}</button>`;
            } else if (i === this.currentPage - 3 || i === this.currentPage + 3) {
                html += `<button disabled>...</button>`;
            }
        }
        
        html += `<button onclick="ContractManagement.goToPage(${this.currentPage + 1})" 
                        ${this.currentPage === totalPages ? 'disabled' : ''}>
                    <i class="fas fa-chevron-right"></i>
                </button>`;
        
        pagination.innerHTML = html;
    },
    
    /**
     * Go to specific page
     */
    goToPage(page) {
        this.currentPage = page;
        this.loadContracts();
    },
    
    /**
     * Format number with comma separators
     */
    formatNumber(num) {
        if (!num) return '0';
        return Math.round(num).toLocaleString('ko-KR');
    },
    
    /**
     * Format date
     */
    formatDate(dateStr) {
        if (!dateStr) return '-';
        const date = new Date(dateStr);
        return date.toLocaleDateString('ko-KR', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
};
