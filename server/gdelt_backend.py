"""
GDELT 데이터 파싱 및 필터링 백엔드 모듈
- GDELT Events CSV 파일에서 긴급 이벤트 추출
- GoldsteinScale 기반 위험도 필터링
- 자동 다운로드 및 데이터 관리
"""

import os
import gzip
import csv
import json
import io
import zipfile
import requests
import shutil
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
import logging
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

logger = logging.getLogger(__name__)

# GDELT Events CSV 컬럼 인덱스 (0-based)
# 참고: http://data.gdeltproject.org/documentation/GDELT-Event_Codebook-V2.0.pdf
# 실제 CSV 파일 검증 완료 (2024-12-30)

# 기본 정보
COL_SQLDATE = 1              # SQLDATE (YYYYMMDD)
COL_EVENT_CODE = 26          # EventCode (CAMEO 코드) - 수정됨 (27→26)
COL_QUAD_CLASS = 29          # QuadClass (1-4) - 수정됨 (28→29)
COL_GOLDSTEIN_SCALE = 30     # GoldsteinScale

# 행위자 정보
COL_ACTOR1NAME = 6           # Actor1Name
COL_ACTOR1COUNTRYCODE = 7    # Actor1CountryCode
COL_ACTOR2NAME = 16          # Actor2Name
COL_ACTOR2COUNTRYCODE = 17   # Actor2CountryCode

# 분석 지표
COL_NUM_MENTIONS = 31        # NumMentions - 수정됨 (32→31)
COL_NUM_SOURCES = 32         # NumSources - 수정됨 (31→32)
COL_NUM_ARTICLES = 33        # NumArticles
COL_AVG_TONE = 34            # AvgTone

# 위치 정보
COL_ACTION_GEO_TYPE = 51         # ActionGeo_Type (신규 추가)
COL_ACTION_GEO_FULLNAME = 52     # ActionGeo_FullName - 수정됨 (58→52)
COL_ACTION_GEO_COUNTRYCODE = 53  # ActionGeo_CountryCode - 수정됨 (51→53)
COL_ACTION_GEO_ADM1CODE = 54     # ActionGeo_ADM1Code - 수정됨 (52→54)
COL_ACTION_GEO_LAT = 56          # ActionGeo_Lat
COL_ACTION_GEO_LONG = 57         # ActionGeo_Long
COL_ACTION_GEO_FEATUREID = 58    # ActionGeo_FeatureID (신규 추가)

# 출처
COL_SOURCEURL = 60          # SOURCEURL (실제 CSV는 61개 컬럼, 인덱스 0-60)


def get_event_category(event_code: str, quad_class: int) -> str:
    """
    CAMEO 이벤트 코드와 QuadClass를 기반으로 카테고리를 반환합니다.
    
    Args:
        event_code: CAMEO 이벤트 코드 (예: "190", "100")
        quad_class: QuadClass 값 (1-4)
        
    Returns:
        카테고리 문자열
    """
    # QuadClass 기반 기본 분류
    quad_class_map = {
        1: "Verbal Cooperation",
        2: "Material Cooperation",
        3: "Verbal Conflict",
        4: "Material Conflict"
    }
    
    # QuadClass가 유효하면 기본 분류 사용
    if quad_class in quad_class_map:
        return quad_class_map[quad_class]
    
    # QuadClass가 없으면 이벤트 코드 기반 추정
    if not event_code:
        return "Unknown"
    
    # 이벤트 코드 범위 기반 분류 (CAMEO 코드 구조 참고)
    try:
        code_num = int(event_code)
        if code_num >= 100 and code_num < 200:
            return "Material Conflict"
        elif code_num >= 200 and code_num < 300:
            return "Verbal Conflict"
        elif code_num >= 300 and code_num < 400:
            return "Material Cooperation"
        elif code_num >= 400 and code_num < 500:
            return "Verbal Cooperation"
        else:
            return "Unknown"
    except ValueError:
        return "Unknown"


def safe_float(value: str, default: float = None) -> Optional[float]:
    """안전하게 float로 변환"""
    if not value or value.strip() == '':
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value: str, default: int = None) -> Optional[int]:
    """안전하게 int로 변환"""
    if not value or value.strip() == '':
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_str(value: str, default: str = '') -> str:
    """안전하게 문자열 반환"""
    if not value:
        return default
    return str(value).strip()


