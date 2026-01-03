/**
 * Onboarding Module
 * 사용자 온보딩 가이드 시스템
 */

const Onboarding = {
    // 저장 키
    STORAGE_KEY: 'aal_onboarding',
    
    // 현재 상태
    currentSlide: 0,
    currentStep: 0,
    isGuideActive: false,
    
    // 슬라이드 데이터 (화주용)
    shipperSlides: [
        {
            icon: 'fas fa-handshake',
            title: 'AAL Platform에 오신 것을 환영합니다!',
            description: '전세계 화주와 포워더를 연결하는 스마트 물류 매칭 플랫폼입니다. 최적의 운송사를 찾고, 투명한 가격으로 거래하세요.',
            features: null
        },
        {
            icon: 'fas fa-file-invoice-dollar',
            title: '간편한 견적 요청',
            description: '몇 가지 정보만 입력하면 여러 포워더로부터 경쟁 입찰을 받을 수 있습니다.',
            features: [
                { icon: 'fas fa-globe', title: '전세계 운송', desc: '해상, 항공, 육상 모두 지원' },
                { icon: 'fas fa-users', title: '다중 입찰', desc: '여러 포워더의 견적을 한눈에 비교' },
                { icon: 'fas fa-star', title: '평점 시스템', desc: '검증된 포워더 선택 가능' }
            ]
        },
        {
            icon: 'fas fa-truck-loading',
            title: '배송 추적 & 관리',
            description: '계약부터 배송 완료까지 모든 과정을 실시간으로 확인하고 관리하세요.',
            features: [
                { icon: 'fas fa-map-marker-alt', title: '실시간 추적', desc: '8단계 상태 업데이트' },
                { icon: 'fas fa-file-contract', title: '계약 관리', desc: '온라인 계약 확인 및 관리' },
                { icon: 'fas fa-calculator', title: '투명한 정산', desc: '명확한 수수료 정책' }
            ]
        },
        {
            icon: 'fas fa-rocket',
            title: '지금 시작해보세요!',
            description: '첫 견적 요청을 등록하고 최적의 물류 파트너를 찾아보세요.',
            features: null
        }
    ],
    
    // 슬라이드 데이터 (포워더용)
    forwarderSlides: [
        {
            icon: 'fas fa-handshake',
            title: 'AAL Platform에 오신 것을 환영합니다!',
            description: '전세계 화주들의 물류 요청에 입찰하고 비즈니스를 확장하세요.',
            features: null
        },
        {
            icon: 'fas fa-gavel',
            title: '입찰 참여',
            description: '다양한 화주들의 견적 요청에 입찰하고 새로운 고객을 확보하세요.',
            features: [
                { icon: 'fas fa-list', title: '입찰 목록', desc: '조건에 맞는 견적 요청 확인' },
                { icon: 'fas fa-bolt', title: '빠른 입찰', desc: '템플릿으로 신속하게 입찰' },
                { icon: 'fas fa-bookmark', title: '북마크', desc: '관심 있는 입찰 저장' }
            ]
        },
        {
            icon: 'fas fa-chart-line',
            title: '비즈니스 성장',
            description: '평점 시스템과 분석 도구로 경쟁력을 높이세요.',
            features: [
                { icon: 'fas fa-star', title: '평점 관리', desc: '좋은 서비스로 평점 향상' },
                { icon: 'fas fa-chart-bar', title: '통계 분석', desc: '입찰 성공률, 매출 분석' },
                { icon: 'fas fa-medal', title: '신뢰도 구축', desc: '검증된 포워더로 인정받기' }
            ]
        },
        {
            icon: 'fas fa-rocket',
            title: '지금 시작해보세요!',
            description: '입찰 목록을 확인하고 첫 입찰에 참여해보세요.',
            features: null
        }
    ],
    
    // 가이드 스텝 (화주용)
    shipperGuideSteps: [
        {
            target: '[data-guide="quote-btn"]',
            title: '견적 요청',
            content: '이 버튼을 클릭하면 새로운 견적 요청을 등록할 수 있습니다.',
            position: 'bottom'
        },
        {
            target: '[data-guide="bidding-list"]',
            title: '입찰 현황',
            content: '등록한 견적에 대한 입찰 현황을 확인하세요.',
            position: 'bottom'
        },
        {
            target: '[data-guide="contract-menu"]',
            title: '계약 관리',
            content: '체결된 계약을 확인하고 관리할 수 있습니다.',
            position: 'bottom'
        }
    ],
    
    // 가이드 스텝 (포워더용)
    forwarderGuideSteps: [
        {
            target: '[data-guide="bidding-list"]',
            title: '입찰 목록',
            content: '현재 진행 중인 입찰 목록을 확인하세요.',
            position: 'bottom'
        },
        {
            target: '[data-guide="my-bids"]',
            title: '내 입찰',
            content: '제출한 입찰 내역을 확인할 수 있습니다.',
            position: 'bottom'
        },
        {
            target: '[data-guide="analytics"]',
            title: '분석',
            content: '입찰 성공률과 매출 통계를 확인하세요.',
            position: 'bottom'
        }
    ],
    
    // 체크리스트 (화주용)
    shipperChecklist: [
        { id: 'profile', text: '프로필 완성하기', desc: '회사 정보 입력', completed: false },
        { id: 'first_quote', text: '첫 견적 요청 등록', desc: '운송 요청 생성', completed: false },
        { id: 'review_bids', text: '입찰 검토하기', desc: '포워더 입찰 확인', completed: false },
        { id: 'first_contract', text: '첫 계약 체결', desc: '운송사 선정 및 계약', completed: false },
        { id: 'first_rating', text: '첫 평가 남기기', desc: '서비스 평가', completed: false }
    ],
    
    // 체크리스트 (포워더용)
    forwarderChecklist: [
        { id: 'profile', text: '프로필 완성하기', desc: '회사 정보 입력', completed: false },
        { id: 'first_bid', text: '첫 입찰 참여', desc: '견적 제출', completed: false },
        { id: 'create_template', text: '입찰 템플릿 만들기', desc: '빠른 입찰을 위한 템플릿', completed: false },
        { id: 'first_win', text: '첫 낙찰 받기', desc: '입찰 성공', completed: false },
        { id: 'first_delivery', text: '첫 배송 완료', desc: '운송 완료 및 정산', completed: false }
    ],
    
    /**
     * 초기화
     */
    init() {
        const userData = localStorage.getItem('shipperUser') || localStorage.getItem('forwarderUser');
        if (!userData) return;
        
        const user = JSON.parse(userData);
        this.userType = localStorage.getItem('shipperUser') ? 'shipper' : 'forwarder';
        
        // 온보딩 상태 로드
        this.loadState();
        
        // 첫 방문 시 환영 모달 표시
        if (!this.state.welcomed) {
            this.showWelcomeModal();
        } else if (!this.state.guideCompleted) {
            // 가이드 미완료 시 체크리스트 표시
            this.showChecklist();
        }
    },
    
    /**
     * 상태 로드
     */
    loadState() {
        const saved = localStorage.getItem(this.STORAGE_KEY);
        if (saved) {
            this.state = JSON.parse(saved);
        } else {
            this.state = {
                welcomed: false,
                guideCompleted: false,
                checklist: {}
            };
        }
    },
    
    /**
     * 상태 저장
     */
    saveState() {
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(this.state));
    },
    
    /**
     * 환영 모달 표시
     */
    showWelcomeModal() {
        const slides = this.userType === 'shipper' ? this.shipperSlides : this.forwarderSlides;
        this.currentSlide = 0;
        
        const modal = document.createElement('div');
        modal.className = 'onboarding-modal';
        modal.id = 'onboardingModal';
        
        modal.innerHTML = `
            <div class="onboarding-container">
                <div class="onboarding-slides" id="onboardingSlides">
                    ${slides.map((slide, index) => this.renderSlide(slide, index)).join('')}
                </div>
                <div class="onboarding-footer">
                    <div class="onboarding-dots">
                        ${slides.map((_, i) => `<div class="onboarding-dot${i === 0 ? ' active' : ''}" data-slide="${i}"></div>`).join('')}
                    </div>
                    <div class="onboarding-buttons">
                        <button class="onboarding-btn onboarding-btn-skip" onclick="Onboarding.skipOnboarding()">건너뛰기</button>
                        <button class="onboarding-btn onboarding-btn-prev" onclick="Onboarding.prevSlide()" style="display: none;">이전</button>
                        <button class="onboarding-btn onboarding-btn-next" onclick="Onboarding.nextSlide()">다음</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // 애니메이션을 위해 약간의 딜레이
        requestAnimationFrame(() => {
            modal.classList.add('active');
        });
        
        // 닷 클릭 이벤트
        modal.querySelectorAll('.onboarding-dot').forEach(dot => {
            dot.addEventListener('click', () => {
                this.goToSlide(parseInt(dot.dataset.slide));
            });
        });
    },
    
    /**
     * 슬라이드 렌더링
     */
    renderSlide(slide, index) {
        let featuresHTML = '';
        if (slide.features) {
            featuresHTML = `
                <div class="onboarding-features">
                    ${slide.features.map(f => `
                        <div class="onboarding-feature">
                            <div class="onboarding-feature-icon"><i class="${f.icon}"></i></div>
                            <div class="onboarding-feature-text">
                                <div class="onboarding-feature-title">${f.title}</div>
                                <div class="onboarding-feature-desc">${f.desc}</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        }
        
        return `
            <div class="onboarding-slide${index === 0 ? ' active' : ''}" data-slide="${index}">
                <div class="onboarding-icon"><i class="${slide.icon}"></i></div>
                <h2 class="onboarding-title">${slide.title}</h2>
                <p class="onboarding-description">${slide.description}</p>
                ${featuresHTML}
            </div>
        `;
    },
    
    /**
     * 다음 슬라이드
     */
    nextSlide() {
        const slides = this.userType === 'shipper' ? this.shipperSlides : this.forwarderSlides;
        
        if (this.currentSlide < slides.length - 1) {
            this.goToSlide(this.currentSlide + 1);
        } else {
            this.completeWelcome();
        }
    },
    
    /**
     * 이전 슬라이드
     */
    prevSlide() {
        if (this.currentSlide > 0) {
            this.goToSlide(this.currentSlide - 1);
        }
    },
    
    /**
     * 특정 슬라이드로 이동
     */
    goToSlide(index) {
        const slides = this.userType === 'shipper' ? this.shipperSlides : this.forwarderSlides;
        this.currentSlide = index;
        
        // 슬라이드 업데이트
        document.querySelectorAll('.onboarding-slide').forEach((slide, i) => {
            slide.classList.toggle('active', i === index);
        });
        
        // 닷 업데이트
        document.querySelectorAll('.onboarding-dot').forEach((dot, i) => {
            dot.classList.toggle('active', i === index);
        });
        
        // 버튼 업데이트
        const prevBtn = document.querySelector('.onboarding-btn-prev');
        const nextBtn = document.querySelector('.onboarding-btn-next');
        
        if (prevBtn) prevBtn.style.display = index > 0 ? 'block' : 'none';
        if (nextBtn) nextBtn.textContent = index === slides.length - 1 ? '시작하기' : '다음';
    },
    
    /**
     * 환영 완료
     */
    completeWelcome() {
        this.state.welcomed = true;
        this.saveState();
        
        this.closeWelcomeModal();
        
        // 체크리스트 표시
        setTimeout(() => {
            this.showChecklist();
        }, 500);
    },
    
    /**
     * 온보딩 건너뛰기
     */
    skipOnboarding() {
        this.state.welcomed = true;
        this.state.guideCompleted = true;
        this.saveState();
        
        this.closeWelcomeModal();
    },
    
    /**
     * 환영 모달 닫기
     */
    closeWelcomeModal() {
        const modal = document.getElementById('onboardingModal');
        if (modal) {
            modal.classList.remove('active');
            setTimeout(() => modal.remove(), 300);
        }
    },
    
    /**
     * 체크리스트 표시
     */
    showChecklist() {
        const checklist = this.userType === 'shipper' ? this.shipperChecklist : this.forwarderChecklist;
        
        // 저장된 완료 상태 적용
        checklist.forEach(item => {
            item.completed = this.state.checklist[item.id] || false;
        });
        
        const completedCount = checklist.filter(i => i.completed).length;
        const progress = Math.round((completedCount / checklist.length) * 100);
        
        // 모두 완료 시 표시 안함
        if (completedCount === checklist.length) {
            this.state.guideCompleted = true;
            this.saveState();
            return;
        }
        
        const container = document.createElement('div');
        container.className = 'onboarding-checklist';
        container.id = 'onboardingChecklist';
        
        container.innerHTML = `
            <button class="checklist-toggle" onclick="Onboarding.toggleChecklist()">
                <i class="fas fa-tasks"></i>
                ${completedCount < checklist.length ? `<span class="badge">${checklist.length - completedCount}</span>` : ''}
            </button>
            <div class="checklist-panel">
                <div class="checklist-header">
                    <div>
                        <h3>시작 가이드</h3>
                        <div class="checklist-progress-bar">
                            <div class="checklist-progress-fill" style="width: ${progress}%"></div>
                        </div>
                    </div>
                </div>
                <div class="checklist-items">
                    ${checklist.map(item => `
                        <div class="checklist-item${item.completed ? ' completed' : ''}" data-id="${item.id}" onclick="Onboarding.handleChecklistClick('${item.id}')">
                            <div class="checklist-checkbox">
                                <i class="fas fa-check"></i>
                            </div>
                            <div class="checklist-text">
                                <span>${item.text}</span>
                                <small>${item.desc}</small>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        
        document.body.appendChild(container);
    },
    
    /**
     * 체크리스트 토글
     */
    toggleChecklist() {
        const panel = document.querySelector('.checklist-panel');
        if (panel) {
            panel.classList.toggle('active');
        }
    },
    
    /**
     * 체크리스트 항목 클릭
     */
    handleChecklistClick(id) {
        const checklist = this.userType === 'shipper' ? this.shipperChecklist : this.forwarderChecklist;
        const item = checklist.find(i => i.id === id);
        
        if (!item || item.completed) return;
        
        // 해당 기능으로 이동하는 로직
        const routes = {
            profile: 'mypage.html#settings',
            first_quote: 'quotation.html',
            review_bids: 'shipper-bidding.html',
            first_contract: 'contract-management.html',
            first_rating: 'mypage.html#ratings',
            first_bid: 'bidding-list.html',
            create_template: 'mypage.html#templates',
            first_win: 'contract-management.html',
            first_delivery: 'shipment-tracking.html'
        };
        
        if (routes[id]) {
            window.location.href = routes[id];
        }
    },
    
    /**
     * 체크리스트 항목 완료 처리
     */
    completeChecklistItem(id) {
        this.state.checklist[id] = true;
        this.saveState();
        
        // UI 업데이트
        const item = document.querySelector(`.checklist-item[data-id="${id}"]`);
        if (item) {
            item.classList.add('completed');
        }
        
        // 진행률 업데이트
        const checklist = this.userType === 'shipper' ? this.shipperChecklist : this.forwarderChecklist;
        const completedCount = Object.values(this.state.checklist).filter(v => v).length;
        const progress = Math.round((completedCount / checklist.length) * 100);
        
        const progressFill = document.querySelector('.checklist-progress-fill');
        if (progressFill) {
            progressFill.style.width = `${progress}%`;
        }
        
        // 뱃지 업데이트
        const badge = document.querySelector('.checklist-toggle .badge');
        if (badge) {
            const remaining = checklist.length - completedCount;
            if (remaining > 0) {
                badge.textContent = remaining;
            } else {
                badge.remove();
            }
        }
        
        // 모두 완료 시
        if (completedCount === checklist.length) {
            this.state.guideCompleted = true;
            this.saveState();
            
            if (window.Toast) {
                Toast.success('모든 시작 가이드를 완료했습니다!', '축하합니다!');
            }
            
            setTimeout(() => {
                const checklistEl = document.getElementById('onboardingChecklist');
                if (checklistEl) checklistEl.remove();
            }, 2000);
        }
    },
    
    /**
     * 온보딩 리셋 (테스트용)
     */
    reset() {
        localStorage.removeItem(this.STORAGE_KEY);
        location.reload();
    }
};

// 전역 등록
window.Onboarding = Onboarding;

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', () => {
    // 로그인 상태일 때만 초기화
    const isLoggedIn = localStorage.getItem('shipperUser') || localStorage.getItem('forwarderUser');
    if (isLoggedIn) {
        // 약간의 딜레이 후 초기화 (페이지 로드 완료 후)
        setTimeout(() => Onboarding.init(), 1000);
    }
});
