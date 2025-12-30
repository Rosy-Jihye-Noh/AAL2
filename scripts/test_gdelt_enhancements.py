"""
GDELT 백엔드 Phase 2/3 기능 테스트 스크립트
"""
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "server"))

import gdelt_backend
import json
from datetime import datetime, timedelta

def test_phase2_filtering():
    """Phase 2: 필터링 기능 테스트"""
    print("\n" + "="*60)
    print("Phase 2 테스트: 필터링 기능")
    print("="*60)
    
    # 기본 알림 가져오기
    print("\n1. 기본 알림 가져오기...")
    result = gdelt_backend.get_critical_alerts(
        goldstein_threshold=-5.0,
        max_alerts=10
    )
    print(f"   ✓ 기본 알림 수: {result.get('count', 0)}")
    
    # 국가별 필터링
    print("\n2. 국가별 필터링 (US)...")
    result_us = gdelt_backend.get_critical_alerts(
        goldstein_threshold=-5.0,
        max_alerts=10,
        country='US'
    )
    print(f"   ✓ US 알림 수: {result_us.get('count', 0)}")
    if result_us.get('alerts'):
        print(f"   ✓ 첫 번째 알림 국가: {result_us['alerts'][0].get('country_code', 'N/A')}")
    
    # 카테고리별 필터링
    print("\n3. 카테고리별 필터링 (Material Conflict)...")
    result_cat = gdelt_backend.get_critical_alerts(
        goldstein_threshold=-5.0,
        max_alerts=10,
        category='Material Conflict'
    )
    print(f"   ✓ Material Conflict 알림 수: {result_cat.get('count', 0)}")
    if result_cat.get('alerts'):
        print(f"   ✓ 첫 번째 알림 카테고리: {result_cat['alerts'][0].get('category', 'N/A')}")
    
    # 중요도 필터링
    print("\n4. 중요도 필터링 (최소 5개 기사)...")
    result_imp = gdelt_backend.get_critical_alerts(
        goldstein_threshold=-5.0,
        max_alerts=10,
        min_articles=5
    )
    print(f"   ✓ 중요도 필터링된 알림 수: {result_imp.get('count', 0)}")
    if result_imp.get('alerts'):
        print(f"   ✓ 첫 번째 알림 기사 수: {result_imp['alerts'][0].get('num_articles', 0)}")
    
    print("\n✓ Phase 2 필터링 테스트 완료")


def test_phase2_sorting():
    """Phase 2: 정렬 기능 테스트"""
    print("\n" + "="*60)
    print("Phase 2 테스트: 정렬 기능")
    print("="*60)
    
    # 중요도 순 정렬
    print("\n1. 중요도 순 정렬...")
    result_imp = gdelt_backend.get_critical_alerts(
        goldstein_threshold=-5.0,
        max_alerts=5,
        sort_by='importance'
    )
    print(f"   ✓ 정렬된 알림 수: {result_imp.get('count', 0)}")
    if result_imp.get('alerts'):
        first = result_imp['alerts'][0]
        importance = first.get('num_articles', 0) + first.get('num_mentions', 0)
        print(f"   ✓ 첫 번째 알림 중요도: {importance}")
    
    # 날짜 순 정렬
    print("\n2. 날짜 순 정렬...")
    result_date = gdelt_backend.get_critical_alerts(
        goldstein_threshold=-5.0,
        max_alerts=5,
        sort_by='date'
    )
    print(f"   ✓ 정렬된 알림 수: {result_date.get('count', 0)}")
    if result_date.get('alerts'):
        print(f"   ✓ 첫 번째 알림 날짜: {result_date['alerts'][0].get('event_date', 'N/A')}")
    
    # 톤 순 정렬
    print("\n3. 톤 순 정렬...")
    result_tone = gdelt_backend.get_critical_alerts(
        goldstein_threshold=-5.0,
        max_alerts=5,
        sort_by='tone'
    )
    print(f"   ✓ 정렬된 알림 수: {result_tone.get('count', 0)}")
    if result_tone.get('alerts'):
        print(f"   ✓ 첫 번째 알림 톤: {result_tone['alerts'][0].get('avg_tone', 'N/A')}")
    
    print("\n✓ Phase 2 정렬 테스트 완료")


