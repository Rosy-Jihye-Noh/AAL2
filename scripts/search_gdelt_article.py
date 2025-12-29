import zipfile
import csv
from pathlib import Path

# GDELT 데이터 경로
base = Path(r'D:\GDELT DB\default\events')

# 최근 90일 디렉토리 검색
date_dirs = sorted([d for d in base.iterdir() if d.is_dir()], reverse=True)[:90]
print(f'Searching {len(date_dirs)} recent directories...\n')

# nvdaily.com 기사 검색 - 여러 키워드 시도
search_keywords = ['nvdaily.com', 'article_2ec7d9f6', 'maphis']
url_keyword = 'nvdaily.com'
found = False
checked = 0

for date_dir in date_dirs:
    csv_files = list(date_dir.glob('*.zip'))
    checked += len(csv_files)
    
    for csv_file in csv_files:
        try:
            with zipfile.ZipFile(csv_file) as z:
                csv_name = z.namelist()[0]
                with z.open(csv_name) as f:
                    content = f.read().decode('utf-8', errors='ignore')
                    
                    if url_keyword in content.lower():
                        print(f'✓ 파일 발견: {csv_file.name}\n')
                        
                        reader = csv.reader(content.split('\n'), delimiter='\t')
                        for row in reader:
                            if len(row) > 60 and url_keyword in row[60].lower():
                                print('=' * 60)
                                print('GDELT Article Information')
                                print('=' * 60)
                                print(f'GoldsteinScale: {row[30]}')
                                print(f'Event Code: {row[26]}')
                                print(f'QuadClass: {row[29]}')
                                print(f'Actor1: {row[6]}')
                                print(f'Actor2: {row[16]}')
                                print(f'Location: {row[52] if len(row) > 52 else "N/A"}')
                                print(f'Date: {row[1] if len(row) > 1 else "N/A"}')
                                print(f'AvgTone: {row[34] if len(row) > 34 else "N/A"}')
                                print(f'URL: {row[60][:80]}...')
                                print('=' * 60)
                                found = True
                                break
                        
                        if found:
                            break
        except Exception as e:
            continue
    
    if found:
        break

print(f'\nTotal {checked} files searched')
if not found:
    print('WARNING: Article not found.')
    print('Try expanding date range or changing URL keywords.')

