"""
GDELT 특정 날짜 데이터 테스트 스크립트
2025-12-22 (또는 20241222) 날짜의 모든 파일을 찾아서 파싱
"""

import sys
from pathlib import Path
import gdelt_backend

def test_date_alerts(target_date="20241222"):
    """
    특정 날짜의 GDELT 데이터를 모두 호출하여 테스트
    
    Args:
        target_date: YYYYMMDD 형식의 날짜 (예: "20241222")
    """
    print("=" * 70)
    print(f"Testing GDELT Data for Date: {target_date}")
    print("=" * 70)
    
    # GDELT 기본 경로
    base_path = Path(r"D:\GDELT DB")
    if not base_path.exists():
        print(f"ERROR: GDELT base path does not exist: {base_path}")
        return
    
    # 날짜 디렉토리 경로
    date_dir = base_path / "default" / "events" / target_date
    
    if not date_dir.exists():
        print(f"ERROR: Date directory does not exist: {date_dir}")
        print(f"\nAvailable date directories:")
        events_dir = base_path / "default" / "events"
        if events_dir.exists():
            date_dirs = sorted([d.name for d in events_dir.iterdir() if d.is_dir()])
            if date_dirs:
                print(f"  Found {len(date_dirs)} date directories:")
                for d in date_dirs[:20]:  # 최대 20개만 표시
                    print(f"    - {d}")
                if len(date_dirs) > 20:
                    print(f"    ... and {len(date_dirs) - 20} more")
            else:
                print("  No date directories found")
        return
    
    print(f"\nDate Directory: {date_dir}")
    print(f"Directory exists: {date_dir.exists()}")
    
    # 해당 날짜의 모든 파일 찾기
    all_files = []
    
    # .tsv.gz 파일 찾기
    tsv_files = list(date_dir.glob("*.export.CSV.tsv.gz"))
    print(f"\nFound {len(tsv_files)} .tsv.gz files")
    all_files.extend(tsv_files)
    
    # .zip 파일 찾기
    zip_files = list(date_dir.glob("*.export.CSV.zip"))
    print(f"Found {len(zip_files)} .zip files")
    all_files.extend(zip_files)
    
    if len(all_files) == 0:
        print(f"\nNo GDELT files found in {date_dir}")
        return
    
    print(f"\nTotal files found: {len(all_files)}")
    for i, file_path in enumerate(all_files, 1):
        try:
            file_size_mb = file_path.stat().st_size / 1024 / 1024
            print(f"  {i}. {file_path.name} ({file_size_mb:.2f} MB)")
        except Exception as e:
            print(f"  {i}. {file_path.name} (size unknown: {e})")
    
    # 각 파일 파싱
    all_alerts = []
    print(f"\n{'=' * 70}")
    print("Parsing Files...")
    print(f"{'=' * 70}")
    
    for file_path in all_files:
        print(f"\nParsing: {file_path.name}")
        try:
            alerts = gdelt_backend.parse_gdelt_csv(file_path, threshold=-5.0)
            print(f"  ✓ Found {len(alerts)} alerts (GoldsteinScale <= -5.0)")
            all_alerts.extend(alerts)
        except Exception as e:
            print(f"  ✗ ERROR parsing file: {e}")
            import traceback
            traceback.print_exc()
    
    # 결과 요약
    print(f"\n{'=' * 70}")
    print("Summary")
    print(f"{'=' * 70}")
    print(f"Total files parsed: {len(all_files)}")
    print(f"Total alerts found: {len(all_alerts)}")
    
    if len(all_alerts) > 0:
        # 위험도 순으로 정렬
        all_alerts.sort(key=lambda x: x.get("scale", 0))
        
        print(f"\nTop 10 Most Critical Alerts:")
        for i, alert in enumerate(all_alerts[:10], 1):
            scale = alert.get('scale', 0)
            lat = alert.get('lat', 'N/A')
            lng = alert.get('lng', 'N/A')
            name = alert.get('name', 'N/A')
            if len(name) > 50:
                name = name[:47] + "..."
            print(f"  {i}. Scale: {scale:.2f}, Location: ({lat}, {lng})")
            print(f"     Name: {name}")
        
        # 통계
        scales = [a.get('scale', 0) for a in all_alerts if a.get('scale') is not None]
        if scales:
            print(f"\nStatistics:")
            print(f"  - Min scale: {min(scales):.2f}")
            print(f"  - Max scale: {max(scales):.2f}")
            print(f"  - Average scale: {sum(scales)/len(scales):.2f}")
        
        # 날짜 정보 확인
        print(f"\nDate information in alerts:")
        dates_found = set()
        for alert in all_alerts:
            if 'date' in alert and alert['date']:
                dates_found.add(alert['date'])
        if dates_found:
            print(f"  Found dates: {sorted(dates_found)}")
        else:
            print(f"  ⚠ WARNING: No date information in alerts!")
            print(f"  (Date should be extracted from filename or CSV column)")
        
        # 위치별 통계
        print(f"\nLocation Statistics:")
        locations = {}
        for alert in all_alerts:
            lat = alert.get('lat')
            lng = alert.get('lng')
            if lat and lng:
                key = f"{lat:.1f},{lng:.1f}"
                locations[key] = locations.get(key, 0) + 1
        
        if locations:
            sorted_locations = sorted(locations.items(), key=lambda x: x[1], reverse=True)
            print(f"  Top 5 locations by alert count:")
            for loc, count in sorted_locations[:5]:
                print(f"    - {loc}: {count} alerts")
    
    print(f"\n{'=' * 70}")
    print("Test Complete")
    print(f"{'=' * 70}")

if __name__ == "__main__":
    # 명령줄 인자로 날짜 받기 (기본값: 20241222)
    target_date = sys.argv[1] if len(sys.argv) > 1 else "20241222"
    
    # 날짜 형식 변환 (YYYY-MM-DD -> YYYYMMDD)
    if "-" in target_date:
        target_date = target_date.replace("-", "")
    
    # 날짜 형식 검증
    if len(target_date) != 8 or not target_date.isdigit():
        print(f"ERROR: Invalid date format: {target_date}")
        print("Expected format: YYYYMMDD (e.g., 20241222)")
        sys.exit(1)
    
    test_date_alerts(target_date)