def test_phase3_stats():
    """Phase 3: 통계 기능 테스트"""
    print("\n" + "="*60)
    print("Phase 3 테스트: 통계 기능")
    print("="*60)
    
    # 국가별 통계
    print("\n1. 국가별 통계...")
    stats_country = gdelt_backend.get_stats_by_country(
        goldstein_threshold=-5.0,
        max_alerts=1000
    )
    print(f"   ✓ 통계 국가 수: {stats_country.get('total_countries', 0)}")
    print(f"   ✓ 총 이벤트 수: {stats_country.get('total_events', 0)}")
    
    if stats_country.get('stats'):
        top_country = list(stats_country['stats'].items())[0]
        print(f"   ✓ 최다 이벤트 국가: {top_country[0]} ({top_country[1]['count']}개)")
    
    # 카테고리별 통계
    print("\n2. 카테고리별 통계...")
    stats_category = gdelt_backend.get_stats_by_category(
        goldstein_threshold=-5.0,
        max_alerts=1000
    )
    print(f"   ✓ 통계 카테고리 수: {stats_category.get('total_categories', 0)}")
    print(f"   ✓ 총 이벤트 수: {stats_category.get('total_events', 0)}")
    
    if stats_category.get('stats'):
        top_cat = list(stats_category['stats'].items())[0]
        print(f"   ✓ 최다 이벤트 카테고리: {top_cat[0]} ({top_cat[1]['count']}개)")
    
    print("\n✓ Phase 3 통계 테스트 완료")


def test_phase3_trends():
    """Phase 3: 트렌드 분석 테스트"""
    print("\n" + "="*60)
    print("Phase 3 테스트: 트렌드 분석")
    print("="*60)
    
    # 최근 3일 트렌드
    end_date = datetime.now()
    start_date = end_date - timedelta(days=2)
    
    print(f"\n1. 트렌드 분석 ({start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')})...")
    trends = gdelt_backend.get_trends(
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        goldstein_threshold=-5.0
    )
    
    print(f"   ✓ 분석 일수: {trends.get('total_days', 0)}")
    
    if trends.get('trends'):
        for date_str, data in list(trends['trends'].items())[:3]:
            print(f"   ✓ {data['date']}: {data['count']}개 이벤트, 평균 Goldstein: {data['avg_goldstein']}")
    
    print("\n✓ Phase 3 트렌드 테스트 완료")


def test_phase3_caching():
    """Phase 3: 캐싱 기능 테스트"""
    print("\n" + "="*60)
    print("Phase 3 테스트: 캐싱 기능")
    print("="*60)
    
    import time
    
    # 첫 번째 요청 (캐시 미스)
    print("\n1. 첫 번째 요청 (캐시 미스 예상)...")
    start = time.time()
    result1 = gdelt_backend.get_cached_alerts(
        goldstein_threshold=-5.0,
        max_alerts=10
    )
    time1 = time.time() - start
    print(f"   ✓ 응답 시간: {time1:.3f}초")
    print(f"   ✓ 알림 수: {result1.get('count', 0)}")
    
    # 두 번째 요청 (캐시 히트)
    print("\n2. 두 번째 요청 (캐시 히트 예상)...")
    start = time.time()
    result2 = gdelt_backend.get_cached_alerts(
        goldstein_threshold=-5.0,
        max_alerts=10
    )
    time2 = time.time() - start
    print(f"   ✓ 응답 시간: {time2:.3f}초")
    print(f"   ✓ 알림 수: {result2.get('count', 0)}")
    
    if time2 < time1:
        print(f"   ✓ 캐싱 효과 확인: {time1/time2:.1f}배 빠름")
    
    # 캐시 클리어
    print("\n3. 캐시 클리어...")
    gdelt_backend.clear_cache()
    print("   ✓ 캐시 클리어 완료")
    
    print("\n✓ Phase 3 캐싱 테스트 완료")


def test_data_fields():
    """추출된 데이터 필드 확인"""
    print("\n" + "="*60)
    print("데이터 필드 확인")
    print("="*60)
    
    result = gdelt_backend.get_critical_alerts(
        goldstein_threshold=-5.0,
        max_alerts=1
    )
    
    if result.get('alerts'):
        alert = result['alerts'][0]
        print("\n추출된 필드:")
        required_fields = [
            'name', 'event_date', 'event_code', 'category', 'quad_class',
            'actor1', 'actor1_country', 'actor2', 'actor2_country',
            'lat', 'lng', 'location', 'country_code',
            'scale', 'goldstein_scale', 'avg_tone',
            'num_articles', 'num_mentions', 'num_sources',
            'url', 'source_url'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field in alert:
                print(f"   ✓ {field}: {type(alert[field]).__name__}")
            else:
                print(f"   ✗ {field}: MISSING")
                missing_fields.append(field)
        
        if missing_fields:
            print(f"\n⚠ 누락된 필드: {', '.join(missing_fields)}")
        else:
            print("\n✓ 모든 필수 필드가 추출되었습니다.")
    else:
        print("⚠ 알림 데이터가 없습니다.")


def main():
    """메인 테스트 함수"""
    print("="*60)
    print("GDELT 백엔드 Phase 2/3 기능 테스트")
    print("="*60)
    
    try:
        # 데이터 필드 확인
        test_data_fields()
        
        # Phase 2 테스트
        test_phase2_filtering()
        test_phase2_sorting()
        
        # Phase 3 테스트
        test_phase3_stats()
        test_phase3_trends()
        test_phase3_caching()
        
        print("\n" + "="*60)
        print("모든 테스트 완료!")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())