# GDELT 다운로드 URL
GDELT_BASE_URL = "http://data.gdeltproject.org/gdeltv2"
GDELT_LASTUPDATE_URL = f"{GDELT_BASE_URL}/lastupdate.txt"

# 기본 GDELT 저장 경로 (프로젝트 내부 data/gdelt로 설정)
# 환경 변수 GDELT_BASE_PATH가 설정되어 있으면 그것을 사용, 없으면 프로젝트 내부 경로 사용
_project_root = Path(__file__).parent.parent
DEFAULT_GDELT_PATH = _project_root / "data" / "gdelt"

def get_gdelt_base_path() -> Path:
    """
    GDELT 기본 경로를 반환합니다.
    환경 변수 GDELT_BASE_PATH가 설정되어 있으면 그것을 사용하고,
    없으면 프로젝트 내부 data/gdelt 경로를 사용합니다.
    """
    env_path = os.getenv("GDELT_BASE_PATH")
    if env_path:
        return Path(env_path)
    return DEFAULT_GDELT_PATH


def find_latest_gdelt_file(base_path: Path = None) -> Optional[Path]:
    """
    가장 최근의 GDELT Events CSV 파일을 찾습니다.
    
    Args:
        base_path: GDELT 파일이 저장된 기본 경로
        
    Returns:
        가장 최근 파일의 Path 또는 None
    """
    if base_path is None:
        base_path = get_gdelt_base_path()
    
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
            goldstein_scale = safe_float(row[COL_GOLDSTEIN_SCALE] if len(row) > COL_GOLDSTEIN_SCALE else '')
            if goldstein_scale is None or goldstein_scale > goldstein_threshold:
                continue
            
            # 위도/경도 확인
            lat = safe_float(row[COL_ACTION_GEO_LAT] if len(row) > COL_ACTION_GEO_LAT else '')
            lng = safe_float(row[COL_ACTION_GEO_LONG] if len(row) > COL_ACTION_GEO_LONG else '')
            
            if lat is None or lng is None:
                continue
            
            # 기본 정보 추출
            event_code = safe_str(row[COL_EVENT_CODE] if len(row) > COL_EVENT_CODE else '')
            quad_class = safe_int(row[COL_QUAD_CLASS] if len(row) > COL_QUAD_CLASS else '')
            event_date = safe_str(row[COL_SQLDATE] if len(row) > COL_SQLDATE else '')
            
            # 행위자 정보
            actor1 = safe_str(row[COL_ACTOR1NAME] if len(row) > COL_ACTOR1NAME else '')
            actor1_country = safe_str(row[COL_ACTOR1COUNTRYCODE] if len(row) > COL_ACTOR1COUNTRYCODE else '')
            actor2 = safe_str(row[COL_ACTOR2NAME] if len(row) > COL_ACTOR2NAME else '')
            actor2_country = safe_str(row[COL_ACTOR2COUNTRYCODE] if len(row) > COL_ACTOR2COUNTRYCODE else '')
            
            # 위치 정보
            country_code = safe_str(row[COL_ACTION_GEO_COUNTRYCODE] if len(row) > COL_ACTION_GEO_COUNTRYCODE else '')
            location = safe_str(row[COL_ACTION_GEO_FULLNAME] if len(row) > COL_ACTION_GEO_FULLNAME else '')
            
            # 분석 지표
            num_sources = safe_int(row[COL_NUM_SOURCES] if len(row) > COL_NUM_SOURCES else '', 0)
            num_mentions = safe_int(row[COL_NUM_MENTIONS] if len(row) > COL_NUM_MENTIONS else '', 0)
            num_articles = safe_int(row[COL_NUM_ARTICLES] if len(row) > COL_NUM_ARTICLES else '', 0)
            avg_tone = safe_float(row[COL_AVG_TONE] if len(row) > COL_AVG_TONE else '')
            
            # 출처
            source_url = safe_str(row[COL_SOURCEURL] if len(row) > COL_SOURCEURL else '')
            
            # 카테고리 결정
            category = get_event_category(event_code, quad_class)
            
            # 이벤트 이름 생성
            name_parts = []
            if actor1:
                name_parts.append(actor1)
            if actor2:
                name_parts.append(actor2)
            name = ' - '.join(name_parts) if name_parts else 'Event'
            
            # 이벤트 정보 추출 (프론트엔드 형식에 맞춤)
            event = {
                # 기본 정보
                'name': name,
                'event_date': event_date,
                'event_code': event_code,
                'category': category,
                'quad_class': quad_class,
                
                # 행위자 정보
                'actor1': actor1,
                'actor1_country': actor1_country,
                'actor2': actor2,
                'actor2_country': actor2_country,
                
                # 위치 정보
                'lat': lat,
                'lng': lng,
                'latitude': lat,  # 하위 호환성
                'longitude': lng,  # 하위 호환성
                'location': location,
                'country_code': country_code,
                
                # 분석 지표
                'scale': goldstein_scale,  # 프론트엔드가 기대하는 필드명
                'goldstein_scale': goldstein_scale,  # 하위 호환성
                'avg_tone': avg_tone,
                'num_articles': num_articles,
                'num_mentions': num_mentions,
                'num_sources': num_sources,
                
                # 출처
                'url': source_url,  # 프론트엔드가 기대하는 필드명
                'source_url': source_url,  # 하위 호환성
            }
            
            events.append(event)
            
            if len(events) >= max_events:
                break
        
        except (ValueError, IndexError) as e:
            # 파싱 오류는 무시하고 계속 진행
            logger.debug(f"Error parsing row: {e}")
            continue
    
    return events


