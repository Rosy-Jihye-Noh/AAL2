/**
 * Toast Notification Module
 * 토스트 알림 유틸리티
 */

const Toast = {
    // 설정
    config: {
        position: 'top-right',
        duration: 5000,
        maxToasts: 5
    },
    
    // 토스트 컨테이너
    _container: null,
    
    // 활성 토스트 목록
    _toasts: [],
    
    /**
     * 토스트 컨테이너 초기화
     */
    _initContainer() {
        if (this._container) return;
        
        this._container = document.createElement('div');
        this._container.className = `toast-container ${this.config.position}`;
        document.body.appendChild(this._container);
    },
    
    /**
     * 토스트 표시
     * @param {Object} options - 토스트 옵션
     * @returns {HTMLElement} 토스트 요소
     */
    show(options = {}) {
        const {
            type = 'info',
            title = '',
            message = '',
            duration = this.config.duration,
            closable = true,
            action = null,
            onClose = null
        } = options;
        
        this._initContainer();
        
        // 최대 토스트 수 제한
        while (this._toasts.length >= this.config.maxToasts) {
            this.dismiss(this._toasts[0]);
        }
        
        // 아이콘 매핑
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-times-circle',
            warning: 'fas fa-exclamation-circle',
            info: 'fas fa-info-circle'
        };
        
        // 토스트 요소 생성
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        let actionHTML = '';
        if (action) {
            actionHTML = `<button class="toast-action" data-action="custom">${action.text}</button>`;
        }
        
        toast.innerHTML = `
            <i class="toast-icon ${icons[type]}"></i>
            <div class="toast-content">
                ${title ? `<div class="toast-title">${title}</div>` : ''}
                <div class="toast-message">${message}</div>
                ${actionHTML}
            </div>
            ${closable ? '<button class="toast-close"><i class="fas fa-times"></i></button>' : ''}
            ${duration > 0 ? `<div class="toast-progress" style="animation-duration: ${duration}ms"></div>` : ''}
        `;
        
        // 닫기 버튼 이벤트
        const closeBtn = toast.querySelector('.toast-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                this.dismiss(toast, onClose);
            });
        }
        
        // 액션 버튼 이벤트
        const actionBtn = toast.querySelector('.toast-action');
        if (actionBtn && action && action.onClick) {
            actionBtn.addEventListener('click', () => {
                action.onClick();
                if (action.closeOnClick !== false) {
                    this.dismiss(toast, onClose);
                }
            });
        }
        
        // 컨테이너에 추가
        this._container.appendChild(toast);
        this._toasts.push(toast);
        
        // 자동 닫기
        if (duration > 0) {
            toast._timeout = setTimeout(() => {
                this.dismiss(toast, onClose);
            }, duration);
        }
        
        // 마우스 오버 시 자동 닫기 일시 정지
        toast.addEventListener('mouseenter', () => {
            if (toast._timeout) {
                clearTimeout(toast._timeout);
                const progress = toast.querySelector('.toast-progress');
                if (progress) {
                    progress.style.animationPlayState = 'paused';
                }
            }
        });
        
        toast.addEventListener('mouseleave', () => {
            if (duration > 0) {
                const progress = toast.querySelector('.toast-progress');
                if (progress) {
                    progress.style.animationPlayState = 'running';
                }
                toast._timeout = setTimeout(() => {
                    this.dismiss(toast, onClose);
                }, duration / 2); // 남은 시간 절반으로
            }
        });
        
        return toast;
    },
    
    /**
     * 토스트 닫기
     * @param {HTMLElement} toast - 토스트 요소
     * @param {Function} onClose - 닫기 콜백
     */
    dismiss(toast, onClose = null) {
        if (!toast || toast._removing) return;
        
        toast._removing = true;
        
        if (toast._timeout) {
            clearTimeout(toast._timeout);
        }
        
        toast.classList.add('removing');
        
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
            
            const index = this._toasts.indexOf(toast);
            if (index > -1) {
                this._toasts.splice(index, 1);
            }
            
            if (onClose) {
                onClose();
            }
        }, 300);
    },
    
    /**
     * 모든 토스트 닫기
     */
    dismissAll() {
        [...this._toasts].forEach(toast => this.dismiss(toast));
    },
    
    /**
     * 성공 토스트
     */
    success(message, title = '성공', options = {}) {
        return this.show({ type: 'success', message, title, ...options });
    },
    
    /**
     * 에러 토스트
     */
    error(message, title = '오류', options = {}) {
        return this.show({ type: 'error', message, title, duration: 7000, ...options });
    },
    
    /**
     * 경고 토스트
     */
    warning(message, title = '경고', options = {}) {
        return this.show({ type: 'warning', message, title, duration: 6000, ...options });
    },
    
    /**
     * 정보 토스트
     */
    info(message, title = '', options = {}) {
        return this.show({ type: 'info', message, title, ...options });
    },
    
    /**
     * 설정 변경
     */
    configure(options = {}) {
        Object.assign(this.config, options);
        
        if (this._container && options.position) {
            this._container.className = `toast-container ${this.config.position}`;
        }
    }
};

