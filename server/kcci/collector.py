"""
KCCI (Korea Container Freight Index) Web Collector

KOBC 공식 웹사이트에서 KCCI 데이터를 수집하는 모듈
- 수집 대상: https://kobc.or.kr/ebz/shippinginfo/kcci/gridList.do
- 수집 방식: HTML 테이블 파싱 (SSR 기반, JavaScript 불필요)
- 수집 주기: 매주 월요일 14:30 이후
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, date, timezone
from typing import Dict, List, Optional
import logging
import re
import time

logger = logging.getLogger(__name__)


class KCCICollector:
    """
    KCCI 데이터 수집기
    
    KOBC 웹사이트에서 KCCI 종합지수 및 항로별 지수 수집
    
    테이블 구조 (2024년 12월 기준):
    - Row 0: Headers (Group, Code, Route, Weight, Current Index+날짜, Previous Index+날짜, Weekly Change)
    - Row 1: KCCI Comprehensive Index
    - Row 2+: Route Indices (그룹 시작 행은 7셀, 나머지는 6셀 - rowspan)
    """
    
    # KOBC KCCI 페이지 URL
    KCCI_URL = "https://kobc.or.kr/ebz/shippinginfo/kcci/gridList.do?mId=0304000000"
    
    # 항로 코드 → 그룹 매핑
    ROUTE_GROUPS = {
        'KUWI': 'Mainlane',      # US West Coast
        'KUEI': 'Mainlane',      # US East Coast
        'KNEI': 'Mainlane',      # Europe
        'KMDI': 'Mainlane',      # Mediterranean
        'KMEI': 'Non-Mainlane',  # Middle East
        'KAUI': 'Non-Mainlane',  # Australia
        'KLEI': 'Non-Mainlane',  # Latin America East
        'KLWI': 'Non-Mainlane',  # Latin America West
        'KSAI': 'Non-Mainlane',  # South Africa
        'KWAI': 'Non-Mainlane',  # West Africa
        'KCI': 'Intra Asia',     # China
        'KJI': 'Intra Asia',     # Japan
        'KSEI': 'Intra Asia',    # Southeast Asia
    }
    
    # 항로 코드 → 영문명 매핑
    ROUTE_NAMES = {
        'KUWI': 'US West Coast',
        'KUEI': 'US East Coast',
        'KNEI': 'Europe',
        'KMDI': 'Mediterranean',
        'KMEI': 'Middle East',
        'KAUI': 'Australia',
        'KLEI': 'Latin America East',
        'KLWI': 'Latin America West',
        'KSAI': 'South Africa',
        'KWAI': 'West Africa',
        'KCI': 'China',
        'KJI': 'Japan',
        'KSEI': 'Southeast Asia',
    }
    
    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        })
    
    def collect(self) -> Dict:
        """KCCI 데이터 수집 메인 함수"""
        start_time = time.time()
        
        try:
            logger.info("Starting KCCI data collection from KOBC...")
            
            response = self.session.get(self.KCCI_URL, timeout=self.timeout)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            table = soup.find('table')
            if not table:
                raise ValueError("KCCI table not found on page")
            
            rows = table.find_all('tr')
            if len(rows) < 2:
                raise ValueError("KCCI table has insufficient rows")
            
            # 헤더에서 날짜 추출
            week_date = self._extract_date_from_header(rows[0])
            
            # 데이터 추출
            comprehensive = None
            routes = []
            current_group = 'Unknown'
            
            for row in rows[1:]:
                cells = row.find_all(['td', 'th'])
                if len(cells) < 6:
                    continue
                
                cell_texts = [c.get_text(strip=True) for c in cells]
                
                # 종합지수 행 (Code = KCCI)
                if 'KCCI' in cell_texts:
                    comprehensive = self._parse_comprehensive_row(cell_texts)
                else:
                    # 항로별 지수 행
                    route_data, group = self._parse_route_row(cell_texts, current_group)
                    if group:
                        current_group = group
                    if route_data:
                        routes.append(route_data)
            
            duration = time.time() - start_time
            
            logger.info(f"KCCI collection completed: date={week_date}, "
                       f"comprehensive={comprehensive.get('current_index') if comprehensive else None}, "
                       f"routes={len(routes)}")
            
            return {
                'success': True,
                'week_date': week_date,
                'comprehensive': comprehensive,
                'routes': routes,
                'error': None,
                'duration_seconds': duration
            }
            
        except requests.RequestException as e:
            duration = time.time() - start_time
            error_msg = f"HTTP request failed: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'week_date': None,
                'comprehensive': None,
                'routes': [],
                'error': error_msg,
                'duration_seconds': duration
            }
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Collection error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                'success': False,
                'week_date': None,
                'comprehensive': None,
                'routes': [],
                'error': error_msg,
                'duration_seconds': duration
            }
    
    def _extract_date_from_header(self, header_row) -> Optional[date]:
        """헤더 행에서 기준 날짜 추출"""
        try:
            header_text = header_row.get_text()
            match = re.search(r'(\d{4})[-./](\d{2})[-./](\d{2})', header_text)
            if match:
                year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
                return date(year, month, day)
            return date.today()
        except Exception as e:
            logger.warning(f"Error extracting date: {e}")
            return date.today()
    
    def _parse_number(self, text: str) -> Optional[float]:
        """텍스트에서 숫자 추출 (쉼표 제거)"""
        if not text:
            return None
        text = text.replace(',', '')
        match = re.search(r'^([+-]?\d+\.?\d*)', text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
        return None
    
    def _parse_change_rate(self, text: str) -> Optional[float]:
        """변동률 추출: "-1(-0.06%)" -> -0.06"""
        if not text:
            return None
        match = re.search(r'\(([+-]?\d+\.?\d*)%?\)', text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
        return None
    
    def _parse_comprehensive_row(self, cells: List[str]) -> Optional[Dict]:
        """
        종합지수 행 파싱
        
        7 cells: [Group, Code, Route, Weight, Current, Previous, Change]
        예: ['Index', 'KCCI', 'Comprehensive Index', '100%', '1,805', '1,806', '-1(-0.06%)']
        """
        try:
            if len(cells) < 7:
                return None
            
            # [Group, Code=KCCI, Route, Weight, Current, Previous, Change]
            current_index = self._parse_number(cells[4])
            previous_index = self._parse_number(cells[5])
            weekly_change = self._parse_number(cells[6])
            weekly_change_rate = self._parse_change_rate(cells[6])
            
            if current_index is None:
                return None
            
            return {
                'current_index': current_index,
                'previous_index': previous_index,
                'weekly_change': weekly_change,
                'weekly_change_rate': weekly_change_rate,
            }
        except Exception as e:
            logger.error(f"Error parsing comprehensive row: {e}")
            return None
    
    def _parse_route_row(self, cells: List[str], current_group: str):
        """
        항로별 지수 행 파싱
        
        7 cells: [Group, Code, Route, Weight, Current, Previous, Change] - 그룹 시작 행
        6 cells: [Code, Route, Weight, Current, Previous, Change] - rowspan으로 그룹 생략된 행
        """
        try:
            new_group = None
            
            if len(cells) == 7:
                # 그룹 시작 행
                new_group = cells[0]  # Group
                route_code = cells[1]
                route_name = cells[2]
                weight_str = cells[3]
                current_str = cells[4]
                previous_str = cells[5]
                change_str = cells[6]
            elif len(cells) == 6:
                # 그룹 생략 행
                route_code = cells[0]
                route_name = cells[1]
                weight_str = cells[2]
                current_str = cells[3]
                previous_str = cells[4]
                change_str = cells[5]
            else:
                return None, None
            
            # 항로 코드 검증 (K로 시작하는 코드)
            if not route_code.upper().startswith('K'):
                return None, new_group
            
            # KCCI 종합지수 건너뛰기
            if route_code.upper() == 'KCCI':
                return None, new_group
            
            route_code = route_code.upper()
            
            # 가중치 파싱
            weight = None
            weight_match = re.search(r'(\d+\.?\d*)', weight_str)
            if weight_match:
                weight = float(weight_match.group(1))
            
            # 지수 값 파싱
            current_index = self._parse_number(current_str)
            previous_index = self._parse_number(previous_str)
            weekly_change = self._parse_number(change_str)
            weekly_change_rate = self._parse_change_rate(change_str)
            
            if current_index is None:
                return None, new_group
            
            # 표준화된 이름 사용
            std_name = self.ROUTE_NAMES.get(route_code, route_name)
            route_group = new_group if new_group else current_group
            
            # 그룹명이 Unknown이면 매핑에서 찾기
            if route_group == 'Unknown' or not route_group:
                route_group = self.ROUTE_GROUPS.get(route_code, 'Unknown')
            
            return {
                'route_code': route_code,
                'route_name': std_name,
                'route_group': route_group,
                'weight': weight,
                'current_index': current_index,
                'previous_index': previous_index,
                'weekly_change': weekly_change,
                'weekly_change_rate': weekly_change_rate,
            }, new_group
            
        except Exception as e:
            logger.error(f"Error parsing route row: {e}")
            return None, None


def collect_kcci_and_save():
    """
    KCCI 데이터 수집 및 데이터베이스 저장
    
    스케줄러에서 호출하는 메인 함수
    """
    from .models import KCCIIndex, KCCIRouteIndex, KCCICollectionLog, get_kcci_session, init_kcci_database
    
    # 데이터베이스 초기화
    init_kcci_database()
    
    # 수집 실행
    collector = KCCICollector()
    result = collector.collect()
    
    session = get_kcci_session()
    
    try:
        # 수집 로그 생성
        log = KCCICollectionLog(
            week_date=result.get('week_date'),
            comprehensive_index=result.get('comprehensive', {}).get('current_index') if result.get('comprehensive') else None,
            route_count=len(result.get('routes', [])),
            is_success=1 if result.get('success') else 0,
            error_message=result.get('error'),
            duration_seconds=result.get('duration_seconds')
        )
        session.add(log)
        
        if result.get('success') and result.get('week_date'):
            week_date = result['week_date']
            
            # 종합지수 저장 (덮어쓰기)
            if result.get('comprehensive'):
                existing = session.query(KCCIIndex).filter(
                    KCCIIndex.week_date == week_date
                ).first()
                
                comp = result['comprehensive']
                
                if existing:
                    existing.current_index = comp['current_index']
                    existing.previous_index = comp.get('previous_index')
                    existing.weekly_change = comp.get('weekly_change')
                    existing.weekly_change_rate = comp.get('weekly_change_rate')
                    existing.collected_at = datetime.now(timezone.utc)
                    existing.source_url = collector.KCCI_URL
                    logger.info(f"Updated existing KCCI index: {week_date} = {comp['current_index']}")
                else:
                    kcci_index = KCCIIndex(
                        week_date=week_date,
                        current_index=comp['current_index'],
                        previous_index=comp.get('previous_index'),
                        weekly_change=comp.get('weekly_change'),
                        weekly_change_rate=comp.get('weekly_change_rate'),
                        source_url=collector.KCCI_URL
                    )
                    session.add(kcci_index)
                    logger.info(f"Inserted new KCCI index: {week_date} = {comp['current_index']}")
            
            # 항로별 지수 저장
            for route in result.get('routes', []):
                existing_route = session.query(KCCIRouteIndex).filter(
                    KCCIRouteIndex.week_date == week_date,
                    KCCIRouteIndex.route_code == route['route_code']
                ).first()
                
                if existing_route:
                    existing_route.current_index = route['current_index']
                    existing_route.previous_index = route.get('previous_index')
                    existing_route.weekly_change = route.get('weekly_change')
                    existing_route.weekly_change_rate = route.get('weekly_change_rate')
                    existing_route.weight = route.get('weight')
                    existing_route.route_name = route.get('route_name')
                    existing_route.route_group = route.get('route_group')
                    existing_route.collected_at = datetime.now(timezone.utc)
                else:
                    route_index = KCCIRouteIndex(
                        week_date=week_date,
                        route_code=route['route_code'],
                        route_name=route.get('route_name', route['route_code']),
                        route_group=route.get('route_group'),
                        weight=route.get('weight'),
                        current_index=route['current_index'],
                        previous_index=route.get('previous_index'),
                        weekly_change=route.get('weekly_change'),
                        weekly_change_rate=route.get('weekly_change_rate'),
                        source_url=collector.KCCI_URL
                    )
                    session.add(route_index)
        
        session.commit()
        logger.info(f"KCCI data saved: week_date={result.get('week_date')}, "
                   f"routes={len(result.get('routes', []))}")
        
        return result
        
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to save KCCI data: {e}", exc_info=True)
        return {
            'success': False,
            'error': f"Database error: {str(e)}"
        }
    finally:
        session.close()
