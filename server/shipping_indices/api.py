"""
Shipping Indices API (SCFI, CCFI, BDI)

Flask Blueprint for shipping indices data endpoints
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, date, timedelta
import logging
import sqlite3
import os

from .models import (
    SCFIIndex, CCFIIndex, BDIIndex,
    init_shipping_indices_database, get_shipping_indices_session
)

logger = logging.getLogger(__name__)

# Flask Blueprint
shipping_bp = Blueprint('shipping_indices', __name__, url_prefix='/api/shipping-indices')

# 데이터베이스 경로
def get_db_path():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, 'shipping_indices.db')


# =============================================================================
# SCFI API Endpoints
# =============================================================================

@shipping_bp.route('/scfi', methods=['GET'])
def get_scfi_index():
    """
    SCFI 지수 조회
    
    Parameters:
    - start_date: 조회 시작일 (YYYY-MM-DD, 선택)
    - end_date: 조회 종료일 (YYYY-MM-DD, 선택)
    - limit: 반환할 최대 개수 (기본값: 500)
    """
    try:
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', 500, type=int)
        
        query = """
            SELECT id, index_date, index_code, index_name, 
                   current_index, previous_index, change, change_rate, 
                   source, collected_at 
            FROM scfi_index WHERE 1=1
        """
        params = []
        
        if start_date:
            query += " AND index_date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND index_date <= ?"
            params.append(end_date)
        
        query += " ORDER BY index_date DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        data = []
        for row in rows:
            data.append({
                'id': row['id'],
                'index_date': row['index_date'],
                'index_code': row['index_code'],
                'index_name': row['index_name'],
                'current_index': row['current_index'],
                'previous_index': row['previous_index'],
                'change': row['change'],
                'change_rate': row['change_rate'],
                'source': row['source'],
                'collected_at': row['collected_at']
            })
        
        # 시계열 순서로 정렬 (오래된 것부터)
        data.reverse()
        
        return jsonify({
            'success': True,
            'data': data,
            'latest': data[-1] if data else None,
            'count': len(data),
            'source': 'Shanghai Shipping Exchange (SSE)',
            'unit': 'pt',
            'index_name': 'SCFI (Shanghai Containerized Freight Index)',
            'description': 'The Shanghai Containerized Freight Index (SCFI) has been published by the Shanghai Shipping Exchange (SSE) since December 7, 2005. It reflects spot freight rates for container shipping from Shanghai to 15 major destinations. Originally based on time charter rates, since October 16, 2009, it is calculated based on container freight rates in USD per TEU (20-foot equivalent unit). The index covers CY-CY shipping conditions for General Dry Cargo Containers. The freight rate for each route is the arithmetic average of all rates on that route, including surcharges related to maritime transport. Freight information is provided by panelists including liner carriers and forwarders from CCFI.'
        })
        
    except Exception as e:
        logger.error(f"Error fetching SCFI index: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'data': []
        }), 500


@shipping_bp.route('/scfi/stats', methods=['GET'])
def get_scfi_stats():
    """SCFI 통계 정보"""
    try:
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 총 개수
        cursor.execute("SELECT COUNT(*) as cnt FROM scfi_index")
        total = cursor.fetchone()['cnt']
        
        # 기간
        cursor.execute("SELECT MIN(index_date) as min_date, MAX(index_date) as max_date FROM scfi_index")
        date_range = cursor.fetchone()
        
        # 최신 데이터
        cursor.execute("SELECT * FROM scfi_index ORDER BY index_date DESC LIMIT 1")
        latest_row = cursor.fetchone()
        
        # 최근 4주 데이터 (평균 계산용)
        cursor.execute("SELECT current_index FROM scfi_index ORDER BY index_date DESC LIMIT 4")
        recent_rows = cursor.fetchall()
        
        conn.close()
        
        stats = {
            'total_records': total,
            'date_range': {
                'start': date_range['min_date'],
                'end': date_range['max_date']
            }
        }
        
        if latest_row:
            stats['latest'] = {
                'index_date': latest_row['index_date'],
                'current_index': latest_row['current_index'],
                'change': latest_row['change'],
                'change_rate': latest_row['change_rate']
            }
        
        if recent_rows:
            avg_4w = sum(r['current_index'] for r in recent_rows) / len(recent_rows)
            stats['average_4w'] = round(avg_4w, 2)
        
        return jsonify({
            'success': True,
            'stats': stats,
            'source': 'Shanghai Shipping Exchange (SSE)',
            'unit': 'pt'
        })
        
    except Exception as e:
        logger.error(f"Error fetching SCFI stats: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@shipping_bp.route('/scfi/chart-data', methods=['GET'])
def get_scfi_chart_data():
    """SCFI 차트 데이터"""
    try:
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        period = request.args.get('period', '6M')
        
        end_date = date.today()
        if period == '1W':
            start_date = end_date - timedelta(days=7)
        elif period == '1M':
            start_date = end_date - timedelta(days=30)
        elif period == '3M':
            start_date = end_date - timedelta(days=90)
        elif period == '6M':
            start_date = end_date - timedelta(days=180)
        elif period == '1Y':
            start_date = end_date - timedelta(days=365)
        elif period == 'ALL' or period == 'MAX':
            start_date = date(2000, 1, 1)
        else:
            start_date = end_date - timedelta(days=180)
        
        cursor.execute("""
            SELECT index_date, current_index, previous_index, change, change_rate
            FROM scfi_index 
            WHERE index_date >= ? AND index_date <= ?
            ORDER BY index_date ASC
        """, (start_date.isoformat(), end_date.isoformat()))
        
        rows = cursor.fetchall()
        conn.close()
        
        data = []
        for row in rows:
            data.append({
                'index_date': row['index_date'],
                'current_index': row['current_index'],
                'previous_index': row['previous_index'],
                'change': row['change'],
                'change_rate': row['change_rate']
            })
        
        # 통계 계산
        if data:
            values = [d['current_index'] for d in data]
            stats = {
                'high': max(values),
                'low': min(values),
                'average': round(sum(values) / len(values), 2),
                'start_value': values[0],
                'end_value': values[-1],
                'change': round(values[-1] - values[0], 2),
                'change_rate': round((values[-1] - values[0]) / values[0] * 100, 2) if values[0] else 0
            }
        else:
            stats = {}
        
        return jsonify({
            'success': True,
            'period': period,
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'labels': [d['index_date'] for d in data],
            'values': [d['current_index'] for d in data],
            'data': data,
            'stats': stats,
            'source': 'Shanghai Shipping Exchange (SSE)',
            'unit': 'pt',
            'index_name': 'SCFI (Shanghai Containerized Freight Index)',
            'description': 'The Shanghai Containerized Freight Index (SCFI) has been published by the Shanghai Shipping Exchange (SSE) since December 7, 2005. It reflects spot freight rates for container shipping from Shanghai to 15 major destinations. Originally based on time charter rates, since October 16, 2009, it is calculated based on container freight rates in USD per TEU (20-foot equivalent unit). The index covers CY-CY shipping conditions for General Dry Cargo Containers. The freight rate for each route is the arithmetic average of all rates on that route, including surcharges related to maritime transport. Freight information is provided by panelists including liner carriers and forwarders from CCFI.'
        })
        
    except Exception as e:
        logger.error(f"Error fetching SCFI chart data: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


# =============================================================================
# CCFI API Endpoints
# =============================================================================

@shipping_bp.route('/ccfi', methods=['GET'])
def get_ccfi_index():
    """CCFI 지수 조회"""
    try:
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', 500, type=int)
        
        query = """
            SELECT id, index_date, index_code, index_name, 
                   current_index, previous_index, change, change_rate, 
                   source, collected_at 
            FROM ccfi_index WHERE 1=1
        """
        params = []
        
        if start_date:
            query += " AND index_date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND index_date <= ?"
            params.append(end_date)
        
        query += " ORDER BY index_date DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        data = []
        for row in rows:
            data.append({
                'id': row['id'],
                'index_date': row['index_date'],
                'index_code': row['index_code'],
                'index_name': row['index_name'],
                'current_index': row['current_index'],
                'previous_index': row['previous_index'],
                'change': row['change'],
                'change_rate': row['change_rate'],
                'source': row['source'],
                'collected_at': row['collected_at']
            })
        
        data.reverse()
        
        return jsonify({
            'success': True,
            'data': data,
            'latest': data[-1] if data else None,
            'count': len(data),
            'source': 'Shanghai Shipping Exchange (SSE)',
            'unit': 'pt',
            'index_name': 'CCFI (China Containerized Freight Index)',
            'description': 'The China Containerized Freight Index (CCFI) is compiled by the Shanghai Shipping Exchange under the supervision of China\'s Ministry of Transport. First published on April 13, 1998, it objectively reflects global container market conditions and serves as a key indicator of Chinese shipping market trends. The index uses January 1, 1998 as the base (1000). It covers 11 major routes from Chinese ports, with freight information from 16 shipping companies, published every Friday.'
        })
        
    except Exception as e:
        logger.error(f"Error fetching CCFI index: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e), 'data': []}), 500


@shipping_bp.route('/ccfi/stats', methods=['GET'])
def get_ccfi_stats():
    """CCFI 통계 정보"""
    try:
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as cnt FROM ccfi_index")
        total = cursor.fetchone()['cnt']
        
        cursor.execute("SELECT MIN(index_date) as min_date, MAX(index_date) as max_date FROM ccfi_index")
        date_range = cursor.fetchone()
        
        cursor.execute("SELECT * FROM ccfi_index ORDER BY index_date DESC LIMIT 1")
        latest_row = cursor.fetchone()
        
        cursor.execute("SELECT current_index FROM ccfi_index ORDER BY index_date DESC LIMIT 4")
        recent_rows = cursor.fetchall()
        
        conn.close()
        
        stats = {
            'total_records': total,
            'date_range': {
                'start': date_range['min_date'],
                'end': date_range['max_date']
            }
        }
        
        if latest_row:
            stats['latest'] = {
                'index_date': latest_row['index_date'],
                'current_index': latest_row['current_index'],
                'change': latest_row['change'],
                'change_rate': latest_row['change_rate']
            }
        
        if recent_rows:
            avg_4w = sum(r['current_index'] for r in recent_rows) / len(recent_rows)
            stats['average_4w'] = round(avg_4w, 2)
        
        return jsonify({
            'success': True,
            'stats': stats,
            'source': 'Shanghai Shipping Exchange (SSE)',
            'unit': 'pt'
        })
        
    except Exception as e:
        logger.error(f"Error fetching CCFI stats: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@shipping_bp.route('/ccfi/chart-data', methods=['GET'])
def get_ccfi_chart_data():
    """CCFI 차트 데이터"""
    try:
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        period = request.args.get('period', '6M')
        
        end_date = date.today()
        if period == '1W':
            start_date = end_date - timedelta(days=7)
        elif period == '1M':
            start_date = end_date - timedelta(days=30)
        elif period == '3M':
            start_date = end_date - timedelta(days=90)
        elif period == '6M':
            start_date = end_date - timedelta(days=180)
        elif period == '1Y':
            start_date = end_date - timedelta(days=365)
        elif period == 'ALL' or period == 'MAX':
            start_date = date(2000, 1, 1)
        else:
            start_date = end_date - timedelta(days=180)
        
        cursor.execute("""
            SELECT index_date, current_index, previous_index, change, change_rate
            FROM ccfi_index 
            WHERE index_date >= ? AND index_date <= ?
            ORDER BY index_date ASC
        """, (start_date.isoformat(), end_date.isoformat()))
        
        rows = cursor.fetchall()
        conn.close()
        
        data = []
        for row in rows:
            data.append({
                'index_date': row['index_date'],
                'current_index': row['current_index'],
                'previous_index': row['previous_index'],
                'change': row['change'],
                'change_rate': row['change_rate']
            })
        
        if data:
            values = [d['current_index'] for d in data]
            stats = {
                'high': max(values),
                'low': min(values),
                'average': round(sum(values) / len(values), 2),
                'start_value': values[0],
                'end_value': values[-1],
                'change': round(values[-1] - values[0], 2),
                'change_rate': round((values[-1] - values[0]) / values[0] * 100, 2) if values[0] else 0
            }
        else:
            stats = {}
        
        return jsonify({
            'success': True,
            'period': period,
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'labels': [d['index_date'] for d in data],
            'values': [d['current_index'] for d in data],
            'data': data,
            'stats': stats,
            'source': 'Shanghai Shipping Exchange (SSE)',
            'unit': 'pt',
            'index_name': 'CCFI (China Containerized Freight Index)',
            'description': 'The China Containerized Freight Index (CCFI) is compiled by the Shanghai Shipping Exchange under the supervision of China\'s Ministry of Transport. First published on April 13, 1998, it objectively reflects global container market conditions and serves as a key indicator of Chinese shipping market trends. The index uses January 1, 1998 as the base (1000). It covers 11 major routes from Chinese ports, with freight information from 16 shipping companies, published every Friday.'
        })
        
    except Exception as e:
        logger.error(f"Error fetching CCFI chart data: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


# =============================================================================
# BDI API Endpoints
# =============================================================================

@shipping_bp.route('/bdi', methods=['GET'])
def get_bdi_index():
    """BDI 지수 조회"""
    try:
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', 500, type=int)
        
        query = """
            SELECT id, index_date, index_code, index_name, 
                   current_index, previous_index, change, change_rate, 
                   source, collected_at 
            FROM bdi_index WHERE 1=1
        """
        params = []
        
        if start_date:
            query += " AND index_date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND index_date <= ?"
            params.append(end_date)
        
        query += " ORDER BY index_date DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        data = []
        for row in rows:
            data.append({
                'id': row['id'],
                'index_date': row['index_date'],
                'index_code': row['index_code'],
                'index_name': row['index_name'],
                'current_index': row['current_index'],
                'previous_index': row['previous_index'],
                'change': row['change'],
                'change_rate': row['change_rate'],
                'source': row['source'],
                'collected_at': row['collected_at']
            })
        
        data.reverse()
        
        return jsonify({
            'success': True,
            'data': data,
            'latest': data[-1] if data else None,
            'count': len(data),
            'source': 'Baltic Exchange',
            'unit': 'pt',
            'index_name': 'BDI (Baltic Dry Index)',
            'description': 'The Baltic Dry Index (BDI) has been used by the Baltic Exchange since November 1, 1999, replacing the BFI (Baltic Freight Index) which tracked dry cargo freight rates since 1985. Using January 4, 1985 as the base (1000), it is a composite index of time charter rates by vessel type: Baltic Capesize Index (BCI), Baltic Panamax Index (BPI), Baltic Supramax Index (BSI), and Baltic Handysize Index (BHSI). The BDI is calculated by averaging these four indices with equal weights and multiplying by the BDI factor.'
        })
        
    except Exception as e:
        logger.error(f"Error fetching BDI index: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e), 'data': []}), 500


@shipping_bp.route('/bdi/stats', methods=['GET'])
def get_bdi_stats():
    """BDI 통계 정보"""
    try:
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as cnt FROM bdi_index")
        total = cursor.fetchone()['cnt']
        
        cursor.execute("SELECT MIN(index_date) as min_date, MAX(index_date) as max_date FROM bdi_index")
        date_range = cursor.fetchone()
        
        cursor.execute("SELECT * FROM bdi_index ORDER BY index_date DESC LIMIT 1")
        latest_row = cursor.fetchone()
        
        cursor.execute("SELECT current_index FROM bdi_index ORDER BY index_date DESC LIMIT 4")
        recent_rows = cursor.fetchall()
        
        conn.close()
        
        stats = {
            'total_records': total,
            'date_range': {
                'start': date_range['min_date'],
                'end': date_range['max_date']
            }
        }
        
        if latest_row:
            stats['latest'] = {
                'index_date': latest_row['index_date'],
                'current_index': latest_row['current_index'],
                'change': latest_row['change'],
                'change_rate': latest_row['change_rate']
            }
        
        if recent_rows:
            avg_4w = sum(r['current_index'] for r in recent_rows) / len(recent_rows)
            stats['average_4w'] = round(avg_4w, 2)
        
        return jsonify({
            'success': True,
            'stats': stats,
            'source': 'Baltic Exchange',
            'unit': 'pt'
        })
        
    except Exception as e:
        logger.error(f"Error fetching BDI stats: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@shipping_bp.route('/bdi/chart-data', methods=['GET'])
def get_bdi_chart_data():
    """BDI 차트 데이터"""
    try:
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        period = request.args.get('period', '6M')
        
        end_date = date.today()
        if period == '1W':
            start_date = end_date - timedelta(days=7)
        elif period == '1M':
            start_date = end_date - timedelta(days=30)
        elif period == '3M':
            start_date = end_date - timedelta(days=90)
        elif period == '6M':
            start_date = end_date - timedelta(days=180)
        elif period == '1Y':
            start_date = end_date - timedelta(days=365)
        elif period == 'ALL' or period == 'MAX':
            start_date = date(2000, 1, 1)
        else:
            start_date = end_date - timedelta(days=180)
        
        cursor.execute("""
            SELECT index_date, current_index, previous_index, change, change_rate
            FROM bdi_index 
            WHERE index_date >= ? AND index_date <= ?
            ORDER BY index_date ASC
        """, (start_date.isoformat(), end_date.isoformat()))
        
        rows = cursor.fetchall()
        conn.close()
        
        data = []
        for row in rows:
            data.append({
                'index_date': row['index_date'],
                'current_index': row['current_index'],
                'previous_index': row['previous_index'],
                'change': row['change'],
                'change_rate': row['change_rate']
            })
        
        if data:
            values = [d['current_index'] for d in data]
            stats = {
                'high': max(values),
                'low': min(values),
                'average': round(sum(values) / len(values), 2),
                'start_value': values[0],
                'end_value': values[-1],
                'change': round(values[-1] - values[0], 2),
                'change_rate': round((values[-1] - values[0]) / values[0] * 100, 2) if values[0] else 0
            }
        else:
            stats = {}
        
        return jsonify({
            'success': True,
            'period': period,
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'labels': [d['index_date'] for d in data],
            'values': [d['current_index'] for d in data],
            'data': data,
            'stats': stats,
            'source': 'Baltic Exchange',
            'unit': 'pt',
            'index_name': 'BDI (Baltic Dry Index)',
            'description': 'The Baltic Dry Index (BDI) has been used by the Baltic Exchange since November 1, 1999, replacing the BFI (Baltic Freight Index) which tracked dry cargo freight rates since 1985. Using January 4, 1985 as the base (1000), it is a composite index of time charter rates by vessel type: Baltic Capesize Index (BCI), Baltic Panamax Index (BPI), Baltic Supramax Index (BSI), and Baltic Handysize Index (BHSI). The BDI is calculated by averaging these four indices with equal weights and multiplying by the BDI factor.'
        })
        
    except Exception as e:
        logger.error(f"Error fetching BDI chart data: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


# =============================================================================
# Combined Endpoints
# =============================================================================

@shipping_bp.route('/all', methods=['GET'])
def get_all_indices():
    """모든 지수의 최신 데이터 조회"""
    try:
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        result = {}
        
        # SCFI
        cursor.execute("SELECT * FROM scfi_index ORDER BY index_date DESC LIMIT 1")
        scfi = cursor.fetchone()
        if scfi:
            result['scfi'] = {
                'index_code': 'SCFI',
                'index_name': 'Shanghai Containerized Freight Index',
                'current_index': scfi['current_index'],
                'change': scfi['change'],
                'change_rate': scfi['change_rate'],
                'index_date': scfi['index_date'],
                'source': 'Shanghai Shipping Exchange (SSE)',
                'unit': 'pt'
            }
        
        # CCFI
        cursor.execute("SELECT * FROM ccfi_index ORDER BY index_date DESC LIMIT 1")
        ccfi = cursor.fetchone()
        if ccfi:
            result['ccfi'] = {
                'index_code': 'CCFI',
                'index_name': 'China Containerized Freight Index',
                'current_index': ccfi['current_index'],
                'change': ccfi['change'],
                'change_rate': ccfi['change_rate'],
                'index_date': ccfi['index_date'],
                'source': 'Shanghai Shipping Exchange (SSE)',
                'unit': 'pt'
            }
        
        # BDI
        cursor.execute("SELECT * FROM bdi_index ORDER BY index_date DESC LIMIT 1")
        bdi = cursor.fetchone()
        if bdi:
            result['bdi'] = {
                'index_code': 'BDI',
                'index_name': 'Baltic Dry Index',
                'current_index': bdi['current_index'],
                'change': bdi['change'],
                'change_rate': bdi['change_rate'],
                'index_date': bdi['index_date'],
                'source': 'Baltic Exchange',
                'unit': 'pt'
            }
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Error fetching all indices: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@shipping_bp.route('/compare', methods=['GET'])
def compare_indices():
    """여러 지수 비교 (차트용)"""
    try:
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        indices = request.args.get('indices', 'scfi,ccfi,bdi').lower().split(',')
        period = request.args.get('period', '6M')
        
        end_date = date.today()
        if period == '1W':
            start_date = end_date - timedelta(days=7)
        elif period == '1M':
            start_date = end_date - timedelta(days=30)
        elif period == '3M':
            start_date = end_date - timedelta(days=90)
        elif period == '6M':
            start_date = end_date - timedelta(days=180)
        elif period == '1Y':
            start_date = end_date - timedelta(days=365)
        elif period == 'ALL' or period == 'MAX':
            start_date = date(2000, 1, 1)
        else:
            start_date = end_date - timedelta(days=180)
        
        result = {}
        
        index_info = {
            'scfi': {'table': 'scfi_index', 'name': 'SCFI', 'color': '#3B82F6'},
            'ccfi': {'table': 'ccfi_index', 'name': 'CCFI', 'color': '#10B981'},
            'bdi': {'table': 'bdi_index', 'name': 'BDI', 'color': '#F59E0B'}
        }
        
        for idx in indices:
            if idx in index_info:
                info = index_info[idx]
                cursor.execute(f"""
                    SELECT index_date, current_index
                    FROM {info['table']}
                    WHERE index_date >= ? AND index_date <= ?
                    ORDER BY index_date ASC
                """, (start_date.isoformat(), end_date.isoformat()))
                
                rows = cursor.fetchall()
                
                if rows:
                    start_val = rows[0]['current_index']
                    data = []
                    for row in rows:
                        pct_change = ((row['current_index'] - start_val) / start_val * 100) if start_val else 0
                        data.append({
                            'index_date': row['index_date'],
                            'current_index': row['current_index'],
                            'pct_change': round(pct_change, 2)
                        })
                    
                    result[idx] = {
                        'name': info['name'],
                        'color': info['color'],
                        'labels': [d['index_date'] for d in data],
                        'values': [d['current_index'] for d in data],
                        'pct_changes': [d['pct_change'] for d in data],
                        'data': data
                    }
        
        conn.close()
        
        return jsonify({
            'success': True,
            'period': period,
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'indices': result
        })
        
    except Exception as e:
        logger.error(f"Error comparing indices: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@shipping_bp.route('/import', methods=['POST'])
def import_data():
    """데이터 임포트 (관리자용)"""
    try:
        from .import_excel import import_all
        
        results = import_all()
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error importing data: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

