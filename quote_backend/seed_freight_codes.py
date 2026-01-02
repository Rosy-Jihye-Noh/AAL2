"""
Freight Code Master Data Seed Script
운임 코드, 카테고리, 단위 초기 데이터 삽입

Usage:
    python seed_freight_codes.py
"""

from database import SessionLocal, engine
from models import Base, FreightCategory, FreightCode, FreightUnit, FreightCodeUnit

# Create tables if not exist
Base.metadata.create_all(bind=engine)


def seed_freight_data():
    db = SessionLocal()
    
    try:
        # ==========================================
        # 1. Freight Categories (4개)
        # ==========================================
        categories_data = [
            {"code": "OCEAN", "name_en": "Ocean Freight", "name_ko": "해상운임", "shipping_types": "ocean", "sort_order": 1},
            {"code": "AIR", "name_en": "Air Freight", "name_ko": "항공운임", "shipping_types": "air", "sort_order": 2},
            {"code": "PORT_CHARGES", "name_en": "Port Charges", "name_ko": "항만비용", "shipping_types": "ocean,air", "sort_order": 3},
            {"code": "LOCAL_CHARGES", "name_en": "Local Charges", "name_ko": "로컬비용", "shipping_types": "ocean,air,truck", "sort_order": 4},
        ]
        
        # Check if already seeded
        existing = db.query(FreightCategory).first()
        if existing:
            print("[SKIP] Freight categories already exist. Skipping category seed.")
        else:
            for cat_data in categories_data:
                cat = FreightCategory(**cat_data)
                db.add(cat)
            db.commit()
            print(f"[OK] Seeded {len(categories_data)} freight categories")
        
        # Get category IDs
        categories = {c.code: c.id for c in db.query(FreightCategory).all()}
        
        # ==========================================
        # 2. Freight Units (9개)
        # ==========================================
        units_data = [
            {"code": "R/TON", "name_en": "Revenue Ton", "name_ko": "운임톤", "sort_order": 1},
            {"code": "CNTR", "name_en": "Container", "name_ko": "컨테이너", "sort_order": 2},
            {"code": "G.W", "name_en": "Gross Weight", "name_ko": "총중량", "sort_order": 3},
            {"code": "C.W", "name_en": "Chargeable Weight", "name_ko": "청구중량", "sort_order": 4},
            {"code": "Day", "name_en": "Day", "name_ko": "일", "sort_order": 5},
            {"code": "B/L(AWB)", "name_en": "Bill of Lading / Air Waybill", "name_ko": "선하증권/항공화물운송장", "sort_order": 6},
            {"code": "Pallet", "name_en": "Pallet", "name_ko": "팔레트", "sort_order": 7},
            {"code": "Box", "name_en": "Box", "name_ko": "박스", "sort_order": 8},
            {"code": "Shipment", "name_en": "Shipment", "name_ko": "건", "sort_order": 9},
        ]
        
        existing_units = db.query(FreightUnit).first()
        if existing_units:
            print("[SKIP] Freight units already exist. Skipping unit seed.")
        else:
            for unit_data in units_data:
                unit = FreightUnit(**unit_data)
                db.add(unit)
            db.commit()
            print(f"[OK] Seeded {len(units_data)} freight units")
        
        # Get unit IDs
        units = {u.code: u.id for u in db.query(FreightUnit).all()}
        
        # ==========================================
        # 3. Freight Codes (66개)
        # ==========================================
        # Format: (code, category_code, group, name_en, name_ko, vat, currency)
        # All codes have Y/N VAT -> all have same units: R/TON, CNTR, G.W, C.W, Day, B/L(AWB), Pallet, Box, Shipment
        
        freight_codes_data = [
            # ===== OCEAN Category =====
            ("FRT", "OCEAN", "FREIGHT", "OCEAN FREIGHT", "해상 운임", False, "USD"),
            ("BAF", "OCEAN", "SURCHARGE", "BUNKER ADJUSTMENT FACTOR", "유류할증료", False, "USD"),
            ("LSS", "OCEAN", "SURCHARGE", "LOW SULPHUR FUEL SURCHARGE", "저유황유할증료", False, "USD"),
            ("CAF", "OCEAN", "SURCHARGE", "CURRENCY ADJUSTMENT FACTOR", "통화할증료", False, "USD"),
            ("EBS", "OCEAN", "SURCHARGE", "EMERGENCY BUNKER SURCHARGE", "긴급 유류할증료", False, "USD"),
            ("CRS", "OCEAN", "SURCHARGE", "EMERGENCY COST RECOVERY SURCHARGE", "운임보전료", False, "USD"),
            ("BBF", "OCEAN", "SURCHARGE", "BREAK BULK FEE", "벌크화물 취급 수수료", False, "USD"),
            ("CIC", "OCEAN", "SURCHARGE", "CONTAINER IMBALANCE CHARGE", "컨테이너 불균형 할증료", False, "USD"),
            ("EPC", "OCEAN", "SURCHARGE", "EMPTY POSITIONING CHARGE", "컨테이너 수급 불균형 할증료", False, "USD"),
            ("WRS", "OCEAN", "SURCHARGE", "WAR RISK SURCHARGE", "전쟁 할증료", False, "USD"),
            ("12D", "OCEAN", "TRUCKING", "12F DRAYAGE", "10FT 컨테이너 셔틀비용(장거리)", False, "KRW"),
            ("12S", "OCEAN", "TRUCKING", "12F SHORT DRAYAGE", "10FT 컨테이너 셔틀비용(근거리)", False, "KRW"),
            ("20D", "OCEAN", "TRUCKING", "20F DRAYAGE", "20FT 컨테이너 셔틀비용(장거리)", False, "KRW"),
            ("20S", "OCEAN", "TRUCKING", "20F SHORT DRAYAGE", "20FT 컨테이너 셔틀비용(근거리)", False, "KRW"),
            ("40D", "OCEAN", "TRUCKING", "40F DRAYAGE", "40FT 컨테이너 셔틀비용(장거리)", False, "KRW"),
            ("40S", "OCEAN", "TRUCKING", "40F SHORT DRAYAGE", "40FT 컨테이너 셔틀비용(근거리)", False, "KRW"),
            ("DYF", "OCEAN", "TRUCKING", "DRAYAGE FEE", "컨테이너 셔틀비용(기타)", False, "KRW"),
            ("DRS", "OCEAN", "ETC", "DRAYAGE RECOVERY CHARGE", "컨테이너 서틀 할증료", False, "KRW"),
            ("CCC", "OCEAN", "ETC", "CONTAINER CLEANING CHARGE", "컨테이너 세척 비용", False, "KRW"),
            ("CSC", "OCEAN", "ETC", "CONTAINER SHIFT CHARGE", "컨테이너 이동 수수료", False, "KRW"),
            ("DEM", "OCEAN", "ETC", "DEMURRAGE", "체선료", False, "KRW"),
            ("DET", "OCEAN", "ETC", "DETENTION", "지체료", False, "KRW"),
            ("DEV", "OCEAN", "ETC", "DEVANNING CHARGE", "컨테이너 적출료", False, "KRW"),
            ("LAS", "OCEAN", "ETC", "LASHING & SHORING CHARGE", "컨테이너 내부 고정작업료", False, "KRW"),
            ("LFO", "OCEAN", "ETC", "LIFT ON OFF CHARGE", "상하역료", False, "KRW"),
            ("PFS", "OCEAN", "ETC", "PORT FACILITY SECURITY CHARGE", "항만보안시설사용료", False, "KRW"),
            ("PSF", "OCEAN", "ETC", "PORT SAFETY MANAGEMENT FEE", "항만안전관리비", False, "KRW"),
            ("SCC", "OCEAN", "ETC", "STEVEDORING CHARGE", "하역비", False, "KRW"),
            ("SCG", "OCEAN", "ETC", "OCEAN CHARGE", "컨테이너 씰 비용", False, "KRW"),
            ("SCR", "OCEAN", "ETC", "SCREENING", "보안검색료", False, "KRW"),
            ("SRR", "OCEAN", "DOCUMENT", "SURRENDER CHARGE", "SURRENDER B/L 발급 수수료", False, "KRW"),
            
            # ===== PORT CHARGES Category =====
            ("CY", "PORT_CHARGES", "PORT", "CONTAINER YARD CHARGE", "컨테이너 장치장 사용료", False, "KRW"),
            ("CFS", "PORT_CHARGES", "PORT", "CONTAINER FREIGHT STATION CHARGE", "컨테이너 화물 집하장 사용료", False, "KRW"),
            ("THC", "PORT_CHARGES", "PORT", "TERMINAL HANDLING CHARGE", "터미널 작업비", False, "KRW"),
            ("WHC", "PORT_CHARGES", "PORT", "WHARFAGE", "부두사용료", False, "KRW"),
            ("VAN", "PORT_CHARGES", "ETC", "VANNING CHARGE", "컨테이너 적입료", False, "KRW"),
            ("RVS", "PORT_CHARGES", "WAREHOUSE", "REEFER VAN STORAGE CHARGE", "리퍼 컨테이너 보관료", False, "KRW"),
            ("CVS", "PORT_CHARGES", "WAREHOUSE", "CONTAINER STORAGE CHARGE", "컨테이너 보관료", False, "KRW"),
            ("HSR", "PORT_CHARGES", "ETC", "CONTAINER GATE OUT CHARGE", "컨테이너 반출료", False, "KRW"),
            
            # ===== LOCAL CHARGES Category =====
            ("DOO", "LOCAL_CHARGES", "DOCUMENT", "D/O CHARGE", "D/O 발급 비용", False, "KRW"),
            ("DOC", "LOCAL_CHARGES", "DOCUMENT", "DOCUMENT FEE", "서류 발급 비용", False, "KRW"),
            ("EDI", "LOCAL_CHARGES", "DOCUMENT", "EDI FEE", "EDI 전송 수수료", False, "KRW"),
            ("CNF", "LOCAL_CHARGES", "DOCUMENT", "CORRECTION FEE", "정정 수수료", False, "KRW"),
            ("AFS", "LOCAL_CHARGES", "DOCUMENT", "ADVANCED FILING SURCHARGE", "AFR 신고 비용", False, "USD"),
            ("AMS", "LOCAL_CHARGES", "DOCUMENT", "AUTOMATED MANIFEST SYSTEM", "AMS 신고 비용", False, "USD"),
            ("CHF", "LOCAL_CHARGES", "CUSTOMS", "CUSTOMS HANDLING FEE", "통관 수수료", False, "KRW"),
            ("HDC", "LOCAL_CHARGES", "DOCUMENT", "HANDLING CHARGE", "업무 처리 수수료", False, "KRW"),
            ("TRO", "LOCAL_CHARGES", "TRUCKING", "TRUCKING CHARGE", "내륙운송료", False, "KRW"),
            ("BOS", "LOCAL_CHARGES", "TRUCKING", "BONDED TRANSPORTATION FEE", "보세 운송료", False, "KRW"),
            ("FLK", "LOCAL_CHARGES", "TRUCKING", "FORK LIFT WORK", "지게차 작업료", False, "KRW"),
            ("CNL", "LOCAL_CHARGES", "ETC", "CANCEL CHARGE", "취소 수수료", False, "KRW"),
            ("HWY", "LOCAL_CHARGES", "ETC", "HIGHWAY FEE", "고속도로 통행료", False, "KRW"),
            ("PSR", "LOCAL_CHARGES", "ETC", "PROFIT SHARE FEE", "이익분배금", False, "KRW"),
            ("RAI", "LOCAL_CHARGES", "ETC", "RADIOACTIVE INSPECTION FEE", "방사능 검사 수수료", False, "KRW"),
            ("TAX", "LOCAL_CHARGES", "TAX", "CONSUMPTION TAX", "소비세", False, "KRW"),
            ("DTY", "LOCAL_CHARGES", "TAX", "DUTY", "관세", False, "KRW"),
            ("INP", "LOCAL_CHARGES", "INSURANCE", "INSURANCE FEE", "보험료", False, "KRW"),
            ("PAC", "LOCAL_CHARGES", "PACKING", "PACKING CHARGE", "화물 포장료", False, "KRW"),
            ("WCO", "LOCAL_CHARGES", "WAREHOUSE", "WAREHOUSE STORAGE CHARGE", "창고 보관료", False, "KRW"),
            
            # ===== AIR Category =====
            ("AFT", "AIR", "FREIGHT", "AIR FREIGHT", "항공 운임", False, "USD"),
            ("FSC", "AIR", "SURCHARGE", "FUEL SURCHARGE", "유류할증료", False, "USD"),
            ("SSC", "AIR", "SURCHARGE", "SECURITY CHARGE", "보안할증료", False, "USD"),
            ("PSC", "AIR", "SURCHARGE", "PEAK SEASON CHARGE", "성수기할증료", False, "USD"),
            ("RAC", "AIR", "SURCHARGE", "DG SURCHARGE", "위험물할증료", False, "USD"),
            ("CGC", "AIR", "SURCHARGE", "CGC CHARGE", "AWB 발행 비용", False, "KRW"),
            ("ATHC", "AIR", "AIRPORT", "TERMINAL HANDLING CHARGE", "터미널 작업비", False, "KRW"),
        ]
        
        existing_codes = db.query(FreightCode).first()
        if existing_codes:
            print("[SKIP] Freight codes already exist. Skipping code seed.")
        else:
            for idx, (code, cat_code, group, name_en, name_ko, vat, currency) in enumerate(freight_codes_data):
                freight_code = FreightCode(
                    code=code,
                    category_id=categories.get(cat_code),
                    group_name=group,
                    name_en=name_en,
                    name_ko=name_ko,
                    vat_applicable=vat,
                    default_currency=currency,
                    sort_order=idx + 1
                )
                db.add(freight_code)
            db.commit()
            print(f"[OK] Seeded {len(freight_codes_data)} freight codes")
        
        # ==========================================
        # 4. Freight Code - Unit Mapping
        # ==========================================
        # All codes can use all units based on the provided data
        
        existing_mapping = db.query(FreightCodeUnit).first()
        if existing_mapping:
            print("[SKIP] Freight code-unit mappings already exist. Skipping mapping seed.")
        else:
            freight_codes = db.query(FreightCode).all()
            all_unit_ids = list(units.values())
            
            mapping_count = 0
            for fc in freight_codes:
                for unit_id in all_unit_ids:
                    mapping = FreightCodeUnit(
                        freight_code_id=fc.id,
                        freight_unit_id=unit_id,
                        is_default=(unit_id == all_unit_ids[0])  # First unit as default
                    )
                    db.add(mapping)
                    mapping_count += 1
            
            db.commit()
            print(f"[OK] Seeded {mapping_count} freight code-unit mappings")
        
        print("\n[DONE] Freight master data seed completed!")
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error seeding data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 50)
    print("Freight Code Master Data Seeder")
    print("=" * 50)
    seed_freight_data()
