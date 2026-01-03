/**
 * Loading Utilities
 * 로딩 상태 관리 유틸리티
 */

const Loading = {
    // 현재 활성화된 오버레이 참조
    _overlay: null,
    
    /**
     * 전체 화면 로딩 오버레이 표시
     * @param {string} text - 로딩 텍스트
     * @param {string} subtext - 서브 텍스트 (선택)
     */
    showOverlay(text = '로딩 중...', subtext = '') {
        // 기존 오버레이가 있으면 제거
        if (this._overlay) {
            this.hideOverlay();
        }
        
        this._overlay = document.createElement('div');
        this._overlay.className = 'loading-overlay';
        this._overlay.innerHTML = `
            <div class="spinner spinner-xl"></div>
            <div class="loading-text">${text}</div>
            ${subtext ? `<div class="loading-subtext">${subtext}</div>` : ''}
        `;
        
        document.body.appendChild(this._overlay);
        
        // 애니메이션을 위해 약간의 딜레이
        requestAnimationFrame(() => {
            this._overlay.classList.add('active');
        });
    },
    
    /**
     * 전체 화면 로딩 오버레이 숨기기
     */
    hideOverlay() {
        if (this._overlay) {
            this._overlay.classList.remove('active');
            setTimeout(() => {
                if (this._overlay && this._overlay.parentNode) {
                    this._overlay.parentNode.removeChild(this._overlay);
                }
                this._overlay = null;
            }, 300);
        }
    },
    
    /**
     * 버튼 로딩 상태 설정
     * @param {HTMLElement} button - 버튼 요소
     * @param {boolean} isLoading - 로딩 상태
     */
    setButtonLoading(button, isLoading = true) {
        if (!button) return;
        
        if (isLoading) {
            button.classList.add('btn-loading');
            button.disabled = true;
            button.dataset.originalText = button.innerHTML;
            
            // 버튼 내용을 감싸서 숨기고 스피너 표시
            const text = button.innerHTML;
            button.innerHTML = `<span class="btn-text">${text}</span>`;
        } else {
            button.classList.remove('btn-loading');
            button.disabled = false;
            if (button.dataset.originalText) {
                button.innerHTML = button.dataset.originalText;
                delete button.dataset.originalText;
            }
        }
    },
    
    /**
     * 컨테이너 내부 로딩 표시
     * @param {HTMLElement|string} container - 컨테이너 요소 또는 선택자
     * @param {string} text - 로딩 텍스트
     */
    showInContainer(container, text = '로딩 중...') {
        const el = typeof container === 'string' 
            ? document.querySelector(container) 
            : container;
        
        if (!el) return;
        
        // 기존 내용 저장
        el.dataset.originalContent = el.innerHTML;
        
        el.innerHTML = `
            <div class="loading-container">
                <div class="spinner spinner-lg"></div>
                <div class="loading-text">${text}</div>
            </div>
        `;
    },
    
    /**
     * 컨테이너 내부 로딩 숨기기 및 원래 내용 복원
     * @param {HTMLElement|string} container - 컨테이너 요소 또는 선택자
     * @param {string} newContent - 새 내용 (선택, 없으면 원래 내용 복원)
     */
    hideInContainer(container, newContent = null) {
        const el = typeof container === 'string' 
            ? document.querySelector(container) 
            : container;
        
        if (!el) return;
        
        if (newContent !== null) {
            el.innerHTML = newContent;
        } else if (el.dataset.originalContent) {
            el.innerHTML = el.dataset.originalContent;
            delete el.dataset.originalContent;
        }
    },
    
    /**
     * 스켈레톤 로딩 생성
     * @param {string} type - 스켈레톤 타입
     * @param {number} count - 개수
     * @returns {string} HTML 문자열
     */
    createSkeleton(type = 'card', count = 3) {
        const skeletons = [];
        
        for (let i = 0; i < count; i++) {
            switch (type) {
                case 'card':
                    skeletons.push(`
                        <div class="skeleton-card-preset">
                            <div class="skeleton-header">
                                <div class="skeleton skeleton-avatar"></div>
                                <div class="skeleton-content" style="flex: 1;">
                                    <div class="skeleton skeleton-text" style="width: 60%;"></div>
                                    <div class="skeleton skeleton-text-sm" style="width: 40%;"></div>
                                </div>
                            </div>
                            <div class="skeleton-body">
                                <div class="skeleton skeleton-text"></div>
                                <div class="skeleton skeleton-text"></div>
                                <div class="skeleton skeleton-text-lg"></div>
                            </div>
                        </div>
                    `);
                    break;
                    
                case 'list':
                    skeletons.push(`
                        <div class="skeleton-list-item">
                            <div class="skeleton skeleton-avatar"></div>
                            <div class="skeleton-content">
                                <div class="skeleton skeleton-text" style="width: 70%;"></div>
                                <div class="skeleton skeleton-text-sm" style="width: 50%;"></div>
                            </div>
                            <div class="skeleton skeleton-button"></div>
                        </div>
                    `);
                    break;
                    
                case 'table-row':
                    skeletons.push(`
                        <div class="skeleton-table-row">
                            <div class="skeleton skeleton-table-cell"></div>
                            <div class="skeleton skeleton-table-cell"></div>
                            <div class="skeleton skeleton-table-cell"></div>
                            <div class="skeleton skeleton-table-cell"></div>
                            <div class="skeleton skeleton-table-cell"></div>
                        </div>
                    `);
                    break;
                    
                case 'stat':
                    skeletons.push(`
                        <div class="skeleton-stat-card">
                            <div class="skeleton skeleton-label"></div>
                            <div class="skeleton skeleton-value"></div>
                        </div>
                    `);
                    break;
                    
                case 'chart':
                    skeletons.push(`<div class="skeleton skeleton-chart"></div>`);
                    break;
                    
                default:
                    skeletons.push(`<div class="skeleton skeleton-text"></div>`);
            }
        }
        
        return skeletons.join('');
    },
    
    /**
     * 프로그레스 바 생성
     * @param {HTMLElement|string} container - 컨테이너
     * @param {boolean} indeterminate - 불확정 모드
     * @returns {Object} 프로그레스 바 컨트롤러
     */
    createProgressBar(container, indeterminate = false) {
        const el = typeof container === 'string' 
            ? document.querySelector(container) 
            : container;
        
        if (!el) return null;
        
        const progressBar = document.createElement('div');
        progressBar.className = `progress-bar${indeterminate ? ' progress-bar-indeterminate' : ''}`;
        progressBar.innerHTML = '<div class="progress-bar-fill" style="width: 0%"></div>';
        
        el.appendChild(progressBar);
        
        const fill = progressBar.querySelector('.progress-bar-fill');
        
        return {
            setProgress(percent) {
                fill.style.width = `${Math.min(100, Math.max(0, percent))}%`;
            },
            remove() {
                progressBar.remove();
            }
        };
    },
    
    /**
     * 요소에 로딩 상태 추가
     * @param {HTMLElement|string} element - 요소
     */
    addLoadingState(element) {
        const el = typeof element === 'string' 
            ? document.querySelector(element) 
            : element;
        
        if (el) {
            el.classList.add('is-loading');
        }
    },
    
    /**
     * 요소에서 로딩 상태 제거
     * @param {HTMLElement|string} element - 요소
     */
    removeLoadingState(element) {
        const el = typeof element === 'string' 
            ? document.querySelector(element) 
            : element;
        
        if (el) {
            el.classList.remove('is-loading');
        }
    },
    
    /**
     * 로딩 dots HTML 생성
     * @returns {string} HTML
     */
    createDots() {
        return `
            <div class="loading-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
    },
    
    /**
     * 비동기 작업 래퍼 - 로딩 상태 자동 관리
     * @param {Function} asyncFn - 비동기 함수
     * @param {Object} options - 옵션
     * @returns {Promise} 결과
     */
    async withLoading(asyncFn, options = {}) {
        const {
            overlay = false,
            overlayText = '처리 중...',
            button = null,
            container = null,
            containerText = '로딩 중...'
        } = options;
        
        try {
            if (overlay) {
                this.showOverlay(overlayText);
            }
            if (button) {
                this.setButtonLoading(button, true);
            }
            if (container) {
                this.showInContainer(container, containerText);
            }
            
            const result = await asyncFn();
            return result;
            
        } finally {
            if (overlay) {
                this.hideOverlay();
            }
            if (button) {
                this.setButtonLoading(button, false);
            }
            // container는 호출자가 직접 hideInContainer 호출해야 함
        }
    }
};

// 전역 등록
window.Loading = Loading;
