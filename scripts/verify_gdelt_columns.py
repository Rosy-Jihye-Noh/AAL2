"""
GDELT CSV 컬럼 인덱스 검증 스크립트
"""
import zipfile
import csv
from pathlib import Path

# GDELT 2.0 Events CSV 공식 컬럼 순서 (0-based index)
# 참고: http://data.gdeltproject.org/documentation/GDELT-Event_Codebook-V2.0.pdf
GDELT_COLUMNS = [
    (0, 'GLOBALEVENTID'),
    (1, 'SQLDATE'),
    (2, 'MonthYear'),
    (3, 'Year'),
    (4, 'FractionDate'),
    (5, 'Actor1Code'),
    (6, 'Actor1Name'),
    (7, 'Actor1CountryCode'),
    (8, 'Actor1KnownGroupCode'),
    (9, 'Actor1EthnicCode'),
    (10, 'Actor1Religion1Code'),
    (11, 'Actor1Religion2Code'),
    (12, 'Actor1Type1Code'),
    (13, 'Actor1Type2Code'),
    (14, 'Actor1Type3Code'),
    (15, 'Actor2Code'),
    (16, 'Actor2Name'),
    (17, 'Actor2CountryCode'),
    (18, 'Actor2KnownGroupCode'),
    (19, 'Actor2EthnicCode'),
    (20, 'Actor2Religion1Code'),
    (21, 'Actor2Religion2Code'),
    (22, 'Actor2Type1Code'),
    (23, 'Actor2Type2Code'),
    (24, 'Actor2Type3Code'),
    (25, 'IsRootEvent'),
    (26, 'EventCode'),
    (27, 'EventBaseCode'),
    (28, 'EventRootCode'),
    (29, 'QuadClass'),
    (30, 'GoldsteinScale'),
    (31, 'NumMentions'),
    (32, 'NumSources'),
    (33, 'NumArticles'),
    (34, 'AvgTone'),
    (35, 'Actor1Geo_Type'),
    (36, 'Actor1Geo_FullName'),
    (37, 'Actor1Geo_CountryCode'),
    (38, 'Actor1Geo_ADM1Code'),
    (39, 'Actor1Geo_ADM2Code'),
    (40, 'Actor1Geo_Lat'),
    (41, 'Actor1Geo_Long'),
    (42, 'Actor1Geo_FeatureID'),
    (43, 'Actor2Geo_Type'),
    (44, 'Actor2Geo_FullName'),
    (45, 'Actor2Geo_CountryCode'),
    (46, 'Actor2Geo_ADM1Code'),
    (47, 'Actor2Geo_ADM2Code'),
    (48, 'Actor2Geo_Lat'),
    (49, 'Actor2Geo_Long'),
    (50, 'Actor2Geo_FeatureID'),
    (51, 'ActionGeo_Type'),
    (52, 'ActionGeo_FullName'),
    (53, 'ActionGeo_CountryCode'),
    (54, 'ActionGeo_ADM1Code'),
    (55, 'ActionGeo_ADM2Code'),
    (56, 'ActionGeo_Lat'),
    (57, 'ActionGeo_Long'),
    (58, 'ActionGeo_FeatureID'),
    (59, 'DATEADDED'),
    (60, 'SOURCEURL'),
]

# 현재 백엔드 코드의 인덱스
CURRENT_INDEXES = {
    'COL_SQLDATE': 1,
    'COL_EVENT_CODE': 27,  # ⚠️ 실제로는 26
    'COL_QUAD_CLASS': 28,  # ⚠️ 실제로는 29
    'COL_GOLDSTEIN_SCALE': 30,
    'COL_ACTOR1NAME': 6,
    'COL_ACTOR1COUNTRYCODE': 7,
    'COL_ACTOR2NAME': 16,
    'COL_ACTOR2COUNTRYCODE': 17,
    'COL_NUM_SOURCES': 31,  # ⚠️ 실제로는 32
    'COL_NUM_MENTIONS': 32,  # ⚠️ 실제로는 31
    'COL_NUM_ARTICLES': 33,
    'COL_AVG_TONE': 34,
    'COL_ACTION_GEO_COUNTRYCODE': 51,  # ⚠️ 실제로는 53
    'COL_ACTION_GEO_ADM1CODE': 52,  # ⚠️ 실제로는 54
    'COL_ACTION_GEO_LAT': 56,
    'COL_ACTION_GEO_LONG': 57,
    'COL_ACTION_GEO_FULLNAME': 58,  # ⚠️ 실제로는 52
    'COL_SOURCEURL': 60,
}

# 올바른 인덱스
CORRECT_INDEXES = {
    'COL_SQLDATE': 1,
    'COL_EVENT_CODE': 26,
    'COL_QUAD_CLASS': 29,
    'COL_GOLDSTEIN_SCALE': 30,
    'COL_ACTOR1NAME': 6,
    'COL_ACTOR1COUNTRYCODE': 7,
    'COL_ACTOR2NAME': 16,
    'COL_ACTOR2COUNTRYCODE': 17,
    'COL_NUM_MENTIONS': 31,
    'COL_NUM_SOURCES': 32,
    'COL_NUM_ARTICLES': 33,
    'COL_AVG_TONE': 34,
    'COL_ACTION_GEO_TYPE': 51,
    'COL_ACTION_GEO_FULLNAME': 52,
    'COL_ACTION_GEO_COUNTRYCODE': 53,
    'COL_ACTION_GEO_ADM1CODE': 54,
    'COL_ACTION_GEO_LAT': 56,
    'COL_ACTION_GEO_LONG': 57,
    'COL_ACTION_GEO_FEATUREID': 58,
    'COL_SOURCEURL': 60,
}


