"""
KCCI (Korea Container Freight Index) API

Flask Blueprint for KCCI data endpoints
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, date, timedelta
from typing import Optional
import logging

from .models import KCCIIndex, KCCIRouteIndex, KCCICollectionLog, get_kcci_session, init_kcci_database
from .collector import KCCICollector, collect_kcci_and_save

logger = logging.getLogger(__name__)

# Flask Blueprint
kcci_bp = Blueprint('kcci', __name__, url_prefix='/api/kcci')


@kcci_bp.route('/comprehensive', methods=['GET'])
def get_comprehensive_index():
    """
    KCCI 종합지수 조회
    
    Parameters:
    - start_date: 조회 시작일 (YYYY-MM-DD, 선택)
    - end_date: 조회 종료일 (YYYY-MM-DD, 선택)
    - limit: 반환할 최대 개수 (기본값: 100)
    
    Returns:
    - data: KCCI 종합지수 리스트
    - latest: 최신 데이터
    - count: 데이터 개수
    """
    try:
        import sqlite3
        import os
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, 'kcci.db')
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 파라미터 파싱
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', 100, type=int)
        
        # 쿼리 구성
        query = "SELECT id, week_date, index_code, index_name, current_index, previous_index, weekly_change, weekly_change_rate, source_url, collected_at FROM kcci_index WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND week_date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND week_date <= ?"
            params.append(end_date)
        
        query += " ORDER BY week_date DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        data = []
        for row in rows:
            data.append({
                'id': row['id'],
                'week_date': row['week_date'],
                'index_code': row['index_code'],
                'index_name': row['index_name'],
                'current_index': row['current_index'],
                'previous_index': row['previous_index'],
                'weekly_change': row['weekly_change'],
                'weekly_change_rate': row['weekly_change_rate'],
                'source_url': row['source_url'],
                'collected_at': row['collected_at']
            })
        
        # 시계열 순서로 정렬 (오래된 것부터)
        data.reverse()
        
        return jsonify({
            'success': True,
            'data': data,
            'latest': data[-1] if data else None,
            'count': len(data),
            'source': '한국해양진흥공사(KOBC)',
            'index_name': 'KCCI (Korea Container Freight Index)'
        })
        
    except Exception as e:
        logger.error(f"Error fetching KCCI comprehensive index: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'data': []
        }), 500


@kcci_bp.route('/routes', methods=['GET'])
def get_route_indices():
    """
    항로별 KCCI 지수 조회
    
    Parameters:
    - route_code: 특정 항로 코드 (예: KUWI, KUEI)
    - route_group: 항로 그룹 (Mainlane, Non-Mainlane, Intra Asia)
    - start_date: 조회 시작일 (YYYY-MM-DD, 선택)
    - end_date: 조회 종료일 (YYYY-MM-DD, 선택)
    - limit: 반환할 최대 개수 (기본값: 500)
    
    Returns:
    - data: 항로별 지수 리스트
    - routes: 유니크한 항로 정보
    - count: 데이터 개수
    """
    try:
        init_kcci_database()
        session = get_kcci_session()
        
        # 파라미터 파싱
        route_code = request.args.get('route_code')
        route_group = request.args.get('route_group')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', 500, type=int)
        
        # 쿼리 구성
        query = session.query(KCCIRouteIndex)
        
        if route_code:
            query = query.filter(KCCIRouteIndex.route_code == route_code.upper())
        
        if route_group:
            query = query.filter(KCCIRouteIndex.route_group == route_group)
        
        if start_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                query = query.filter(KCCIRouteIndex.week_date >= start)
            except ValueError:
                pass
        
        if end_date:
            try:
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(KCCIRouteIndex.week_date <= end)
            except ValueError:
                pass
        
        # 정렬 및 제한
        query = query.order_by(KCCIRouteIndex.week_date.desc(), KCCIRouteIndex.route_code).limit(limit)
        
        results = query.all()
        
        # 유니크 항로 정보 추출
        routes_info = {}
        for r in results:
            if r.route_code not in routes_info:
                routes_info[r.route_code] = {
                    'route_code': r.route_code,
                    'route_name': r.route_name,
                    'route_group': r.route_group
                }
        
        session.close()
        
        data = [r.to_dict() for r in results]
        
        # 시계열 순서로 정렬
        data.sort(key=lambda x: (x['week_date'], x['route_code']))
        
        return jsonify({
            'success': True,
            'data': data,
            'routes': list(routes_info.values()),
            'count': len(data),
            'source': '한국해양진흥공사(KOBC)'
        })
        
    except Exception as e:
        logger.error(f"Error fetching KCCI route indices: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'data': []
        }), 500


@kcci_bp.route('/routes/latest', methods=['GET'])
def get_latest_route_indices():
    """
    최신 항로별 KCCI 지수 조회
    
    Returns:
    - data: 최신 주차의 모든 항로 지수
    - week_date: 기준 주차
    """
    try:
        init_kcci_database()
        
        # Raw SQL을 사용하여 컬럼 매핑 문제 해결
        import sqlite3
        import os
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, 'kcci.db')
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # 컬럼 이름으로 접근 가능하게
        cursor = conn.cursor()
        
        # 최신 주차 확인
        cursor.execute("SELECT MAX(week_date) FROM kcci_route_index")
        latest_week = cursor.fetchone()[0]
        
        if not latest_week:
            conn.close()
            return jsonify({
                'success': True,
                'data': [],
                'week_date': None,
                'count': 0
            })
        
        # 최신 주차의 모든 항로 조회
        cursor.execute("""
            SELECT id, week_date, route_group, route_code, route_name, 
                   weight, current_index, previous_index, weekly_change, 
                   weekly_change_rate, source_url, collected_at
            FROM kcci_route_index 
            WHERE week_date = ?
            ORDER BY route_code
        """, (latest_week,))
        
        rows = cursor.fetchall()
        conn.close()
        
        data = []
        for row in rows:
            data.append({
                'id': row['id'],
                'week_date': row['week_date'],
                'route_group': row['route_group'],
                'route_code': row['route_code'],
                'route_name': row['route_name'],
                'weight': row['weight'],
                'current_index': row['current_index'],
                'previous_index': row['previous_index'],
                'weekly_change': row['weekly_change'],
                'weekly_change_rate': row['weekly_change_rate'],
                'source_url': row['source_url'],
                'collected_at': row['collected_at']
            })
        
        return jsonify({
            'success': True,
            'data': data,
            'week_date': latest_week,
            'count': len(data),
            'source': '한국해양진흥공사(KOBC)'
        })
        
    except Exception as e:
        logger.error(f"Error fetching latest KCCI route indices: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'data': []
        }), 500


@kcci_bp.route('/collect', methods=['POST'])
def trigger_collection():
    """
    KCCI 데이터 수집 수동 트리거
    
    Returns:
    - success: 수집 성공 여부
    - data: 수집된 데이터 요약
    """
    try:
        result = collect_kcci_and_save()
        
        return jsonify({
            'success': result.get('success', False),
            'week_date': result.get('week_date').isoformat() if result.get('week_date') else None,
            'comprehensive': result.get('comprehensive'),
            'route_count': len(result.get('routes', [])),
            'duration_seconds': result.get('duration_seconds'),
            'error': result.get('error')
        })
        
    except Exception as e:
        logger.error(f"Error triggering KCCI collection: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@kcci_bp.route('/logs', methods=['GET'])
def get_collection_logs():
    """
    KCCI 수집 로그 조회
    
    Parameters:
    - limit: 반환할 최대 개수 (기본값: 20)
    
    Returns:
    - logs: 수집 로그 리스트
    """
    try:
        init_kcci_database()
        session = get_kcci_session()
        
        limit = request.args.get('limit', 20, type=int)
        
        logs = session.query(KCCICollectionLog).order_by(
            KCCICollectionLog.executed_at.desc()
        ).limit(limit).all()
        
        session.close()
        
        return jsonify({
            'success': True,
            'logs': [log.to_dict() for log in logs],
            'count': len(logs)
        })
        
    except Exception as e:
        logger.error(f"Error fetching KCCI collection logs: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'logs': []
        }), 500


@kcci_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    KCCI 데이터 통계
    
    Returns:
    - total_weeks: 총 주차 수
    - date_range: 데이터 기간
    - latest: 최신 데이터
    - change: 변동 정보
    """
    try:
        init_kcci_database()
        session = get_kcci_session()
        
        # 종합지수 통계
        total = session.query(KCCIIndex).count()
        
        oldest = session.query(KCCIIndex).order_by(KCCIIndex.week_date.asc()).first()
        latest = session.query(KCCIIndex).order_by(KCCIIndex.week_date.desc()).first()
        
        # 최근 변동 계산
        recent_data = session.query(KCCIIndex).order_by(
            KCCIIndex.week_date.desc()
        ).limit(4).all()
        
        session.close()
        
        stats = {
            'total_weeks': total,
            'date_range': {
                'start': oldest.week_date.isoformat() if oldest else None,
                'end': latest.week_date.isoformat() if latest else None
            },
            'latest': latest.to_dict() if latest else None,
        }
        
        # 변동 계산
        if len(recent_data) >= 2:
            current = recent_data[0].current_index
            previous = recent_data[1].current_index
            change = current - previous
            change_rate = (change / previous * 100) if previous else 0
            
            stats['change'] = {
                'value': round(change, 2),
                'rate': round(change_rate, 2),
                'direction': 'up' if change > 0 else ('down' if change < 0 else 'unchanged')
            }
        
        # 4주 평균
        if recent_data:
            avg_4w = sum(r.current_index for r in recent_data) / len(recent_data)
            stats['average_4w'] = round(avg_4w, 2)
        
        return jsonify({
            'success': True,
            'stats': stats,
            'source': '한국해양진흥공사(KOBC)',
            'update_schedule': '매주 월요일 14:00'
        })
        
    except Exception as e:
        logger.error(f"Error fetching KCCI stats: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@kcci_bp.route('/chart-data', methods=['GET'])
def get_chart_data():
    """
    시각화용 차트 데이터 반환
    
    Parameters:
    - period: 기간 (3M, 6M, 1Y, ALL, 기본값: 6M)
    - route_codes: 항로 코드 리스트 (콤마 구분, 선택)
    - include_routes: 항로별 데이터 포함 여부 (기본값: false)
    
    Returns:
    - comprehensive: 종합지수 시계열 데이터
    - routes: 항로별 시계열 데이터 (optional)
    """
    try:
        import sqlite3
        import os
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, 'kcci.db')
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 파라미터 파싱
        period = request.args.get('period', '6M')
        route_codes = request.args.get('route_codes', '')
        include_routes = request.args.get('include_routes', 'false').lower() == 'true'
        
        # 기간 계산
        end_date = date.today()
        if period == '3M':
            start_date = end_date - timedelta(days=90)
        elif period == '6M':
            start_date = end_date - timedelta(days=180)
        elif period == '1Y':
            start_date = end_date - timedelta(days=365)
        elif period == 'ALL':
            start_date = date(2000, 1, 1)
        else:
            start_date = end_date - timedelta(days=180)
        
        # 종합지수 조회 (Raw SQL)
        cursor.execute("""
            SELECT week_date, current_index, previous_index, weekly_change, weekly_change_rate
            FROM kcci_index 
            WHERE week_date >= ? AND week_date <= ?
            ORDER BY week_date ASC
        """, (start_date.isoformat(), end_date.isoformat()))
        
        comprehensive_rows = cursor.fetchall()
        
        comprehensive_data = []
        for row in comprehensive_rows:
            comprehensive_data.append({
                'week_date': row['week_date'],
                'current_index': row['current_index'],
                'previous_index': row['previous_index'],
                'weekly_change': row['weekly_change'],
                'weekly_change_rate': row['weekly_change_rate']
            })
        
        response = {
            'success': True,
            'period': period,
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'comprehensive': {
                'labels': [d['week_date'] for d in comprehensive_data],
                'values': [d['current_index'] for d in comprehensive_data],
                'data': comprehensive_data
            },
            'source': '한국해양진흥공사(KOBC)',
            'index_name': 'KCCI (Korea Container Freight Index)'
        }
        
        # 항로별 데이터 포함
        if include_routes:
            if route_codes:
                codes = [c.strip().upper() for c in route_codes.split(',') if c.strip()]
                placeholders = ','.join(['?' for _ in codes])
                cursor.execute(f"""
                    SELECT route_code, route_name, route_group, week_date, current_index
                    FROM kcci_route_index 
                    WHERE week_date >= ? AND week_date <= ? AND route_code IN ({placeholders})
                    ORDER BY route_code, week_date
                """, [start_date.isoformat(), end_date.isoformat()] + codes)
            else:
                cursor.execute("""
                    SELECT route_code, route_name, route_group, week_date, current_index
                    FROM kcci_route_index 
                    WHERE week_date >= ? AND week_date <= ?
                    ORDER BY route_code, week_date
                """, (start_date.isoformat(), end_date.isoformat()))
            
            route_rows = cursor.fetchall()
            
            # 항로별로 그룹화
            routes_grouped = {}
            for row in route_rows:
                code = row['route_code']
                if code not in routes_grouped:
                    routes_grouped[code] = {
                        'route_code': code,
                        'route_name': row['route_name'],
                        'route_group': row['route_group'],
                        'labels': [],
                        'values': []
                    }
                routes_grouped[code]['labels'].append(row['week_date'])
                routes_grouped[code]['values'].append(row['current_index'])
            
            response['routes'] = list(routes_grouped.values())
        
        conn.close()
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error fetching KCCI chart data: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

