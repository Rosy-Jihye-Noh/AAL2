"""
GDELT API 엔드포인트 테스트 스크립트
서버가 실행 중일 때 사용
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000"

def test_basic_alerts():
    """기본 알림 API 테스트"""
    print("\n1. 기본 알림 API 테스트...")
    response = requests.get(f"{BASE_URL}/api/global-alerts?threshold=-5.0&max_alerts=5")
    assert response.status_code == 200, f"Status code: {response.status_code}"
    data = response.json()
    print(f"   ✓ 알림 수: {data.get('count', 0)}")
    print(f"   ✓ 필터 정보: {data.get('filters', {})}")
    if data.get('alerts'):
        alert = data['alerts'][0]
        print(f"   ✓ 첫 번째 알림 필드 수: {len(alert)}")
    return True

def test_filtering():
    """필터링 API 테스트"""
    print("\n2. 필터링 API 테스트...")
    
    # 국가별 필터링
    response = requests.get(f"{BASE_URL}/api/global-alerts?country=US&max_alerts=5")
    assert response.status_code == 200
    data = response.json()
    print(f"   ✓ 국가 필터 (US): {data.get('count', 0)}개")
    
    # 카테고리별 필터링
    response = requests.get(f"{BASE_URL}/api/global-alerts?category=Material Conflict&max_alerts=5")
    assert response.status_code == 200
    data = response.json()
    print(f"   ✓ 카테고리 필터: {data.get('count', 0)}개")
    
    return True

def test_sorting():
    """정렬 API 테스트"""
    print("\n3. 정렬 API 테스트...")
    
    response = requests.get(f"{BASE_URL}/api/global-alerts?sort_by=importance&max_alerts=5")
    assert response.status_code == 200
    data = response.json()
    print(f"   ✓ 중요도 순 정렬: {data.get('count', 0)}개")
    
    return True

def test_stats():
    """통계 API 테스트"""
    print("\n4. 통계 API 테스트...")
    
    # 국가별 통계
    response = requests.get(f"{BASE_URL}/api/global-alerts/stats/by-country")
    assert response.status_code == 200
    data = response.json()
    print(f"   ✓ 국가별 통계: {data.get('total_countries', 0)}개 국가")
    
    # 카테고리별 통계
    response = requests.get(f"{BASE_URL}/api/global-alerts/stats/by-category")
    assert response.status_code == 200
    data = response.json()
    print(f"   ✓ 카테고리별 통계: {data.get('total_categories', 0)}개 카테고리")
    
    return True

def test_trends():
    """트렌드 API 테스트"""
    print("\n5. 트렌드 API 테스트...")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=2)
    
    url = f"{BASE_URL}/api/global-alerts/trends"
    params = {
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d')
    }
    response = requests.get(url, params=params)
    assert response.status_code == 200
    data = response.json()
    print(f"   ✓ 트렌드 분석: {data.get('total_days', 0)}일")
    
    return True

if __name__ == '__main__':
    print("="*60)
    print("GDELT API 테스트")
    print("="*60)
    print(f"서버 URL: {BASE_URL}")
    print("서버가 실행 중인지 확인하세요.")
    
    try:
        test_basic_alerts()
        test_filtering()
        test_sorting()
        test_stats()
        test_trends()
        print("\n" + "="*60)
        print("모든 API 테스트 통과!")
        print("="*60)
    except requests.exceptions.ConnectionError:
        print("\n✗ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
    except AssertionError as e:
        print(f"\n✗ 테스트 실패: {e}")

