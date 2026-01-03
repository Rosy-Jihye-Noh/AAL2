/**
 * Shipment Tracking Module
 * 배송 추적 기능
 */

const ShipmentTracking = {
    API_BASE: 'http://localhost:8001/api',
    currentPage: 1,
    limit: 10,
    currentUser: null,
    currentShipment: null,
    
    statusLabels: {
        booked: '예약됨',
        picked_up: '픽업 완료',
        in_transit: '운송 중',
        arrived_port: '항구 도착',
        customs: '통관 중',
        out_for_delivery: '배송 출발',
        delivered: '배송 완료',
        completed: '완료'
    },
    
    statusIcons: {
        booked: 'fa-calendar-check',
        picked_up: 'fa-box',
        in_transit: 'fa-ship',
        arrived_port: 'fa-anchor',
        customs: 'fa-clipboard-list',
        out_for_delivery: 'fa-truck',
        delivered: 'fa-home',
        completed: 'fa-check-circle'
    },
    
    /**
     * Initialize the module
     */
    init() {
        this.checkAuth();
        this.loadShipments();
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
            document.getElementById('shipmentList').innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-lock"></i>
                    <p>배송 추적 기능을 사용하려면 로그인이 필요합니다.</p>
                </div>
            `;
            return false;
        }
        
        return true;
    },
    
    /**
     * Load shipments from API
     */
    async loadShipments() {
        if (!this.currentUser) return;
        
        const listContainer = document.getElementById('shipmentList');
        listContainer.innerHTML = `
            <div class="loading-state">
                <i class="fas fa-spinner fa-spin"></i>
                <p>배송 목록을 불러오는 중...</p>
            </div>
        `;
        
        try {
            const status = document.getElementById('filterStatus').value;
            
            let url = `${this.API_BASE}/shipments?user_type=${this.currentUser.userType}&user_id=${this.currentUser.id}&page=${this.currentPage}&limit=${this.limit}`;
            
            if (status) {
                url += `&status=${status}`;
            }
            
            const response = await fetch(url);
            const data = await response.json();
            
            this.renderShipments(data);
            this.renderPagination(data.total);
            this.loadStats();
            
        } catch (error) {
            console.error('Error loading shipments:', error);
            listContainer.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>배송 목록을 불러오는 중 오류가 발생했습니다.</p>
                </div>
            `;
        }
    },
    
    /**
     * Render shipments list
     */
    renderShipments(data) {
        const listContainer = document.getElementById('shipmentList');
        
        if (!data.data || data.data.length === 0) {
            listContainer.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-shipping-fast"></i>
                    <p>배송 내역이 없습니다.</p>
                </div>
            `;
            return;
        }
        
        listContainer.innerHTML = data.data.map(shipment => this.renderShipmentCard(shipment)).join('');
    },
    
    /**
     * Render single shipment card
     */
    renderShipmentCard(shipment) {
        const isShipper = this.currentUser.userType === 'shipper';
        const showConfirmBtn = isShipper && shipment.current_status === 'delivered' && !shipment.delivery_confirmed;
        
        return `
            <div class="shipment-card" onclick="ShipmentTracking.openDetail(${shipment.id})">
                <div class="shipment-status-indicator ${shipment.current_status}">
                    <i class="fas ${this.statusIcons[shipment.current_status] || 'fa-box'}"></i>
                </div>
                <div class="shipment-main">
                    <div class="shipment-numbers">
                        <span class="shipment-no">${shipment.shipment_no}</span>
                        <span class="contract-ref">${shipment.contract_no} / ${shipment.bidding_no}</span>
                    </div>
                    <div class="shipment-route">
                        <span>${shipment.pol}</span>
                        <i class="fas fa-long-arrow-alt-right"></i>
                        <span>${shipment.pod}</span>
                    </div>
                    ${shipment.estimated_delivery ? `
                    <div class="shipment-eta">
                        예상 도착: ${this.formatDate(shipment.estimated_delivery)}
                    </div>
                    ` : ''}
                </div>
                <div class="shipment-actions">
                    <span class="status-badge ${shipment.current_status}">
                        ${this.statusLabels[shipment.current_status] || shipment.current_status}
                    </span>
                    ${showConfirmBtn ? `
                    <button class="confirm-btn" onclick="event.stopPropagation(); ShipmentTracking.confirmDelivery(${shipment.id})">
                        <i class="fas fa-check"></i> 배송 확인
                    </button>
                    ` : ''}
                </div>
            </div>
        `;
    },
    
    /**
     * Load shipment statistics
     */
    async loadStats() {
        if (!this.currentUser) return;
        
        try {
            // In transit count
            const transitResponse = await fetch(
                `${this.API_BASE}/shipments?user_type=${this.currentUser.userType}&user_id=${this.currentUser.id}&status=in_transit&limit=1`
            );
            const transitData = await transitResponse.json();
            document.getElementById('statInTransit').textContent = transitData.total || 0;
            
            // Delivered count
            const deliveredResponse = await fetch(
                `${this.API_BASE}/shipments?user_type=${this.currentUser.userType}&user_id=${this.currentUser.id}&status=delivered&limit=1`
            );
            const deliveredData = await deliveredResponse.json();
            document.getElementById('statDelivered').textContent = deliveredData.total || 0;
            
            // Pending confirm (delivered but not confirmed)
            document.getElementById('statPendingConfirm').textContent = deliveredData.total || 0;
            
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    },
    
    /**
     * Search shipment
     */
    searchShipment() {
        const searchValue = document.getElementById('trackingSearch').value.trim();
        if (!searchValue) return;
        
        // For now, just filter the current list
        // In production, this would call a search API
        alert(`배송번호 "${searchValue}" 검색 기능은 준비 중입니다.`);
    },
    
    /**
     * Open shipment detail modal
     */
    async openDetail(shipmentId) {
        try {
            const response = await fetch(`${this.API_BASE}/shipment/${shipmentId}`);
            const shipment = await response.json();
            
            this.currentShipment = shipment;
            this.renderDetailModal(shipment);
            
            document.getElementById('shipmentDetailModal').classList.add('active');
            
        } catch (error) {
            console.error('Error loading shipment detail:', error);
            alert('배송 정보를 불러오는 중 오류가 발생했습니다.');
        }
    },
    
    /**
     * Render shipment detail modal content
     */
    renderDetailModal(shipment) {
        // Header
        document.getElementById('modalShipmentNo').textContent = shipment.shipment_no;
        document.getElementById('modalRoute').textContent = `${shipment.pol} → ${shipment.pod}`;
        document.getElementById('modalStatus').innerHTML = `
            <span class="status-badge ${shipment.current_status}">
                ${this.statusLabels[shipment.current_status] || shipment.current_status}
            </span>
        `;
        
        // Timeline
        this.renderTimeline(shipment);
        
        // Details Grid
        this.renderDetailsGrid(shipment);
        
        // Actions
        this.renderModalActions(shipment);
    },
    
    /**
     * Render tracking timeline
     */
    renderTimeline(shipment) {
        const timeline = document.getElementById('trackingTimeline');
        const history = shipment.tracking_history || [];
        
        if (history.length === 0) {
            timeline.innerHTML = `
                <div class="timeline-item active">
                    <div class="timeline-dot"></div>
                    <div class="timeline-content">
                        <div class="timeline-status">${this.statusLabels[shipment.current_status]}</div>
                        <div class="timeline-time">${this.formatDate(shipment.created_at)}</div>
                    </div>
                </div>
            `;
            return;
        }
        
        timeline.innerHTML = history.map((item, index) => `
            <div class="timeline-item ${index === 0 ? 'active' : 'completed'}">
                <div class="timeline-dot"></div>
                <div class="timeline-content">
                    <div class="timeline-status">
                        <i class="fas ${this.statusIcons[item.status] || 'fa-circle'}"></i>
                        ${this.statusLabels[item.status] || item.status}
                    </div>
                    ${item.location ? `<div class="timeline-location"><i class="fas fa-map-marker-alt"></i> ${item.location}</div>` : ''}
                    <div class="timeline-time">${this.formatDate(item.created_at)}</div>
                    ${item.remark ? `<div class="timeline-remark">${item.remark}</div>` : ''}
                </div>
            </div>
        `).join('');
    },
    
    /**
     * Render details grid
     */
    renderDetailsGrid(shipment) {
        const grid = document.getElementById('shipmentDetailsGrid');
        
        grid.innerHTML = `
            <div class="detail-card">
                <h4>배송 정보</h4>
                <div class="detail-row">
                    <span class="label">배송번호</span>
                    <span class="value">${shipment.shipment_no}</span>
                </div>
                <div class="detail-row">
                    <span class="label">계약번호</span>
                    <span class="value">${shipment.contract_no || '-'}</span>
                </div>
                <div class="detail-row">
                    <span class="label">B/L 번호</span>
                    <span class="value">${shipment.bl_no || '-'}</span>
                </div>
                <div class="detail-row">
                    <span class="label">선박/항공편</span>
                    <span class="value">${shipment.vessel_flight || '-'}</span>
                </div>
            </div>
            
            <div class="detail-card">
                <h4>일정</h4>
                <div class="detail-row">
                    <span class="label">픽업 예정</span>
                    <span class="value">${this.formatDate(shipment.estimated_pickup) || '-'}</span>
                </div>
                <div class="detail-row">
                    <span class="label">실제 픽업</span>
                    <span class="value">${this.formatDate(shipment.actual_pickup) || '-'}</span>
                </div>
                <div class="detail-row">
                    <span class="label">도착 예정</span>
                    <span class="value">${this.formatDate(shipment.estimated_delivery) || '-'}</span>
                </div>
                <div class="detail-row">
                    <span class="label">실제 도착</span>
                    <span class="value">${this.formatDate(shipment.actual_delivery) || '-'}</span>
                </div>
            </div>
        `;
    },
    
    /**
     * Render modal action buttons
     */
    renderModalActions(shipment) {
        const footer = document.getElementById('shipmentModalFooter');
        const isShipper = this.currentUser.userType === 'shipper';
        const isForwarder = this.currentUser.userType === 'forwarder';
        
        let buttons = `<button class="btn-secondary" onclick="ShipmentTracking.closeModal()">닫기</button>`;
        
        if (isShipper && shipment.current_status === 'delivered' && !shipment.delivery_confirmed) {
            buttons += `
                <button class="btn-primary" onclick="ShipmentTracking.confirmDelivery(${shipment.id})">
                    <i class="fas fa-check"></i> 배송 완료 확인
                </button>
            `;
        }
        
        if (isForwarder && !['delivered', 'completed'].includes(shipment.current_status)) {
            buttons += `
                <button class="btn-primary" onclick="ShipmentTracking.openStatusModal()">
                    <i class="fas fa-edit"></i> 상태 업데이트
                </button>
            `;
        }
        
        footer.innerHTML = buttons;
    },
    
    /**
     * Confirm delivery (shipper)
     */
    async confirmDelivery(shipmentId) {
        if (!confirm('배송 완료를 확인하시겠습니까?\n확인 후에는 평점을 등록할 수 있습니다.')) return;
        
        try {
            const response = await fetch(
                `${this.API_BASE}/shipment/${shipmentId}/confirm-delivery`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        customer_id: this.currentUser.id
                    })
                }
            );
            
            const result = await response.json();
            
            if (result.success) {
                alert('배송 완료가 확인되었습니다.\n정산이 자동으로 생성됩니다.');
                this.closeModal();
                this.loadShipments();
            } else {
                alert(result.detail || '배송 확인에 실패했습니다.');
            }
            
        } catch (error) {
            console.error('Error confirming delivery:', error);
            alert('배송 확인 중 오류가 발생했습니다.');
        }
    },
    
    /**
     * Open status update modal (forwarder)
     */
    openStatusModal() {
        document.getElementById('updateStatusModal').classList.add('active');
        
        // Pre-select next logical status
        const currentStatus = this.currentShipment.current_status;
        const statusOrder = ['booked', 'picked_up', 'in_transit', 'arrived_port', 'customs', 'out_for_delivery', 'delivered'];
        const currentIndex = statusOrder.indexOf(currentStatus);
        
        if (currentIndex >= 0 && currentIndex < statusOrder.length - 1) {
            document.getElementById('newStatus').value = statusOrder[currentIndex + 1];
        }
    },
    
    /**
     * Close status update modal
     */
    closeStatusModal() {
        document.getElementById('updateStatusModal').classList.remove('active');
        document.getElementById('statusLocation').value = '';
        document.getElementById('statusRemark').value = '';
    },
    
    /**
     * Submit status update (forwarder)
     */
    async submitStatusUpdate() {
        const newStatus = document.getElementById('newStatus').value;
        const location = document.getElementById('statusLocation').value;
        const remark = document.getElementById('statusRemark').value;
        
        try {
            const response = await fetch(
                `${this.API_BASE}/shipment/${this.currentShipment.id}/status`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        status: newStatus,
                        location: location,
                        remark: remark,
                        forwarder_id: this.currentUser.id
                    })
                }
            );
            
            const result = await response.json();
            
            if (result.success) {
                alert('배송 상태가 업데이트되었습니다.');
                this.closeStatusModal();
                this.openDetail(this.currentShipment.id);
                this.loadShipments();
            } else {
                alert(result.detail || '상태 업데이트에 실패했습니다.');
            }
            
        } catch (error) {
            console.error('Error updating status:', error);
            alert('상태 업데이트 중 오류가 발생했습니다.');
        }
    },
    
    /**
     * Close detail modal
     */
    closeModal() {
        document.getElementById('shipmentDetailModal').classList.remove('active');
        this.currentShipment = null;
    },
    
    /**
     * Apply filters
     */
    applyFilters() {
        this.currentPage = 1;
        this.loadShipments();
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
        
        html += `<button onclick="ShipmentTracking.goToPage(${this.currentPage - 1})" 
                        ${this.currentPage === 1 ? 'disabled' : ''}>
                    <i class="fas fa-chevron-left"></i>
                </button>`;
        
        for (let i = 1; i <= totalPages; i++) {
            if (i === 1 || i === totalPages || (i >= this.currentPage - 2 && i <= this.currentPage + 2)) {
                html += `<button onclick="ShipmentTracking.goToPage(${i})" 
                                class="${i === this.currentPage ? 'active' : ''}">${i}</button>`;
            } else if (i === this.currentPage - 3 || i === this.currentPage + 3) {
                html += `<button disabled>...</button>`;
            }
        }
        
        html += `<button onclick="ShipmentTracking.goToPage(${this.currentPage + 1})" 
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
        this.loadShipments();
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