def verify_columns():
    """실제 CSV 파일로 컬럼 검증"""
    print("="*70)
    print("GDELT CSV 컬럼 인덱스 검증")
    print("="*70)
    
    # 데이터 파일 찾기
    data_path = Path(__file__).parent.parent / "data" / "gdelt" / "default" / "events"
    
    if not data_path.exists():
        print(f"⚠️ 데이터 경로를 찾을 수 없습니다: {data_path}")
        return
    
    # 최신 날짜 디렉토리 찾기
    date_dirs = sorted([d for d in data_path.iterdir() if d.is_dir()], reverse=True)
    if not date_dirs:
        print("⚠️ 데이터 디렉토리가 없습니다.")
        return
    
    # ZIP 파일 찾기
    zip_files = list(date_dirs[0].glob("*.export.CSV.zip"))
    if not zip_files:
        print("⚠️ ZIP 파일을 찾을 수 없습니다.")
        return
    
    zip_path = zip_files[0]
    print(f"\n[FILE] 분석 파일: {zip_path.name}")
    
    # ZIP 파일 열기
    with zipfile.ZipFile(zip_path, 'r') as zf:
        csv_name = [name for name in zf.namelist() if name.endswith('.CSV')][0]
        with zf.open(csv_name) as f:
            import io
            content = io.TextIOWrapper(f, encoding='utf-8', errors='ignore')
            reader = csv.reader(content, delimiter='\t')
            
            # 첫 번째 행 읽기
            row = next(reader)
            
            print(f"\n[INFO] 총 컬럼 수: {len(row)}")
            print("\n" + "-"*70)
            print("컬럼 검증 결과:")
            print("-"*70)
            
            # 주요 컬럼 확인
            checks = [
                ('SQLDATE', 1, row[1] if len(row) > 1 else 'N/A'),
                ('Actor1Name', 6, row[6] if len(row) > 6 else 'N/A'),
                ('Actor1CountryCode', 7, row[7] if len(row) > 7 else 'N/A'),
                ('Actor2Name', 16, row[16] if len(row) > 16 else 'N/A'),
                ('Actor2CountryCode', 17, row[17] if len(row) > 17 else 'N/A'),
                ('EventCode', 26, row[26] if len(row) > 26 else 'N/A'),
                ('EventBaseCode (현재 EventCode로 사용)', 27, row[27] if len(row) > 27 else 'N/A'),
                ('QuadClass (현재 28)', 28, row[28] if len(row) > 28 else 'N/A'),
                ('QuadClass (올바른 29)', 29, row[29] if len(row) > 29 else 'N/A'),
                ('GoldsteinScale', 30, row[30] if len(row) > 30 else 'N/A'),
                ('NumMentions', 31, row[31] if len(row) > 31 else 'N/A'),
                ('NumSources', 32, row[32] if len(row) > 32 else 'N/A'),
                ('NumArticles', 33, row[33] if len(row) > 33 else 'N/A'),
                ('AvgTone', 34, row[34] if len(row) > 34 else 'N/A'),
                ('ActionGeo_Type (현재 CountryCode로 사용)', 51, row[51] if len(row) > 51 else 'N/A'),
                ('ActionGeo_FullName (올바른)', 52, row[52] if len(row) > 52 else 'N/A'),
                ('ActionGeo_CountryCode (올바른)', 53, row[53] if len(row) > 53 else 'N/A'),
                ('ActionGeo_ADM1Code (올바른)', 54, row[54] if len(row) > 54 else 'N/A'),
                ('ActionGeo_Lat', 56, row[56] if len(row) > 56 else 'N/A'),
                ('ActionGeo_Long', 57, row[57] if len(row) > 57 else 'N/A'),
                ('ActionGeo_FeatureID (현재 FullName으로 사용)', 58, row[58] if len(row) > 58 else 'N/A'),
                ('SOURCEURL', 60, row[60][:50] + '...' if len(row) > 60 and len(row[60]) > 50 else row[60] if len(row) > 60 else 'N/A'),
            ]
            
            for name, idx, value in checks:
                value_str = str(value)[:40] if value else 'EMPTY'
                print(f"[{idx:2d}] {name:40s}: {value_str}")
            
            print("\n" + "="*70)
            print("⚠️ 발견된 인덱스 오류:")
            print("="*70)
            
            errors = [
                ("COL_EVENT_CODE", 27, 26, "EventCode"),
                ("COL_QUAD_CLASS", 28, 29, "QuadClass"),
                ("COL_NUM_SOURCES", 31, 32, "NumSources"),
                ("COL_NUM_MENTIONS", 32, 31, "NumMentions"),
                ("COL_ACTION_GEO_COUNTRYCODE", 51, 53, "ActionGeo_CountryCode"),
                ("COL_ACTION_GEO_ADM1CODE", 52, 54, "ActionGeo_ADM1Code"),
                ("COL_ACTION_GEO_FULLNAME", 58, 52, "ActionGeo_FullName"),
            ]
            
            for const_name, current, correct, field_name in errors:
                print(f"❌ {const_name}: 현재 {current} → 올바른 {correct} ({field_name})")


if __name__ == '__main__':
    verify_columns()