def filter_events(
    events: List[Dict],
    country: Optional[str] = None,
    category: Optional[str] = None,
    min_articles: Optional[int] = None
) -> List[Dict]:
    """
    이벤트 리스트를 필터링합니다.
    
    Args:
        events: 이벤트 리스트
        country: 국가 코드 필터 (country_code, actor1_country, actor2_country 중 하나라도 일치)
        category: 카테고리 필터
        min_articles: 최소 기사 수 필터
        
    Returns:
        필터링된 이벤트 리스트
    """
    filtered = events
    
    if country:
        country_upper = country.upper()
        filtered = [
            e for e in filtered
            if (e.get('country_code', '').upper() == country_upper or
                e.get('actor1_country', '').upper() == country_upper or
                e.get('actor2_country', '').upper() == country_upper)
        ]
    
    if category:
        filtered = [e for e in filtered if e.get('category', '') == category]
    
    if min_articles is not None:
        filtered = [e for e in filtered if e.get('num_articles', 0) >= min_articles]
    
    return filtered


def sort_events(
    events: List[Dict],
    sort_by: str = 'date'
) -> List[Dict]:
    """
    이벤트 리스트를 정렬합니다.
    
    Args:
        events: 이벤트 리스트
        sort_by: 정렬 기준 ('importance', 'date', 'tone', 'scale')
            - importance: num_articles + num_mentions 기준 (내림차순)
            - date: event_date 기준 (내림차순)
            - tone: avg_tone 기준 (오름차순, 음수가 먼저)
            - scale: goldstein_scale 기준 (오름차순, 음수가 먼저)
        
    Returns:
        정렬된 이벤트 리스트
    """
    if not events:
        return events
    
    if sort_by == 'importance':
        return sorted(
            events,
            key=lambda x: (x.get('num_articles', 0) + x.get('num_mentions', 0)),
            reverse=True
        )
    elif sort_by == 'date':
        return sorted(
            events,
            key=lambda x: x.get('event_date', ''),
            reverse=True
        )
    elif sort_by == 'tone':
        return sorted(
            events,
            key=lambda x: safe_float(str(x.get('avg_tone', 0)), 0)
        )
    elif sort_by == 'scale':
        return sorted(
            events,
            key=lambda x: safe_float(str(x.get('goldstein_scale', 0)), 0)
        )
    else:
        # 기본값: 날짜순
        return sorted(events, key=lambda x: x.get('event_date', ''), reverse=True)


