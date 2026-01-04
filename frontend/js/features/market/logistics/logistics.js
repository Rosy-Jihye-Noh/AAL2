/**
 * AAL Application - Logistics Module
 * 물류 지수 관련 기능 모듈
 * 
 * 담당 패널: #logistics-panel
 * 주요 기능: 물류 지수, 운임 지수, 컨테이너 지수
 * 
 * 포함 지수:
 * - KCCI (Korea Container Freight Index) - 구현 완료
 * - SCFI (Shanghai Container Freight Index) - 추후 구현
 * - BDI (Baltic Dry Index) - 추후 구현
 * - NCFI (Ningbo Container Freight Index) - 추후 구현
 */

// ============================================================
// MODULE MARKER
// ============================================================
window.logisticsModuleLoaded = true;

// ============================================================
// LOGISTICS INITIALIZATION
// ============================================================

/**
 * Logistics 탭 초기화
 * Economy 탭에서 Logistics 탭으로 전환될 때 호출
 */
function initLogistics() {
    console.log('🚛 Initializing Logistics module...');
    
    // KCCI 초기화 (기본값)
    if (typeof initKCCI === 'function' && !window.kcciDataLoaded) {
        initKCCI();
    }
}

// ============================================================
// GLOBAL EXPORTS
// ============================================================

window.initLogistics = initLogistics;

console.log('🚛 Logistics module loaded');

