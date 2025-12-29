"""
FRED (Federal Reserve Economic Data) API 백엔드 모듈
- 미국 기준금리 데이터 조회
- DFF: Effective Federal Funds Rate
- DFEDTARU: Federal Funds Target Range - Upper Limit
"""

import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging

load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FRED_API_KEY = os.getenv("FRED_API_KEY")
if not FRED_API_KEY:
    logger.warning("FRED_API_KEY not set in .env file. API calls will fail.")

FRED_API_BASE_URL = "https://api.stlouisfed.org/fred"
API_TIMEOUT = 30  # 30초 타임아웃

# FRED Series IDs
FRED_SERIES_DFF = "DFF"  # Effective Federal Funds Rate
FRED_SERIES_DFEDTARU = "DFEDTARU"  # Federal Funds Target Range - Upper Limit

# 인메모리 캐시 (TTL: 1시간)
_cache = {
    "data": None,
    "expires_at": None
}
CACHE_TTL_SECONDS = 3600  # 1시간


def get_latest_observation(series_id: str) -> Dict:
    """
    FRED API에서 특정 시리즈의 최신 관측값을 조회합니다.
    
    Args:
        series_id: FRED 시리즈 ID (예: "DFF", "DFEDTARU")
    
    Returns:
        dict: {
            "date": "YYYY-MM-DD",
            "value": float | None,
            "series_id": str
        } 또는 에러 정보 {"error": "..."}
    
    참고: https://fred.stlouisfed.org/docs/api/fred/series_observations.html
    """
    if not FRED_API_KEY:
        error_msg = "FRED_API_KEY not configured. Please set FRED_API_KEY in .env file."
        logger.error(error_msg)
        return {"error": error_msg}
    
    # FRED API 엔드포인트
    url = f"{FRED_API_BASE_URL}/series/observations"
    
    # 쿼리 파라미터
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "sort_order": "desc",  # 최신값부터
        "limit": 1  # 최신 1개만
    }
    
    logger.info(f"FRED API Request: series_id={series_id}")
    logger.debug(f"Request URL: {url}, params={params}")
    
    try:
        response = requests.get(url, params=params, timeout=API_TIMEOUT)
        response.raise_for_status()
        
        data = response.json()
        
        # FRED API 응답 구조 검증
        if 'observations' not in data:
            error_msg = "Invalid API response format: missing 'observations'"
            logger.error(error_msg)
            return {"error": error_msg, "response": data}
        
        observations = data.get('observations', [])
        
        if not observations or len(observations) == 0:
            logger.warning(f"No observations found for series_id={series_id}")
            return {
                "date": None,
                "value": None,
                "series_id": series_id,
                "error": "No observations available"
            }
        
        # 최신 관측값 추출
        latest = observations[0]
        date_str = latest.get('date', '')
        value_str = latest.get('value', '')
        
        # FRED API는 값이 없을 때 "." 또는 빈 문자열을 반환
        value = None
        if value_str and value_str != '.' and value_str.strip():
            try:
                value = float(value_str)
            except (ValueError, TypeError):
                logger.warning(f"Invalid value format for series_id={series_id}: {value_str}")
                value = None
        
        result = {
            "date": date_str,
            "value": value,
            "series_id": series_id
        }
        
        logger.info(f"Successfully retrieved latest observation for {series_id}: date={date_str}, value={value}")
        return result
        
    except requests.exceptions.Timeout:
        error_msg = f"Request timeout after {API_TIMEOUT} seconds"
        logger.error(error_msg)
        return {"error": error_msg}
    
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response else None
        
        # 429 Too Many Requests 처리
        if status_code == 429:
            error_msg = "FRED API rate limit exceeded. Please try again later."
            logger.error(error_msg)
            return {"error": error_msg, "status_code": status_code}
        
        error_msg = f"HTTP Error {status_code}: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg, "status_code": status_code}
    
    except requests.exceptions.RequestException as e:
        error_msg = f"Request failed: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}
    
    except ValueError as e:
        error_msg = f"JSON parsing error: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}
    
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {"error": error_msg}


