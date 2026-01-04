"""
Excel 파일에서 Shipping Indices 데이터 가져오기 (SCFI, CCFI, BDI)

엑셀 파일 형식:
- 첫 행: 구분, 운임지수, 등록일
- 구분: 지수명 (SCFI, CCFI, BDI)
- 운임지수: 숫자
- 등록일: yyyy-mm-dd
"""

import os
import sys
from datetime import datetime, date

# 프로젝트 루트를 path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

# Import models directly to avoid circular dependency with api.py
try:
    from shipping_indices.models import (
        SCFIIndex, CCFIIndex, BDIIndex,
        init_shipping_indices_database, get_shipping_indices_session
    )
except ImportError:
    from models import (
        SCFIIndex, CCFIIndex, BDIIndex,
        init_shipping_indices_database, get_shipping_indices_session
    )


def parse_date(date_val):
    """날짜 파싱 (yyyy-mm-dd 또는 datetime -> date object)"""
    if isinstance(date_val, datetime):
        return date_val.date()
    if isinstance(date_val, date):
        return date_val
    
    date_str = str(date_val).strip()
    
    # yyyy-mm-dd 형식
    if '-' in date_str:
        parts = date_str.split('-')
        return date(int(parts[0]), int(parts[1]), int(parts[2]))
    
    # yyyymmdd 형식
    if len(date_str) == 8 and date_str.isdigit():
        return date(int(date_str[:4]), int(date_str[4:6]), int(date_str[6:8]))
    
    raise ValueError(f"Cannot parse date: {date_val}")


