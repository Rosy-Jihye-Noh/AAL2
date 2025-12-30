"""
GDELT API 상세 테스트 - 필터링 및 데이터 검증
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_country_filtering_detailed():
    """국가 필터링 상세 테스트"""
    print("\n" + "="*60)
    print("국가 필터링 상세 테스트")
    print("="*60)
    
    # 먼저 기본 데이터 확인
    print("\n1. 기본 알림 데이터 확인...")
    response = requests.get(f"{BASE_URL}/api/global-alerts?threshold=-5.0&max_alerts=100")
    assert response.status_code == 200
    data = response.json()
    alerts = data.get('alerts', [])
    print(f"   총 알림 수: {len(alerts)}")
    
    # 국가 코드 분포 확인
    country_counts = {}
    for alert in alerts:
        country = alert.get('country_code', 'UNKNOWN')
        country_counts[country] = country_counts.get(country, 0) + 1
    
    print(f"\n2. 국가별 분포:")
    for country, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   {country}: {count}개")
    
    # US 데이터 확인
    us_alerts = [a for a in alerts if a.get('country_code') == 'US' or 
                 a.get('actor1_country') == 'USA' or a.get('actor2_country') == 'USA']
    print(f"\n3. US 관련 알림 수: {len(us_alerts)}")
    
    if us_alerts:
        print(f"   첫 번째 US 알림:")
        alert = us_alerts[0]
        print(f"     - country_code: {alert.get('country_code')}")
        print(f"     - actor1_country: {alert.get('actor1_country')}")
        print(f"     - actor2_country: {alert.get('actor2_country')}")
        print(f"     - location: {alert.get('location')}")
    
    # US 필터링 테스트
    print(f"\n4. US 필터링 테스트...")
    response = requests.get(f"{BASE_URL}/api/global-alerts?country=US&max_alerts=100")
    assert response.status_code == 200
    filtered_data = response.json()
    print(f"   필터링된 알림 수: {filtered_data.get('count', 0)}")
    
    if filtered_data.get('alerts'):
        print(f"   첫 번째 필터링된 알림:")
        alert = filtered_data['alerts'][0]
        print(f"     - country_code: {alert.get('country_code')}")
        print(f"     - location: {alert.get('location')}")
    
    return len(us_alerts) > 0

def test_all_filters():
    """모든 필터 조합 테스트"""
    print("\n" + "="*60)
    print("필터 조합 테스트")
    print("="*60)
    
    # 카테고리별 분포 확인
    print("\n1. 카테고리별 분포:")
    response = requests.get(f"{BASE_URL}/api/global-alerts?threshold=-5.0&max_alerts=100")
    data = response.json()
    alerts = data.get('alerts', [])
    
    category_counts = {}
    for alert in alerts:
        cat = alert.get('category', 'Unknown')
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   {cat}: {count}개")
    
    # 필터 조합 테스트
    print("\n2. 필터 조합 테스트:")
    
    # 카테고리만
    response = requests.get(f"{BASE_URL}/api/global-alerts?category=Material Conflict&max_alerts=10")
    data = response.json()
    print(f"   카테고리 필터만: {data.get('count', 0)}개")
    
    # 중요도 필터만
    response = requests.get(f"{BASE_URL}/api/global-alerts?min_articles=5&max_alerts=10")
    data = response.json()
    print(f"   중요도 필터만 (min_articles=5): {data.get('count', 0)}개")
    
    # 정렬 테스트
    print("\n3. 정렬 테스트:")
    for sort_by in ['importance', 'date', 'tone', 'scale']:
        response = requests.get(f"{BASE_URL}/api/global-alerts?sort_by={sort_by}&max_alerts=5")
        data = response.json()
        if data.get('alerts'):
            first = data['alerts'][0]
            if sort_by == 'importance':
                value = first.get('num_articles', 0) + first.get('num_mentions', 0)
            elif sort_by == 'date':
                value = first.get('event_date', 'N/A')
            elif sort_by == 'tone':
                value = first.get('avg_tone', 'N/A')
            else:
                value = first.get('goldstein_scale', 'N/A')
            print(f"   {sort_by}: 첫 번째 값 = {value}")

def test_data_fields():
    """데이터 필드 확인"""
    print("\n" + "="*60)
    print("데이터 필드 확인")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/global-alerts?max_alerts=1")
    data = response.json()
    
    if data.get('alerts'):
        alert = data['alerts'][0]
        print("\n추출된 필드:")
        required_fields = [
            'name', 'event_date', 'event_code', 'category', 'quad_class',
            'actor1', 'actor1_country', 'actor2', 'actor2_country',
            'lat', 'lng', 'location', 'country_code',
            'scale', 'goldstein_scale', 'avg_tone',
            'num_articles', 'num_mentions', 'num_sources',
            'url', 'source_url'
        ]
        
        missing = []
        for field in required_fields:
            if field in alert:
                value = alert[field]
                value_str = str(value)[:50] if value else 'None'
                print(f"   ✓ {field}: {value_str}")
            else:
                print(f"   ✗ {field}: MISSING")
                missing.append(field)
        
        if missing:
            print(f"\n⚠ 누락된 필드: {', '.join(missing)}")
        else:
            print("\n✓ 모든 필수 필드가 추출되었습니다.")

if __name__ == '__main__':
    print("="*60)
    print("GDELT API 상세 테스트")
    print("="*60)
    
    try:
        test_data_fields()
        test_country_filtering_detailed()
        test_all_filters()
        
        print("\n" + "="*60)
        print("상세 테스트 완료!")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n✗ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
    except Exception as e:
        print(f"\n✗ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

