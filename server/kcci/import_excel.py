"""
Excel 파일에서 KCCI 데이터 가져오기
KOBC CONTAINER COMPOSITE INDEX TIMESERIES 파일 파싱
"""

import os
import sys
from datetime import datetime

# 프로젝트 루트를 path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from kcci.models import (
    KCCIIndex, KCCIRouteIndex, KCCICollectionLog,
    init_kcci_database, get_kcci_session
)

# 항로 정보 (코드, 이름, 그룹, 가중치)
ROUTE_INFO = {
    'KCCI': {'name': 'Comprehensive Index', 'group': 'Index', 'weight': 100.0},
    'KUWI': {'name': 'USWC', 'group': 'Mainlane', 'weight': 15.0},
    'KUEI': {'name': 'USEC', 'group': 'Mainlane', 'weight': 10.0},
    'KNEI': {'name': 'Europe', 'group': 'Mainlane', 'weight': 10.0},
    'KMDI': {'name': 'Mediterranean', 'group': 'Mainlane', 'weight': 5.0},
    'KMEI': {'name': 'Middle East', 'group': 'Non-Mainlane', 'weight': 5.0},
    'KAUI': {'name': 'Australia', 'group': 'Non-Mainlane', 'weight': 5.0},
    'KLEI': {'name': 'Latin America East Coast', 'group': 'Non-Mainlane', 'weight': 5.0},
    'KLWI': {'name': 'Latin America West Coast', 'group': 'Non-Mainlane', 'weight': 5.0},
    'KSAI': {'name': 'South Africa', 'group': 'Non-Mainlane', 'weight': 2.5},
    'KWAI': {'name': 'West Africa', 'group': 'Non-Mainlane', 'weight': 2.5},
    'KCI': {'name': 'China', 'group': 'Intra Asia', 'weight': 15.0},
    'KJI': {'name': 'Japan', 'group': 'Intra Asia', 'weight': 10.0},
    'KSEI': {'name': 'South East Asia', 'group': 'Intra Asia', 'weight': 10.0},
}

# 항로 코드 순서 (Excel 컬럼 순서)
ROUTE_CODES = ['KCCI', 'KUWI', 'KUEI', 'KNEI', 'KMDI', 'KMEI', 'KAUI', 'KLEI', 'KLWI', 'KSAI', 'KWAI', 'KCI', 'KJI', 'KSEI']


def parse_date(date_val):
    """날짜 파싱 (YYYYMMDD -> date object)"""
    from datetime import date
    date_str = str(int(date_val))
    year = int(date_str[:4])
    month = int(date_str[4:6])
    day = int(date_str[6:8])
    return date(year, month, day)


