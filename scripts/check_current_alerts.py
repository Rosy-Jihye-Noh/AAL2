import json
import requests

# Flask API 호출
try:
    response = requests.get('http://localhost:5000/api/global-alerts?threshold=-5.0&max_alerts=1000')
    
    if response.status_code == 200:
        data = response.json()
        alerts = data.get('alerts', [])
        
        print(f'Total alerts: {len(alerts)}')
        print('=' * 80)
        
        # nvdaily.com 기사 찾기
        search_keywords = ['nvdaily', 'maphis', '2ec7d9f6']
        
        found_count = 0
        for alert in alerts:
            url = alert.get('url', '').lower()
            
            # 키워드 포함 여부 확인
            if any(keyword in url for keyword in search_keywords):
                found_count += 1
                print(f'\nFOUND #{found_count}:')
                print('=' * 80)
                print(f"GoldsteinScale: {alert.get('goldstein_scale', 'N/A')}")
                print(f"Scale: {alert.get('scale', 'N/A')}")
                print(f"Event Code: {alert.get('event_code', 'N/A')}")
                print(f"QuadClass: {alert.get('quad_class', 'N/A')}")
                print(f"Category: {alert.get('category', 'N/A')}")
                print(f"Name: {alert.get('name', 'N/A')}")
                print(f"Actor1: {alert.get('actor1', 'N/A')}")
                print(f"Actor2: {alert.get('actor2', 'N/A')}")
                print(f"Location: {alert.get('location', 'N/A')}")
                print(f"Event Date: {alert.get('event_date', 'N/A')}")
                print(f"Num Mentions: {alert.get('num_mentions', 'N/A')}")
                print(f"Num Sources: {alert.get('num_sources', 'N/A')}")
                print(f"Num Articles: {alert.get('num_articles', 'N/A')}")
                print(f"Avg Tone: {alert.get('avg_tone', 'N/A')}")
                print(f"URL: {alert.get('url', 'N/A')}")
                print('=' * 80)
        
        if found_count == 0:
            print('\nNo matching articles found in current alerts.')
            print('\nSearching for similar keywords in all alerts...')
            
            # 모든 URL 출력 (샘플)
            print('\nSample URLs (first 10):')
            for i, alert in enumerate(alerts[:10]):
                print(f"{i+1}. {alert.get('url', 'N/A')[:100]}")
            
    else:
        print(f'Error: HTTP {response.status_code}')
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print('ERROR: Could not connect to Flask server.')
    print('Please make sure the server is running on http://localhost:5000')
except Exception as e:
    print(f'Error: {e}')