def import_scfi_excel(excel_path: str, clear_existing: bool = True):
    """
    SCFI Excel 파일에서 데이터 가져오기
    
    Args:
        excel_path: Excel 파일 경로
        clear_existing: 기존 데이터 삭제 여부
    """
    print(f"[SCFI] Reading Excel file: {excel_path}")
    
    # Excel 파일 읽기
    df = pd.read_excel(excel_path)
    
    # 컬럼명 확인 및 매핑
    print(f"[SCFI] Original columns: {df.columns.tolist()}")
    
    # 컬럼명을 영어로 변환 (순서 기반)
    df.columns = ['index_code', 'index_value', 'index_date']
    
    print(f"[SCFI] Data rows: {len(df)}")
    
    # 데이터베이스 초기화
    init_shipping_indices_database()
    session = get_shipping_indices_session()
    
    try:
        if clear_existing:
            print("[SCFI] Clearing existing data...")
            session.query(SCFIIndex).delete()
            session.commit()
        
        # 데이터 파싱
        data_rows = []
        for idx, row in df.iterrows():
            try:
                if pd.isna(row['index_date']) or pd.isna(row['index_value']):
                    continue
                
                index_date = parse_date(row['index_date'])
                index_value = float(row['index_value'])
                
                data_rows.append({
                    'index_date': index_date,
                    'index_value': index_value
                })
            except Exception as e:
                print(f"[SCFI] Error parsing row {idx}: {e}")
                continue
        
        # 날짜순 정렬 (오래된 것부터)
        data_rows.sort(key=lambda x: x['index_date'])
        
        print(f"[SCFI] Parsed {len(data_rows)} data rows")
        
        # 데이터 삽입
        count = 0
        for i, row_data in enumerate(data_rows):
            index_date = row_data['index_date']
            current_val = row_data['index_value']
            
            # 이전 데이터
            prev_val = data_rows[i - 1]['index_value'] if i > 0 else None
            change = current_val - prev_val if prev_val else None
            change_rate = (change / prev_val * 100) if prev_val and change is not None else None
            
            # 기존 데이터 확인
            existing = session.query(SCFIIndex).filter_by(index_date=index_date).first()
            if existing:
                existing.current_index = current_val
                existing.previous_index = prev_val
                existing.change = change
                existing.change_rate = round(change_rate, 2) if change_rate else None
            else:
                scfi = SCFIIndex(
                    index_date=index_date,
                    index_code='SCFI',
                    index_name='Shanghai Containerized Freight Index',
                    current_index=current_val,
                    previous_index=prev_val,
                    change=change,
                    change_rate=round(change_rate, 2) if change_rate else None,
                    source='Shanghai Shipping Exchange (SSE)',
                    collected_at=datetime.now()
                )
                session.add(scfi)
            count += 1
        
        session.commit()
        
        print(f"[SCFI] Import completed! {count} records imported.")
        return True
        
    except Exception as e:
        session.rollback()
        print(f"[SCFI] Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()


def import_ccfi_excel(excel_path: str, clear_existing: bool = True):
    """
    CCFI Excel 파일에서 데이터 가져오기
    """
    print(f"[CCFI] Reading Excel file: {excel_path}")
    
    df = pd.read_excel(excel_path)
    df.columns = ['index_code', 'index_value', 'index_date']
    
    print(f"[CCFI] Data rows: {len(df)}")
    
    init_shipping_indices_database()
    session = get_shipping_indices_session()
    
    try:
        if clear_existing:
            print("[CCFI] Clearing existing data...")
            session.query(CCFIIndex).delete()
            session.commit()
        
        data_rows = []
        for idx, row in df.iterrows():
            try:
                if pd.isna(row['index_date']) or pd.isna(row['index_value']):
                    continue
                
                index_date = parse_date(row['index_date'])
                index_value = float(row['index_value'])
                
                data_rows.append({
                    'index_date': index_date,
                    'index_value': index_value
                })
            except Exception as e:
                print(f"[CCFI] Error parsing row {idx}: {e}")
                continue
        
        data_rows.sort(key=lambda x: x['index_date'])
        print(f"[CCFI] Parsed {len(data_rows)} data rows")
        
        count = 0
        for i, row_data in enumerate(data_rows):
            index_date = row_data['index_date']
            current_val = row_data['index_value']
            
            prev_val = data_rows[i - 1]['index_value'] if i > 0 else None
            change = current_val - prev_val if prev_val else None
            change_rate = (change / prev_val * 100) if prev_val and change is not None else None
            
            existing = session.query(CCFIIndex).filter_by(index_date=index_date).first()
            if existing:
                existing.current_index = current_val
                existing.previous_index = prev_val
                existing.change = change
                existing.change_rate = round(change_rate, 2) if change_rate else None
            else:
                ccfi = CCFIIndex(
                    index_date=index_date,
                    index_code='CCFI',
                    index_name='China Containerized Freight Index',
                    current_index=current_val,
                    previous_index=prev_val,
                    change=change,
                    change_rate=round(change_rate, 2) if change_rate else None,
                    source='Shanghai Shipping Exchange (SSE)',
                    collected_at=datetime.now()
                )
                session.add(ccfi)
            count += 1
        
        session.commit()
        print(f"[CCFI] Import completed! {count} records imported.")
        return True
        
    except Exception as e:
        session.rollback()
        print(f"[CCFI] Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()


def import_bdi_excel(excel_path: str, clear_existing: bool = True):
    """
    BDI Excel 파일에서 데이터 가져오기
    """
    print(f"[BDI] Reading Excel file: {excel_path}")
    
    df = pd.read_excel(excel_path)
    df.columns = ['index_code', 'index_value', 'index_date']
    
    print(f"[BDI] Data rows: {len(df)}")
    
    init_shipping_indices_database()
    session = get_shipping_indices_session()
    
    try:
        if clear_existing:
            print("[BDI] Clearing existing data...")
            session.query(BDIIndex).delete()
            session.commit()
        
        data_rows = []
        for idx, row in df.iterrows():
            try:
                if pd.isna(row['index_date']) or pd.isna(row['index_value']):
                    continue
                
                index_date = parse_date(row['index_date'])
                index_value = float(row['index_value'])
                
                data_rows.append({
                    'index_date': index_date,
                    'index_value': index_value
                })
            except Exception as e:
                print(f"[BDI] Error parsing row {idx}: {e}")
                continue
        
        data_rows.sort(key=lambda x: x['index_date'])
        print(f"[BDI] Parsed {len(data_rows)} data rows")
        
        count = 0
        for i, row_data in enumerate(data_rows):
            index_date = row_data['index_date']
            current_val = row_data['index_value']
            
            prev_val = data_rows[i - 1]['index_value'] if i > 0 else None
            change = current_val - prev_val if prev_val else None
            change_rate = (change / prev_val * 100) if prev_val and change is not None else None
            
            existing = session.query(BDIIndex).filter_by(index_date=index_date).first()
            if existing:
                existing.current_index = current_val
                existing.previous_index = prev_val
                existing.change = change
                existing.change_rate = round(change_rate, 2) if change_rate else None
            else:
                bdi = BDIIndex(
                    index_date=index_date,
                    index_code='BDI',
                    index_name='Baltic Dry Index',
                    current_index=current_val,
                    previous_index=prev_val,
                    change=change,
                    change_rate=round(change_rate, 2) if change_rate else None,
                    source='Baltic Exchange',
                    collected_at=datetime.now()
                )
                session.add(bdi)
            count += 1
        
        session.commit()
        print(f"[BDI] Import completed! {count} records imported.")
        return True
        
    except Exception as e:
        session.rollback()
        print(f"[BDI] Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()


def import_all():
    """모든 지수 Excel 파일 가져오기"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    scfi_path = os.path.join(base_dir, 'scfi', 'SCFI.xlsx')
    ccfi_path = os.path.join(base_dir, 'ccfi', 'CCFI.xlsx')
    bdi_path = os.path.join(base_dir, 'bdi', 'BDI.xlsx')
    
    results = {}
    
    if os.path.exists(scfi_path):
        results['scfi'] = import_scfi_excel(scfi_path)
    else:
        print(f"[SCFI] File not found: {scfi_path}")
        results['scfi'] = False
    
    if os.path.exists(ccfi_path):
        results['ccfi'] = import_ccfi_excel(ccfi_path)
    else:
        print(f"[CCFI] File not found: {ccfi_path}")
        results['ccfi'] = False
    
    if os.path.exists(bdi_path):
        results['bdi'] = import_bdi_excel(bdi_path)
    else:
        print(f"[BDI] File not found: {bdi_path}")
        results['bdi'] = False
    
    return results


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        index_type = sys.argv[1].upper()
        if len(sys.argv) > 2:
            file_path = sys.argv[2]
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            file_path = os.path.join(base_dir, index_type.lower(), f'{index_type}.xlsx')
        
        if index_type == 'SCFI':
            import_scfi_excel(file_path)
        elif index_type == 'CCFI':
            import_ccfi_excel(file_path)
        elif index_type == 'BDI':
            import_bdi_excel(file_path)
        else:
            print(f"Unknown index type: {index_type}")
            print("Usage: python import_excel.py [SCFI|CCFI|BDI] [file_path]")
    else:
        # 모든 지수 가져오기
        import_all()