def get_us_rates(use_cache: bool = True) -> Dict:
    """
    미국 기준금리 2종(DFF, DFEDTARU)을 조회하여 반환합니다.
    캐시를 사용하여 API 호출을 최소화합니다.
    
    Args:
        use_cache: 캐시 사용 여부 (기본값: True)
    
    Returns:
        dict: {
            "source": "FRED",
            "asOf": "YYYY-MM-DD",
            "effective": {
                "seriesId": "DFF",
                "date": "YYYY-MM-DD",
                "ratePct": float
            },
            "targetUpper": {
                "seriesId": "DFEDTARU",
                "date": "YYYY-MM-DD",
                "ratePct": float
            }
        } 또는 에러 정보
    """
    global _cache
    
    # 캐시 확인
    if use_cache and _cache["data"] is not None and _cache["expires_at"] is not None:
        if datetime.now() < _cache["expires_at"]:
            logger.info("Returning cached US rates data")
            return _cache["data"]
        else:
            logger.info("Cache expired, fetching new data")
    
    logger.info("Fetching US interest rates from FRED API")
    
    # DFF (Effective Federal Funds Rate) 조회
    effective_result = get_latest_observation(FRED_SERIES_DFF)
    if "error" in effective_result:
        logger.error(f"Failed to fetch DFF: {effective_result['error']}")
        # 실패 시 stale 캐시가 있으면 반환
        if _cache["data"] is not None:
            logger.warning("API call failed, returning stale cache with warning")
            stale_data = _cache["data"].copy()
            stale_data["warning"] = f"Using cached data due to API error: {effective_result['error']}"
            return stale_data
        return {"error": f"Failed to fetch effective rate: {effective_result['error']}"}
    
    # DFEDTARU (Federal Funds Target Range - Upper Limit) 조회
    target_upper_result = get_latest_observation(FRED_SERIES_DFEDTARU)
    if "error" in target_upper_result:
        logger.error(f"Failed to fetch DFEDTARU: {target_upper_result['error']}")
        # 실패 시 stale 캐시가 있으면 반환
        if _cache["data"] is not None:
            logger.warning("API call failed, returning stale cache with warning")
            stale_data = _cache["data"].copy()
            stale_data["warning"] = f"Using cached data due to API error: {target_upper_result['error']}"
            return stale_data
        return {"error": f"Failed to fetch target upper rate: {target_upper_result['error']}"}
    
    # 최신 날짜 결정 (두 시리즈 중 더 최근 날짜)
    effective_date = effective_result.get('date', '')
    target_upper_date = target_upper_result.get('date', '')
    
    # 날짜 비교 (YYYY-MM-DD 형식)
    as_of_date = effective_date
    if target_upper_date and effective_date:
        try:
            eff_dt = datetime.strptime(effective_date, '%Y-%m-%d')
            tar_dt = datetime.strptime(target_upper_date, '%Y-%m-%d')
            if tar_dt > eff_dt:
                as_of_date = target_upper_date
        except ValueError:
            pass  # 날짜 파싱 실패 시 effective_date 사용
    
    # 결과 구성
    result = {
        "source": "FRED",
        "asOf": as_of_date,
        "effective": {
            "seriesId": FRED_SERIES_DFF,
            "date": effective_date,
            "ratePct": effective_result.get('value')
        },
        "targetUpper": {
            "seriesId": FRED_SERIES_DFEDTARU,
            "date": target_upper_date,
            "ratePct": target_upper_result.get('value')
        }
    }
    
    # 캐시에 저장
    _cache["data"] = result
    _cache["expires_at"] = datetime.now() + timedelta(seconds=CACHE_TTL_SECONDS)
    logger.info(f"Cached US rates data (expires at {_cache['expires_at']})")
    
    logger.info(f"Successfully retrieved US rates: effective={effective_result.get('value')}, targetUpper={target_upper_result.get('value')}")
    return result
