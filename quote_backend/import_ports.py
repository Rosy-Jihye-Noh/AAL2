# -*- coding: utf-8 -*-
"""
Import Port Data from Excel Files to Database
Supports both Air Ports and Sea Ports
"""

import pandas as pd
import sys
import os

# Set console encoding
sys.stdout.reconfigure(encoding='utf-8')

from database import SessionLocal, engine
from models import Port, Base

# Excel file paths
AIR_PORT_PATH = r"D:\Planning_data\네오헬리우스MTO\기획자료\MDM\PORT\PORT CODE DB_ALIGNED.xls"
SEA_PORT_PATH = r"D:\Planning_data\네오헬리우스MTO\기획자료\MDM\PORT\PORT CODE_DB2_ALIGNED.xls"


def import_air_ports(db):
    """Import air port data from Excel"""
    try:
        df = pd.read_excel(AIR_PORT_PATH, engine='xlrd')
        print(f"[AIR] File loaded: {len(df)} rows")
        
        added_count = 0
        for idx, row in df.iterrows():
            code = row['Location']
            name = row['Location Name']
            country_code = row.get('Country', None)
            country_name = row.get('Country Name', None)
            
            if pd.isna(code) or pd.isna(name):
                continue
            
            code = str(code).strip().upper()
            name = str(name).strip()
            
            if pd.isna(country_code):
                country_code = 'XX'
            else:
                country_code = str(country_code).strip().upper()[:2]
            
            if pd.isna(country_name):
                country_name = 'Unknown'
            else:
                country_name = str(country_name).strip()
            
            port = Port(
                code=code,
                name=name,
                name_ko=None,
                country=country_name,
                country_code=country_code,
                port_type='air',
                is_active=True
            )
            db.add(port)
            added_count += 1
            
            if added_count % 500 == 0:
                db.commit()
                print(f"[AIR] Progress: {added_count} ports...")
        
        db.commit()
        print(f"[AIR] Completed: {added_count} air ports added")
        return added_count
        
    except Exception as e:
        print(f"[AIR ERROR] {e}")
        return 0


def import_sea_ports(db):
    """Import sea port data from Excel"""
    try:
        df = pd.read_excel(SEA_PORT_PATH, engine='xlrd')
        print(f"[SEA] File loaded: {len(df)} rows")
        
        added_count = 0
        skipped_count = 0
        
        for idx, row in df.iterrows():
            code = row['Location']
            name = row['Location Name']
            country_code = row.get('Country', None)
            country_name = row.get('Country Name', None)
            
            if pd.isna(code) or pd.isna(name):
                skipped_count += 1
                continue
            
            code = str(code).strip().upper()
            name = str(name).strip()
            
            # Check if same code already exists (might be air port)
            existing = db.query(Port).filter(Port.code == code).first()
            if existing:
                # Update to 'both' if it was 'air'
                if existing.port_type == 'air':
                    existing.port_type = 'both'
                skipped_count += 1
                continue
            
            if pd.isna(country_code):
                country_code = 'XX'
            else:
                country_code = str(country_code).strip().upper()[:2]
            
            if pd.isna(country_name):
                country_name = 'Unknown'
            else:
                country_name = str(country_name).strip()
            
            port = Port(
                code=code,
                name=name,
                name_ko=None,
                country=country_name,
                country_code=country_code,
                port_type='ocean',
                is_active=True
            )
            db.add(port)
            added_count += 1
            
            if added_count % 5000 == 0:
                db.commit()
                print(f"[SEA] Progress: {added_count} ports...")
        
        db.commit()
        print(f"[SEA] Completed: {added_count} sea ports added, {skipped_count} skipped/updated")
        return added_count
        
    except Exception as e:
        print(f"[SEA ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 0


def import_all_ports():
    """Import all ports (air and sea) to database"""
    print("\n" + "="*50)
    print("PORT DATA IMPORT")
    print("="*50 + "\n")
    
    db = SessionLocal()
    
    try:
        # Clear existing data
        existing_count = db.query(Port).count()
        print(f"[INFO] Existing ports in DB: {existing_count}")
        
        db.query(Port).delete()
        db.commit()
        print(f"[INFO] Cleared existing port data\n")
        
        # Import air ports first
        air_count = import_air_ports(db)
        print()
        
        # Import sea ports
        sea_count = import_sea_ports(db)
        print()
        
        # Summary
        total_in_db = db.query(Port).count()
        air_in_db = db.query(Port).filter(Port.port_type == 'air').count()
        sea_in_db = db.query(Port).filter(Port.port_type == 'ocean').count()
        both_in_db = db.query(Port).filter(Port.port_type == 'both').count()
        
        print("="*50)
        print("IMPORT SUMMARY")
        print("="*50)
        print(f"Total ports in DB: {total_in_db}")
        print(f"  - Air ports:  {air_in_db}")
        print(f"  - Sea ports:  {sea_in_db}")
        print(f"  - Both types: {both_in_db}")
        print("="*50)
        
        # Show samples
        print("\n[SAMPLE] Air ports:")
        for p in db.query(Port).filter(Port.port_type == 'air').limit(5).all():
            print(f"  {p.code}: {p.name} ({p.country_code})")
        
        print("\n[SAMPLE] Sea ports:")
        for p in db.query(Port).filter(Port.port_type == 'ocean').limit(5).all():
            print(f"  {p.code}: {p.name} ({p.country_code})")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    import_all_ports()

