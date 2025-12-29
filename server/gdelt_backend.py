"""
GDELT 데이터 파싱 및 필터링 백엔드 모듈
- GDELT Events CSV 파일에서 긴급 이벤트 추출
- GoldsteinScale 기반 위험도 필터링
"""

import os
import gzip
import csv
import json
import io
import zipfile
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

# GDELT Events CSV 컬럼 인덱스 (0-based)
# 참고: https://blog.gdeltproject.org/gdelt-2-0-data-format-codebook/
COL_GOLDSTEIN_SCALE = 30  # GoldsteinScale
COL_ACTION_GEO_LAT = 56   # ActionGeo_Lat
COL_ACTION_GEO_LONG = 57  # ActionGeo_Long
COL_ACTOR1NAME = 6        # Actor1Name
COL_ACTOR2NAME = 16       # Actor2NAME
COL_EVENT_BASE_TEXT = 60  # EventBaseText (또는 다른 텍스트 필드)
COL_SOURCEURL = 60        # SOURCEURL (실제 CSV는 61개 컬럼, 인덱스 0-60)

# 기본 GDELT 저장 경로
DEFAULT_GDELT_PATH = Path(r"D:\GDELT DB")

def find_latest_gdelt_file(base_path: Path = None) -> Optional[Path]:
    """
    가장 최근의 GDELT Events CSV 파일을 찾습니다.
    
    Args:
        base_path: GDELT 파일이 저장된 기본 경로
        
    Returns:
        가장 최근 파일의 Path 또는 None
    """
    if base_path is None:
        base_path = Path(os.getenv("GDELT_BASE_PATH", str(DEFAULT_GDELT_PATH)))
    
    if not base_path.exists():
        logger.warning(f"GDELT base path does not exist: {base_path}")
        return None
    
    # default/events/YYYYMMDD/ 디렉토리 구조에서 최신 파일 찾기
    events_path = base_path / "default" / "events"
    if not events_path.exists():
        logger.warning(f"GDELT events path does not exist: {events_path}")
        return None
    
    # 날짜 디렉토리 중 가장 최근 것 찾기
    date_dirs = sorted([d for d in events_path.iterdir() if d.is_dir()], reverse=True)
    
    for date_dir in date_dirs:
        # CSV 파일 찾기 (압축 파일 포함)
        csv_files = list(date_dir.glob("*.export.CSV")) + list(date_dir.glob("*.export.CSV.zip"))
        if csv_files:
            # 가장 최근 파일 반환
            latest_file = sorted(csv_files, reverse=True)[0]
            logger.info(f"Found latest GDELT file: {latest_file}")
            return latest_file
    
    logger.warning("No GDELT CSV files found")
    return None


def parse_gdelt_events(
    file_path: Path,
    goldstein_threshold: float = -5.0,
    max_events: int = 1000
) -> List[Dict]:
    """
    GDELT Events CSV 파일을 파싱하여 긴급 이벤트를 추출합니다.
    
    Args:
        file_path: GDELT CSV 파일 경로
        goldstein_threshold: GoldsteinScale 임계값 (이하 값만 추출)
        max_events: 최대 추출할 이벤트 수
        
    Returns:
        이벤트 리스트
    """
    if not file_path or not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return []
    
    events = []
    
    try:
        # 파일 열기 (압축 파일 처리)
        if file_path.suffix.lower() == '.zip':
            with zipfile.ZipFile(file_path, 'r') as zf:
                # ZIP 내부의 CSV 파일 찾기
                csv_name = [name for name in zf.namelist() if name.endswith('.CSV')][0]
                with zf.open(csv_name) as f:
                    content = io.TextIOWrapper(f, encoding='utf-8', errors='ignore')
                    events = _parse_csv_content(content, goldstein_threshold, max_events)
        elif file_path.suffix.lower() == '.gz':
            with gzip.open(file_path, 'rt', encoding='utf-8', errors='ignore') as f:
                events = _parse_csv_content(f, goldstein_threshold, max_events)
        else:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                events = _parse_csv_content(f, goldstein_threshold, max_events)
    
    except Exception as e:
        logger.error(f"Error parsing GDELT file: {e}", exc_info=True)
        return []
    
    logger.info(f"Parsed {len(events)} critical events from {file_path.name}")
    return events


