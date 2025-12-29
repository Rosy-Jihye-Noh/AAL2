#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
서버 테스트 스크립트
"""
import sys
import requests
import json

def test_server():
    base_url = "http://127.0.0.1:5000"
    
    print("=" * 60)
    print("서버 연결 테스트")
    print("=" * 60)
    
    # 1. 메인 페이지 테스트
    print("\n1. 메인 페이지 테스트...")
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("   [OK] 메인 페이지 정상 작동")
        else:
            print(f"   ⚠️  메인 페이지 응답 코드: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   [ERROR] 메인 페이지 연결 실패: {e}")
        return False
    
    # 2. 카테고리 정보 테스트
    print("\n2. 카테고리 정보 API 테스트...")
    try:
        response = requests.get(f"{base_url}/api/market/categories", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'categories' in data or 'error' not in data:
                print("   [OK] 카테고리 API 정상 작동")
                if 'categories' in data:
                    print(f"      - 사용 가능한 카테고리 수: {len(data.get('categories', {}))}")
            else:
                print(f"   ⚠️  카테고리 API 응답에 문제: {data.get('error', 'Unknown')}")
        else:
            print(f"   ⚠️  카테고리 API 응답 코드: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ 카테고리 API 연결 실패: {e}")
    
    # 3. Trade API 테스트
    print("\n3. Trade API 테스트...")
    try:
        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        start_str = start_date.strftime('%Y%m%d')
        end_str = end_date.strftime('%Y%m%d')
        
        url = f"{base_url}/api/market/indices?type=trade&itemCode=EXPORT_USD&startDate={start_str}&endDate={end_str}&cycle=M"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'StatisticSearch' in data and 'row' in data.get('StatisticSearch', {}):
                row_count = len(data['StatisticSearch']['row'])
                print(f"   [OK] Trade API 정상 작동 (데이터 행 수: {row_count})")
            else:
                print(f"   ⚠️  Trade API 응답 형식 이상: {data.get('error', 'Unknown')}")
        else:
            print(f"   ⚠️  Trade API 응답 코드: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Trade API 연결 실패: {e}")
    
    # 4. GDP API 테스트
    print("\n4. GDP API 테스트...")
    try:
        from datetime import datetime
        current_year = datetime.now().year - 1
        start_str = f"{current_year - 1}0101"
        end_str = f"{current_year}1231"
        
        url = f"{base_url}/api/market/indices?type=gdp&itemCode=10101&startDate={start_str}&endDate={end_str}&cycle=A"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'StatisticSearch' in data and 'row' in data.get('StatisticSearch', {}):
                row_count = len(data['StatisticSearch']['row'])
                print(f"   [OK] GDP API 정상 작동 (데이터 행 수: {row_count})")
            else:
                print(f"   ⚠️  GDP API 응답 형식 이상: {data.get('error', 'Unknown')}")
        else:
            print(f"   ⚠️  GDP API 응답 코드: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ GDP API 연결 실패: {e}")
    
    print("\n" + "=" * 60)
    print("테스트 완료")
    print("=" * 60)
    print(f"\n서버 URL: {base_url}")
    print("브라우저에서 접속하여 기능을 테스트하세요.")
    
    return True

if __name__ == "__main__":
    test_server()