def get_critical_alerts(
    goldstein_threshold: float = -5.0,
    max_alerts: int = 1000,
    base_path: Path = None,
    country: Optional[str] = None,
    category: Optional[str] = None,
    min_articles: Optional[int] = None,
    sort_by: str = 'date'
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
    
    # 이벤트 파싱 (필터링 전에는 더 많이 가져오기)
    parse_limit = max_alerts * 2 if (country or category or min_articles) else max_alerts
    events = parse_gdelt_events(latest_file, goldstein_threshold, parse_limit)
    
    # 필터링 적용
    events = filter_events(events, country=country, category=category, min_articles=min_articles)
    
    # 정렬 적용
    events = sort_events(events, sort_by=sort_by)
    
    # 최대 개수 제한
    events = events[:max_alerts]
    
    return {
        'alerts': events,
        'count': len(events),
        'last_updated': datetime.now().isoformat(),
        'file_path': str(latest_file),
        'threshold': goldstein_threshold,
        'filters': {
            'country': country,
            'category': category,
            'min_articles': min_articles,
            'sort_by': sort_by
        }
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
        base_path = get_gdelt_base_path()
    
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
    base_path: Path = None,
    country: Optional[str] = None,
    category: Optional[str] = None,
    min_articles: Optional[int] = None,
    sort_by: str = 'date'
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
        base_path = get_gdelt_base_path()
    
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
    
    # 날짜별로 파일 찾아서 파싱 (필터링 전에는 더 많이 가져오기)
    parse_limit = max_alerts * 2 if (country or category or min_articles) else max_alerts
    while current_date <= end_dt:
        date_str = current_date.strftime('%Y%m%d')
        file_path = find_gdelt_file_by_date(date_str, base_path)
        
        if file_path:
            events = parse_gdelt_events(
                file_path,
                goldstein_threshold,
                parse_limit
            )
            all_events.extend(events)
        
        current_date += timedelta(days=1)
    
    # 필터링 적용
    all_events = filter_events(all_events, country=country, category=category, min_articles=min_articles)
    
    # 정렬 적용
    all_events = sort_events(all_events, sort_by=sort_by)
    
    # 최대 개수 제한
    all_events = all_events[:max_alerts]
    
    return {
        'alerts': all_events,
        'count': len(all_events),
        'date_range': {
            'start': start_date,
            'end': end_date
        },
        'threshold': goldstein_threshold,
        'last_updated': datetime.now().isoformat(),
        'filters': {
            'country': country,
            'category': category,
            'min_articles': min_articles,
            'sort_by': sort_by
        }
    }


def get_latest_gdelt_file_url() -> Optional[str]:
    """
    GDELT 서버에서 최신 파일 URL을 가져옵니다.
    
    Returns:
        최신 파일 URL 또는 None
    """
    try:
        response = requests.get(GDELT_LASTUPDATE_URL, timeout=10)
        if response.status_code == 200:
            # lastupdate.txt 형식: 
            # 78857 e097bd4fb117a0ca51716cf09f16bea2 http://data.gdeltproject.org/gdeltv2/20251230020000.export.CSV.zip
            lines = response.text.strip().split('\n')
            if lines:
                # 첫 번째 줄에서 마지막 토큰 추출 (이미 전체 URL이 포함됨)
                last_token = lines[0].strip().split()[-1] if lines[0].strip() else None
                if last_token:
                    # 이미 URL이면 그대로 사용, 파일명만이면 BASE_URL 추가
                    if last_token.startswith('http://') or last_token.startswith('https://'):
                        return last_token
                    else:
                        return f"{GDELT_BASE_URL}/{last_token}"
        logger.error(f"Failed to get latest GDELT file URL: HTTP {response.status_code}")
    except Exception as e:
        logger.error(f"Error fetching latest GDELT file URL: {e}")
    return None


def download_gdelt_file(file_url: str = None, base_path: Path = None) -> Optional[Path]:
    """
    GDELT 파일을 다운로드합니다.
    
    Args:
        file_url: 다운로드할 파일 URL (None이면 최신 파일 자동 감지)
        base_path: 저장할 기본 경로
        
    Returns:
        다운로드된 파일의 Path 또는 None
    """
    if base_path is None:
        base_path = get_gdelt_base_path()
    
    # 디렉토리 구조 생성
    base_path.mkdir(parents=True, exist_ok=True)
    events_path = base_path / "default" / "events"
    events_path.mkdir(parents=True, exist_ok=True)
    
    # 최신 파일 URL 가져오기
    if file_url is None:
        file_url = get_latest_gdelt_file_url()
        if not file_url:
            logger.error("Failed to get latest GDELT file URL")
            return None
    
    try:
        # 파일명 추출 (예: 20251229120000.export.CSV.zip)
        file_name = file_url.split('/')[-1]
        
        # 날짜 추출 (YYYYMMDD)
        date_str = file_name[:8]  # 첫 8자리가 날짜
        
        # 날짜별 디렉토리 생성
        date_dir = events_path / date_str
        date_dir.mkdir(exist_ok=True)
        
        # 저장 경로
        save_path = date_dir / file_name
        
        # 이미 파일이 있으면 스킵
        if save_path.exists():
            logger.info(f"File already exists: {save_path}")
            return save_path
        
        # 파일 다운로드
        logger.info(f"Downloading GDELT file: {file_url}")
        response = requests.get(file_url, timeout=60, stream=True)
        response.raise_for_status()
        
        # 파일 저장
        with open(save_path, 'wb') as f:
            shutil.copyfileobj(response.raw, f)
        
        logger.info(f"Downloaded GDELT file: {save_path}")
        return save_path
        
    except Exception as e:
        logger.error(f"Error downloading GDELT file: {e}", exc_info=True)
        return None


def cleanup_old_gdelt_data(base_path: Path = None, keep_days: int = 2) -> int:
    """
    오래된 GDELT 데이터를 삭제합니다.
    UTC 기준으로 오늘과 어제 데이터만 유지하고 나머지는 삭제합니다.
    
    Args:
        base_path: GDELT 데이터 기본 경로
        keep_days: 유지할 일수 (기본값: 2 = 오늘 + 어제)
        
    Returns:
        삭제된 디렉토리 수
    """
    if base_path is None:
        base_path = get_gdelt_base_path()
    
    events_path = base_path / "default" / "events"
    if not events_path.exists():
        return 0
    
    # UTC 기준 오늘 날짜
    utc_now = datetime.now(timezone.utc)
    today = utc_now.date()
    
    # 유지할 날짜 목록 (오늘부터 keep_days-1일 전까지)
    keep_dates = {today - timedelta(days=i) for i in range(keep_days)}
    
    deleted_count = 0
    
    try:
        # 날짜 디렉토리 순회
        for date_dir in events_path.iterdir():
            if not date_dir.is_dir():
                continue
            
            try:
                # 디렉토리명에서 날짜 파싱 (YYYYMMDD)
                dir_date = datetime.strptime(date_dir.name, '%Y%m%d').date()
                
                # 유지할 날짜가 아니면 삭제
                if dir_date not in keep_dates:
                    logger.info(f"Deleting old GDELT data: {date_dir}")
                    shutil.rmtree(date_dir)
                    deleted_count += 1
            except ValueError:
                # 날짜 형식이 아닌 디렉토리는 무시
                logger.warning(f"Skipping invalid date directory: {date_dir.name}")
                continue
        
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old GDELT data directories")
        
    except Exception as e:
        logger.error(f"Error cleaning up old GDELT data: {e}", exc_info=True)
    
    return deleted_count


def update_gdelt_data() -> Dict:
    """
    GDELT 데이터를 업데이트합니다 (다운로드 + 정리).
    
    Returns:
        업데이트 결과 딕셔너리
    """
    result = {
        'downloaded': False,
        'file_path': None,
        'cleaned_dirs': 0,
        'error': None
    }
    
    try:
        # 최신 파일 다운로드
        downloaded_file = download_gdelt_file()
        if downloaded_file:
            result['downloaded'] = True
            result['file_path'] = str(downloaded_file)
        
        # 오래된 데이터 정리
        deleted_count = cleanup_old_gdelt_data()
        result['cleaned_dirs'] = deleted_count
        
    except Exception as e:
        result['error'] = str(e)
        logger.error(f"Error updating GDELT data: {e}", exc_info=True)
    
    return result


# ============================================================================
# Phase 3: 통계 및 집계 API
# ============================================================================

def get_stats_by_country(
    goldstein_threshold: float = -5.0,
    max_alerts: int = 10000,
    base_path: Path = None
) -> Dict:
    """
    국가별 통계를 계산합니다.
    
    Args:
        goldstein_threshold: GoldsteinScale 임계값
        max_alerts: 최대 알림 수 (통계 계산용)
        base_path: GDELT 데이터 경로
        
    Returns:
        국가별 통계 딕셔너리
    """
    latest_file = find_latest_gdelt_file(base_path)
    if not latest_file:
        return {'error': 'No GDELT data file found', 'stats': {}}
    
    events = parse_gdelt_events(latest_file, goldstein_threshold, max_alerts)
    
    country_stats = {}
    for event in events:
        country = event.get('country_code', 'UNKNOWN')
        if not country:
            country = 'UNKNOWN'
        
        if country not in country_stats:
            country_stats[country] = {
                'count': 0,
                'avg_goldstein': 0.0,
                'avg_tone': 0.0,
                'total_articles': 0,
                'categories': {}
            }
        
        stats = country_stats[country]
        stats['count'] += 1
        stats['avg_goldstein'] += event.get('goldstein_scale', 0)
        stats['avg_tone'] += event.get('avg_tone', 0) or 0
        stats['total_articles'] += event.get('num_articles', 0)
        
        category = event.get('category', 'Unknown')
        stats['categories'][category] = stats['categories'].get(category, 0) + 1
    
    # 평균 계산
    for country in country_stats:
        stats = country_stats[country]
        if stats['count'] > 0:
            stats['avg_goldstein'] = round(stats['avg_goldstein'] / stats['count'], 2)
            stats['avg_tone'] = round(stats['avg_tone'] / stats['count'], 2)
    
    # 정렬 (이벤트 수 기준)
    sorted_stats = dict(sorted(
        country_stats.items(),
        key=lambda x: x[1]['count'],
        reverse=True
    ))
    
    return {
        'stats': sorted_stats,
        'total_countries': len(sorted_stats),
        'total_events': len(events),
        'last_updated': datetime.now().isoformat()
    }


def get_stats_by_category(
    goldstein_threshold: float = -5.0,
    max_alerts: int = 10000,
    base_path: Path = None
) -> Dict:
    """
    카테고리별 통계를 계산합니다.
    
    Args:
        goldstein_threshold: GoldsteinScale 임계값
        max_alerts: 최대 알림 수 (통계 계산용)
        base_path: GDELT 데이터 경로
        
    Returns:
        카테고리별 통계 딕셔너리
    """
    latest_file = find_latest_gdelt_file(base_path)
    if not latest_file:
        return {'error': 'No GDELT data file found', 'stats': {}}
    
    events = parse_gdelt_events(latest_file, goldstein_threshold, max_alerts)
    
    category_stats = {}
    for event in events:
        category = event.get('category', 'Unknown')
        
        if category not in category_stats:
            category_stats[category] = {
                'count': 0,
                'avg_goldstein': 0.0,
                'avg_tone': 0.0,
                'total_articles': 0,
                'countries': set()
            }
        
        stats = category_stats[category]
        stats['count'] += 1
        stats['avg_goldstein'] += event.get('goldstein_scale', 0)
        stats['avg_tone'] += event.get('avg_tone', 0) or 0
        stats['total_articles'] += event.get('num_articles', 0)
        
        country = event.get('country_code', '')
        if country:
            stats['countries'].add(country)
    
    # 평균 계산 및 set을 list로 변환
    for category in category_stats:
        stats = category_stats[category]
        if stats['count'] > 0:
            stats['avg_goldstein'] = round(stats['avg_goldstein'] / stats['count'], 2)
            stats['avg_tone'] = round(stats['avg_tone'] / stats['count'], 2)
        stats['countries'] = list(stats['countries'])
        stats['num_countries'] = len(stats['countries'])
    
    # 정렬 (이벤트 수 기준)
    sorted_stats = dict(sorted(
        category_stats.items(),
        key=lambda x: x[1]['count'],
        reverse=True
    ))
    
    return {
        'stats': sorted_stats,
        'total_categories': len(sorted_stats),
        'total_events': len(events),
        'last_updated': datetime.now().isoformat()
    }


def get_trends(
    start_date: str,
    end_date: str,
    goldstein_threshold: float = -5.0,
    base_path: Path = None
) -> Dict:
    """
    시간대별 트렌드를 분석합니다.
    
    Args:
        start_date: 시작 날짜 (YYYY-MM-DD)
        end_date: 종료 날짜 (YYYY-MM-DD)
        goldstein_threshold: GoldsteinScale 임계값
        base_path: GDELT 데이터 경로
        
    Returns:
        트렌드 분석 딕셔너리
    """
    from datetime import datetime, timedelta
    
    if base_path is None:
        base_path = get_gdelt_base_path()
    
    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return {
            'error': 'Invalid date format. Use YYYY-MM-DD',
            'trends': {}
        }
    
    daily_stats = {}
    current_date = start_dt
    
    while current_date <= end_dt:
        date_str = current_date.strftime('%Y%m%d')
        file_path = find_gdelt_file_by_date(date_str, base_path)
        
        if file_path:
            events = parse_gdelt_events(file_path, goldstein_threshold, 10000)
            
            if events:
                daily_stats[date_str] = {
                    'date': current_date.strftime('%Y-%m-%d'),
                    'count': len(events),
                    'avg_goldstein': round(
                        sum(e.get('goldstein_scale', 0) for e in events) / len(events),
                        2
                    ),
                    'avg_tone': round(
                        sum(e.get('avg_tone', 0) or 0 for e in events) / len(events),
                        2
                    ),
                    'total_articles': sum(e.get('num_articles', 0) for e in events),
                    'categories': {}
                }
                
                # 카테고리별 분포
                for event in events:
                    cat = event.get('category', 'Unknown')
                    daily_stats[date_str]['categories'][cat] = \
                        daily_stats[date_str]['categories'].get(cat, 0) + 1
        
        current_date += timedelta(days=1)
    
    # 정렬 (날짜순)
    sorted_trends = dict(sorted(daily_stats.items()))
    
    return {
        'trends': sorted_trends,
        'date_range': {
            'start': start_date,
            'end': end_date
        },
        'total_days': len(sorted_trends),
        'last_updated': datetime.now().isoformat()
    }


# ============================================================================
# Phase 3: 캐싱 메커니즘 (간단한 메모리 캐시)
# ============================================================================

_cache = {}
_cache_timestamps = {}
CACHE_TTL = 300  # 5분


def _get_cache_key(func_name: str, **kwargs) -> str:
    """캐시 키 생성"""
    key_parts = [func_name]
    for k, v in sorted(kwargs.items()):
        if v is not None:
            key_parts.append(f"{k}:{v}")
    return "|".join(key_parts)


def _is_cache_valid(key: str) -> bool:
    """캐시가 유효한지 확인"""
    if key not in _cache:
        return False
    
    timestamp = _cache_timestamps.get(key, 0)
    elapsed = datetime.now().timestamp() - timestamp
    return elapsed < CACHE_TTL


def clear_cache():
    """캐시 초기화"""
    global _cache, _cache_timestamps
    _cache.clear()
    _cache_timestamps.clear()


def get_cached_alerts(
    goldstein_threshold: float = -5.0,
    max_alerts: int = 1000,
    base_path: Path = None,
    country: Optional[str] = None,
    category: Optional[str] = None,
    min_articles: Optional[int] = None,
    sort_by: str = 'date'
) -> Dict:
    """
    캐싱을 사용하는 get_critical_alerts 래퍼 함수
    """
    cache_key = _get_cache_key(
        'get_critical_alerts',
        threshold=goldstein_threshold,
        max_alerts=max_alerts,
        country=country,
        category=category,
        min_articles=min_articles,
        sort_by=sort_by
    )
    
    if _is_cache_valid(cache_key):
        logger.debug(f"Cache hit: {cache_key}")
        return _cache[cache_key]
    
    logger.debug(f"Cache miss: {cache_key}")
    result = get_critical_alerts(
        goldstein_threshold=goldstein_threshold,
        max_alerts=max_alerts,
        base_path=base_path,
        country=country,
        category=category,
        min_articles=min_articles,
        sort_by=sort_by
    )
    
    _cache[cache_key] = result
    _cache_timestamps[cache_key] = datetime.now().timestamp()
    
    return result