/**
 * Empty State Helper
 * 빈 상태 UI 생성 헬퍼
 */
const EmptyState = {
    /**
     * 빈 상태 HTML 생성
     * @param {Object} options - 옵션
     * @returns {string} HTML 문자열
     */
    create(options = {}) {
        const {
            icon = 'fas fa-inbox',
            title = '데이터가 없습니다',
            message = '',
            actionText = '',
            actionIcon = '',
            compact = false
        } = options;
        
        let actionHTML = '';
        if (actionText) {
            actionHTML = `
                <button class="empty-state-action" data-action="empty-action">
                    ${actionIcon ? `<i class="${actionIcon}"></i>` : ''}
                    ${actionText}
                </button>
            `;
        }
        
        return `
            <div class="empty-state${compact ? ' compact' : ''}">
                <i class="empty-state-icon ${icon}"></i>
                <h3 class="empty-state-title">${title}</h3>
                ${message ? `<p class="empty-state-message">${message}</p>` : ''}
                ${actionHTML}
            </div>
        `;
    },
    
    /**
     * 컨테이너에 빈 상태 표시
     * @param {HTMLElement|string} container - 컨테이너
     * @param {Object} options - 옵션
     * @param {Function} onAction - 액션 버튼 클릭 핸들러
     */
    show(container, options = {}, onAction = null) {
        const el = typeof container === 'string' 
            ? document.querySelector(container) 
            : container;
        
        if (!el) return;
        
        el.innerHTML = this.create(options);
        
        if (onAction) {
            const actionBtn = el.querySelector('[data-action="empty-action"]');
            if (actionBtn) {
                actionBtn.addEventListener('click', onAction);
            }
        }
    },
    
    // 프리셋
    presets: {
        noData: {
            icon: 'fas fa-database',
            title: '데이터가 없습니다',
            message: '표시할 데이터가 없습니다.'
        },
        noResults: {
            icon: 'fas fa-search',
            title: '검색 결과가 없습니다',
            message: '다른 검색어로 다시 시도해 보세요.'
        },
        noMessages: {
            icon: 'fas fa-envelope-open',
            title: '메시지가 없습니다',
            message: '받은 메시지가 없습니다.'
        },
        noNotifications: {
            icon: 'fas fa-bell-slash',
            title: '알림이 없습니다',
            message: '새로운 알림이 없습니다.'
        },
        error: {
            icon: 'fas fa-exclamation-triangle',
            title: '오류가 발생했습니다',
            message: '데이터를 불러올 수 없습니다. 잠시 후 다시 시도해 주세요.'
        },
        offline: {
            icon: 'fas fa-wifi-slash',
            title: '오프라인 상태',
            message: '인터넷 연결을 확인해 주세요.'
        }
    }
};

/**
 * Form Validation Helper
 * 폼 검증 에러 UI 헬퍼
 */
const FormError = {
    /**
     * 입력 필드에 에러 표시
     * @param {HTMLElement|string} input - 입력 필드
     * @param {string} message - 에러 메시지
     */
    show(input, message) {
        const el = typeof input === 'string' 
            ? document.querySelector(input) 
            : input;
        
        if (!el) return;
        
        // 기존 에러 제거
        this.clear(el);
        
        // 입력 필드에 에러 클래스 추가
        el.classList.add('input-error');
        
        // 에러 메시지 요소 생성
        const errorEl = document.createElement('div');
        errorEl.className = 'form-error';
        errorEl.innerHTML = `<i class="fas fa-exclamation-circle"></i><span>${message}</span>`;
        
        // 입력 필드 다음에 삽입
        el.parentNode.insertBefore(errorEl, el.nextSibling);
        
        // 포커스 시 에러 제거
        el.addEventListener('focus', () => this.clear(el), { once: true });
    },
    
    /**
     * 에러 제거
     * @param {HTMLElement|string} input - 입력 필드
     */
    clear(input) {
        const el = typeof input === 'string' 
            ? document.querySelector(input) 
            : input;
        
        if (!el) return;
        
        el.classList.remove('input-error');
        
        const errorEl = el.parentNode.querySelector('.form-error');
        if (errorEl) {
            errorEl.remove();
        }
    },
    
    /**
     * 폼 내 모든 에러 제거
     * @param {HTMLElement|string} form - 폼 요소
     */
    clearAll(form) {
        const el = typeof form === 'string' 
            ? document.querySelector(form) 
            : form;
        
        if (!el) return;
        
        el.querySelectorAll('.input-error').forEach(input => {
            this.clear(input);
        });
    }
};

// 전역 등록
window.Toast = Toast;
window.EmptyState = EmptyState;
window.FormError = FormError;