def _parse_csv_content(
    content,
    goldstein_threshold: float,
    max_events: int
) -> List[Dict]:
    """
    CSV 내용을 파싱하여 이벤트 추출
    """
    events = []
    reader = csv.reader(content, delimiter='\t')
    
    for row in reader:
        if len(row) < 61:  # 최소 컬럼 수 확인
            continue
        
        try:
            # GoldsteinScale 확인
            goldstein_scale = float(row[COL_GOLDSTEIN_SCALE])
            if goldstein_scale > goldstein_threshold:
                continue
            
            # 위도/경도 확인
            lat = float(row[COL_ACTION_GEO_LAT]) if row[COL_ACTION_GEO_LAT] else None
            lng = float(row[COL_ACTION_GEO_LONG]) if row[COL_ACTION_GEO_LONG] else None
            
            if lat is None or lng is None:
                continue
            
            # 이벤트 정보 추출 (프론트엔드 형식에 맞춤)
            event = {
                'name': f"{row[COL_ACTOR1NAME]} - {row[COL_ACTOR2NAME]}" if len(row) > COL_ACTOR2NAME else 'Event',
                'actor1': row[COL_ACTOR1NAME] if len(row) > COL_ACTOR1NAME else '',
                'actor2': row[COL_ACTOR2NAME] if len(row) > COL_ACTOR2NAME else '',
                'scale': goldstein_scale,  # 프론트엔드가 기대하는 필드명
                'goldstein_scale': goldstein_scale,  # 하위 호환성
                'lat': lat,  # 프론트엔드가 기대하는 필드명
                'lng': lng,  # 프론트엔드가 기대하는 필드명
                'latitude': lat,  # 하위 호환성
                'longitude': lng,  # 하위 호환성
                'url': row[COL_SOURCEURL] if len(row) > COL_SOURCEURL else '',  # 프론트엔드가 기대하는 필드명
                'source_url': row[COL_SOURCEURL] if len(row) > COL_SOURCEURL else '',  # 하위 호환성
                'event_date': row[1] if len(row) > 1 else '',  # SQLDATE
            }
            
            events.append(event)
            
            if len(events) >= max_events:
                break
        
        except (ValueError, IndexError) as e:
            # 파싱 오류는 무시하고 계속 진행
            continue
    
    return events


def get_critical_alerts(
    goldstein_threshold: float = -5.0,
    max_alerts: int = 1000,
    base_path: Path = None
) -> Dict:
    """
    긴급 알림 데이터를 가져옵니다.
    
    Args:
        goldstein_threshold: GoldsteinScale 임계값
        max_alerts: 최대 알림 수
        base_path: GDELT 데이터 경로
        
    Returns:
        알림 데이터 딕셔너리
    """
    # 최신 GDELT 파일 찾기
    latest_file = find_latest_gdelt_file(base_path)
    
    if not latest_file:
        return {
            'error': 'No GDELT data file found',
            'alerts': [],
            'count': 0,
            'last_updated': None
        }
    
    # 이벤트 파싱
    events = parse_gdelt_events(latest_file, goldstein_threshold, max_alerts)
    
    return {
        'alerts': events,
        'count': len(events),
        'last_updated': datetime.now().isoformat(),
        'file_path': str(latest_file),
        'threshold': goldstein_threshold
    }


# 날짜별로 GDELT 파일 찾기
def find_gdelt_file_by_date(target_date: str, base_path: Path = None) -> Optional[Path]:
    """
    특정 날짜의 GDELT 파일을 찾습니다.
    
    Args:
        target_date: 날짜 (YYYYMMDD 또는 YYYY-MM-DD 형식)
        base_path: GDELT 데이터 경로
        
    Returns:
        파일 Path 또는 None
    """
    if base_path is None:
        base_path = Path(os.getenv("GDELT_BASE_PATH", str(DEFAULT_GDELT_PATH)))
    
    # 날짜 형식 정규화 (YYYYMMDD)
    target_date = target_date.replace('-', '')
    
    events_path = base_path / "default" / "events" / target_date
    
    if not events_path.exists():
        logger.warning(f"Date directory not found: {events_path}")
        return None
    
    # CSV 파일 찾기
    csv_files = list(events_path.glob("*.export.CSV")) + list(events_path.glob("*.export.CSV.zip"))
    
    if csv_files:
        return sorted(csv_files, reverse=True)[0]
    
    return None


def get_alerts_by_date_range(
    start_date: str,
    end_date: str,
    goldstein_threshold: float = -5.0,
    max_alerts: int = 1000,
    base_path: Path = None
) -> Dict:
    """
    날짜 범위 내의 긴급 알림을 가져옵니다.
    
    Args:
        start_date: 시작 날짜 (YYYY-MM-DD)
        end_date: 종료 날짜 (YYYY-MM-DD)
        goldstein_threshold: GoldsteinScale 임계값
        max_alerts: 최대 알림 수
        base_path: GDELT 데이터 경로
        
    Returns:
        알림 데이터 딕셔너리
    """
    from datetime import datetime, timedelta
    
    if base_path is None:
        base_path = Path(os.getenv("GDELT_BASE_PATH", str(DEFAULT_GDELT_PATH)))
    
    # 날짜 파싱
    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return {
            'error': 'Invalid date format. Use YYYY-MM-DD',
            'alerts': [],
            'count': 0
        }
    
    all_events = []
    current_date = start_dt
    
    # 날짜별로 파일 찾아서 파싱
    while current_date <= end_dt and len(all_events) < max_alerts:
        date_str = current_date.strftime('%Y%m%d')
        file_path = find_gdelt_file_by_date(date_str, base_path)
        
        if file_path:
            events = parse_gdelt_events(
                file_path,
                goldstein_threshold,
                max_alerts - len(all_events)
            )
            all_events.extend(events)
        
        current_date += timedelta(days=1)
    
    return {
        'alerts': all_events,
        'count': len(all_events),
        'date_range': {
            'start': start_date,
            'end': end_date
        },
        'threshold': goldstein_threshold,
        'last_updated': datetime.now().isoformat()
    }

