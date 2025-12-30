#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for the 5 new international BOK indicators:
1. gdp-international (902Y016) - 국제 주요국 국내총생산(GDP)
2. gni-international (902Y017) - 국제 주요국 국민총소득(GNI)
3. gdp-per-capita-international (902Y018) - 국제 주요국 1인당 GDP
4. unemployment-international (902Y021) - 국제 주요국 실업률(계절변동조정)
5. stock-index-international (902Y002) - 국제 주요국 주가지수
"""

import sys
import os
import io

# Set stdout to UTF-8 on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.bok_backend import (
    get_category_info,
    get_market_index,
    get_statistic_item_list,
    BOK_MAPPING
)

# Test categories
NEW_CATEGORIES = [
    {
        "category": "gdp-international",
        "stat_code": "902Y016",
        "name": "국제 주요국 국내총생산(GDP)",
        "default_cycle": "A"
    },
    {
        "category": "gni-international",
        "stat_code": "902Y017",
        "name": "국제 주요국 국민총소득(GNI)",
        "default_cycle": "A"
    },
    {
        "category": "gdp-per-capita-international",
        "stat_code": "902Y018",
        "name": "국제 주요국 1인당 GDP",
        "default_cycle": "A"
    },
    {
        "category": "unemployment-international",
        "stat_code": "902Y021",
        "name": "국제 주요국 실업률(계절변동조정)",
        "default_cycle": "M"
    },
    {
        "category": "stock-index-international",
        "stat_code": "902Y002",
        "name": "국제 주요국 주가지수",
        "default_cycle": "M"
    }
]

def print_separator():
    print("=" * 80)

def test_bok_mapping():
    """Test that new categories are properly added to BOK_MAPPING"""
    print_separator()
    print("TEST 1: Verifying BOK_MAPPING entries")
    print_separator()
    
    success_count = 0
    for cat_info in NEW_CATEGORIES:
        category = cat_info["category"]
        if category in BOK_MAPPING:
            mapping = BOK_MAPPING[category]
            print(f"✓ {category}")
            print(f"  - stat_code: {mapping.get('stat_code')}")
            print(f"  - name: {mapping.get('name')}")
            print(f"  - default_cycle: {mapping.get('default_cycle')}")
            
            # Verify values
            assert mapping.get('stat_code') == cat_info['stat_code'], f"stat_code mismatch for {category}"
            assert mapping.get('name') == cat_info['name'], f"name mismatch for {category}"
            assert mapping.get('default_cycle') == cat_info['default_cycle'], f"default_cycle mismatch for {category}"
            
            success_count += 1
        else:
            print(f"✗ {category} - NOT FOUND in BOK_MAPPING")
    
    print(f"\nResult: {success_count}/{len(NEW_CATEGORIES)} categories verified")
    return success_count == len(NEW_CATEGORIES)

def test_statistic_item_list():
    """Test StatisticItemList API for each new category"""
    print_separator()
    print("TEST 2: Testing StatisticItemList API")
    print_separator()
    
    success_count = 0
    for cat_info in NEW_CATEGORIES:
        stat_code = cat_info["stat_code"]
        category = cat_info["category"]
        
        print(f"\nTesting {category} ({stat_code})...")
        result = get_statistic_item_list(stat_code, start_index=1, end_index=50)
        
        if 'error' in result:
            print(f"  ✗ Error: {result['error']}")
        else:
            items = result.get('row', [])
            total = result.get('list_total_count', 0)
            print(f"  ✓ Found {total} items")
            
            # Print first 5 items as sample
            if items:
                print("  Sample items:")
                for item in items[:5]:
                    item_code = item.get('ITEM_CODE', 'N/A')
                    item_name = item.get('ITEM_NAME', 'N/A')
                    cycle = item.get('CYCLE', 'N/A')
                    print(f"    - {item_code}: {item_name} (cycle: {cycle})")
                
                success_count += 1
    
    print(f"\nResult: {success_count}/{len(NEW_CATEGORIES)} categories have data")
    return success_count == len(NEW_CATEGORIES)

def test_category_info():
    """Test get_category_info for each new category"""
    print_separator()
    print("TEST 3: Testing get_category_info")
    print_separator()
    
    success_count = 0
    for cat_info in NEW_CATEGORIES:
        category = cat_info["category"]
        
        print(f"\nTesting {category}...")
        result = get_category_info(category)
        
        if 'error' in result:
            print(f"  ✗ Error: {result['error']}")
        else:
            print(f"  ✓ Category: {result.get('category')}")
            print(f"    - stat_code: {result.get('stat_code')}")
            print(f"    - name: {result.get('name')}")
            print(f"    - default_cycle: {result.get('default_cycle')}")
            
            items = result.get('items', {})
            print(f"    - items count: {len(items)}")
            
            # Print first 3 items as sample
            if items:
                print("    - Sample items:")
                for i, (key, value) in enumerate(list(items.items())[:3]):
                    print(f"      {key}: {value.get('name', 'N/A')}")
            
            success_count += 1
    
    print(f"\nResult: {success_count}/{len(NEW_CATEGORIES)} categories working")
    return success_count == len(NEW_CATEGORIES)

def test_market_index():
    """Test get_market_index for each new category with actual data retrieval"""
    print_separator()
    print("TEST 4: Testing get_market_index (actual data retrieval)")
    print_separator()
    
    success_count = 0
    
    for cat_info in NEW_CATEGORIES:
        category = cat_info["category"]
        default_cycle = cat_info["default_cycle"]
        
        # Set appropriate date range based on cycle
        if default_cycle == "A":  # Annual
            start_date = "20150101"
            end_date = "20231231"
        elif default_cycle == "Q":  # Quarterly
            start_date = "20220101"
            end_date = "20231231"
        else:  # Monthly or Daily
            start_date = "20230101"
            end_date = "20231231"
        
        print(f"\nTesting {category} ({default_cycle}, {start_date}~{end_date})...")
        
        # First get category info to find an item_code
        cat_result = get_category_info(category)
        if 'error' in cat_result:
            print(f"  ✗ Error getting category info: {cat_result['error']}")
            continue
        
        items = cat_result.get('items', {})
        if not items:
            print(f"  ✗ No items found for category")
            continue
        
        # Use first item for testing
        first_item_key = list(items.keys())[0]
        first_item = items[first_item_key]
        item_code = first_item.get('code', first_item_key)
        item_name = first_item.get('name', 'Unknown')
        
        print(f"  Using item: {item_code} ({item_name})")
        
        # Now test get_market_index
        result = get_market_index(
            category=category,
            start_date=start_date,
            end_date=end_date,
            item_code=item_code,
            cycle=default_cycle
        )
        
        if 'error' in result:
            print(f"  ✗ Error: {result['error']}")
        else:
            stat_search = result.get('StatisticSearch', {})
            total_count = stat_search.get('list_total_count', 0)
            rows = stat_search.get('row', [])
            
            print(f"  ✓ Retrieved {total_count} data points")
            
            if rows:
                # Print first 3 data points
                print("  Sample data:")
                for row in rows[:3]:
                    time = row.get('TIME', 'N/A')
                    value = row.get('DATA_VALUE', 'N/A')
                    unit = row.get('UNIT_NAME', '')
                    print(f"    - {time}: {value} {unit}")
                
                success_count += 1
    
    print(f"\nResult: {success_count}/{len(NEW_CATEGORIES)} categories returning data")
    return success_count == len(NEW_CATEGORIES)

def main():
    print("\n" + "=" * 80)
    print("INTERNATIONAL INDICATORS TEST SUITE")
    print("Testing 5 new BOK ECOS API categories")
    print("=" * 80 + "\n")
    
    results = []
    
    # Test 1: BOK_MAPPING
    results.append(("BOK_MAPPING", test_bok_mapping()))
    
    # Test 2: StatisticItemList API
    results.append(("StatisticItemList", test_statistic_item_list()))
    
    # Test 3: get_category_info
    results.append(("get_category_info", test_category_info()))
    
    # Test 4: get_market_index
    results.append(("get_market_index", test_market_index()))
    
    # Summary
    print_separator()
    print("SUMMARY")
    print_separator()
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 All tests passed! Backend is ready for frontend integration.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