def import_excel(excel_path: str, clear_existing: bool = True):
    """
    Excel 파일에서 KCCI 데이터 가져오기
    
    Args:
        excel_path: Excel 파일 경로
        clear_existing: 기존 데이터 삭제 여부
    """
    print(f"Reading Excel file: {excel_path}")
    
    # Excel 파일 읽기
    xls = pd.ExcelFile(excel_path)
    df = pd.read_excel(xls, sheet_name=xls.sheet_names[0], header=None)
    
    # 헤더 행 찾기 (DATE 컬럼이 있는 행)
    header_row = None
    for idx, row in df.iterrows():
        if 'DATE' in str(row.values):
            header_row = idx
            break
    
    if header_row is None:
        # 첫 번째 행이 헤더라고 가정
        header_row = 0
    
    # 컬럼명 설정
    df.columns = df.iloc[header_row].values
    df = df.iloc[header_row + 1:].reset_index(drop=True)
    
    print(f"Columns: {df.columns.tolist()}")
    print(f"Data rows: {len(df)}")
    
    # 데이터베이스 초기화
    init_kcci_database()
    session = get_kcci_session()
    
    try:
        if clear_existing:
            print("Clearing existing data...")
            session.query(KCCIRouteIndex).delete()
            session.query(KCCIIndex).delete()
            session.commit()
        
        # 데이터 파싱
        data_rows = []
        for idx, row in df.iterrows():
            try:
                date_val = row.get('DATE') or row.iloc[1]  # DATE 컬럼 또는 두 번째 컬럼
                if pd.isna(date_val):
                    continue
                    
                week_date = parse_date(date_val)
                
                row_data = {'week_date': week_date}
                for code in ROUTE_CODES:
                    if code in df.columns:
                        val = row[code]
                    else:
                        # 컬럼명이 다를 수 있으므로 인덱스로 접근
                        col_idx = ROUTE_CODES.index(code) + 2  # DATE 컬럼 다음부터
                        if col_idx < len(row):
                            val = row.iloc[col_idx]
                        else:
                            val = None
                    
                    if pd.notna(val):
                        row_data[code] = float(val)
                
                data_rows.append(row_data)
            except Exception as e:
                print(f"Error parsing row {idx}: {e}")
                continue
        
        # 날짜순 정렬 (오래된 것부터)
        data_rows.sort(key=lambda x: x['week_date'])
        
        print(f"Parsed {len(data_rows)} data rows")
        
        # 데이터 삽입
        comprehensive_count = 0
        route_count = 0
        
        for i, row_data in enumerate(data_rows):
            week_date = row_data['week_date']
            
            # 이전 주 데이터 가져오기
            prev_data = data_rows[i - 1] if i > 0 else None
            
            # 종합지수 (KCCI)
            if 'KCCI' in row_data:
                current_val = row_data['KCCI']
                prev_val = prev_data.get('KCCI') if prev_data else None
                change = current_val - prev_val if prev_val else None
                change_rate = (change / prev_val * 100) if prev_val and change is not None else None
                
                # 기존 데이터 확인
                existing = session.query(KCCIIndex).filter_by(week_date=week_date).first()
                if existing:
                    existing.current_index = current_val
                    existing.previous_index = prev_val
                    existing.weekly_change = change
                    existing.weekly_change_rate = change_rate
                else:
                    comp_index = KCCIIndex(
                        week_date=week_date,
                        index_code='KCCI',
                        index_name='KCCI Comprehensive Index',
                        current_index=current_val,
                        previous_index=prev_val,
                        weekly_change=change,
                        weekly_change_rate=round(change_rate, 2) if change_rate else None,
                        source_url='https://www.kobc.or.kr',
                        collected_at=datetime.now()
                    )
                    session.add(comp_index)
                comprehensive_count += 1
            
            # 항로별 지수
            for code in ROUTE_CODES[1:]:  # KCCI 제외
                if code not in row_data:
                    continue
                    
                current_val = row_data[code]
                prev_val = prev_data.get(code) if prev_data else None
                change = current_val - prev_val if prev_val else None
                change_rate = (change / prev_val * 100) if prev_val and change is not None else None
                
                route_info = ROUTE_INFO[code]
                
                # 기존 데이터 확인
                existing = session.query(KCCIRouteIndex).filter_by(
                    week_date=week_date,
                    route_code=code
                ).first()
                
                if existing:
                    existing.current_index = current_val
                    existing.previous_index = prev_val
                    existing.weekly_change = change
                    existing.weekly_change_rate = round(change_rate, 2) if change_rate else None
                    existing.weight = route_info['weight']
                else:
                    route_index = KCCIRouteIndex(
                        week_date=week_date,
                        route_group=route_info['group'],
                        route_code=code,
                        route_name=route_info['name'],
                        weight=route_info['weight'],
                        current_index=current_val,
                        previous_index=prev_val,
                        weekly_change=change,
                        weekly_change_rate=round(change_rate, 2) if change_rate else None,
                        source_url='https://www.kobc.or.kr',
                        collected_at=datetime.now()
                    )
                    session.add(route_index)
                route_count += 1
        
        # 수집 로그 기록
        log = KCCICollectionLog(
            executed_at=datetime.now(),
            is_success=1,
            route_count=route_count,
            error_message=f'Imported {comprehensive_count} comprehensive and {route_count} route records from {os.path.basename(excel_path)}'
        )
        session.add(log)
        
        session.commit()
        
        print(f"[OK] Import completed!")
        print(f"   - Comprehensive index records: {comprehensive_count}")
        print(f"   - Route index records: {route_count}")
        
        return True
        
    except Exception as e:
        session.rollback()
        print(f"[ERROR] Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        # 기본 파일 경로
        excel_path = os.path.join(
            os.path.dirname(__file__),
            'KOBC CONTAINER COMPOSITE INDEX TIMESERIES_20260102161859.xls'
        )
    else:
        excel_path = sys.argv[1]
    
    if not os.path.exists(excel_path):
        print(f"File not found: {excel_path}")
        sys.exit(1)
    
    import_excel(excel_path)

