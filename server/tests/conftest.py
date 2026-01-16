"""
Pytest Configuration and Fixtures for Server Tests
"""
import pytest
import sys
import os
from pathlib import Path

# Add server directory to path
server_dir = Path(__file__).parent.parent
sys.path.insert(0, str(server_dir))

# Set test environment
os.environ['TESTING'] = 'true'
os.environ['FLASK_ENV'] = 'testing'


@pytest.fixture(scope='session')
def app():
    """Create Flask application for testing."""
    from main import app as flask_app
    
    flask_app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
    })
    
    yield flask_app


@pytest.fixture(scope='function')
def client(app):
    """Create test client for Flask application."""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """Create test CLI runner for Flask application."""
    return app.test_cli_runner()


@pytest.fixture(scope='session')
def auth_db():
    """Create in-memory auth database for testing."""
    import sqlite3
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT,
            company TEXT,
            role TEXT DEFAULT 'shipper',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    yield conn
    conn.close()


@pytest.fixture
def sample_user():
    """Sample user data for testing."""
    return {
        'email': 'test@example.com',
        'password': 'TestPassword123!',
        'name': 'Test User',
        'company': 'Test Company',
        'role': 'shipper'
    }


@pytest.fixture
def sample_market_params():
    """Sample market API parameters."""
    return {
        'type': 'exchange_rate',
        'start_date': '20240101',
        'end_date': '20240131'
    }


@pytest.fixture
def mock_bok_response():
    """Mock response from BOK API."""
    return {
        'StatisticSearch': {
            'list_total_count': 10,
            'row': [
                {
                    'TIME': '20240101',
                    'DATA_VALUE': '1320.50',
                    'STAT_NAME': '환율',
                    'ITEM_NAME1': 'USD'
                },
                {
                    'TIME': '20240102',
                    'DATA_VALUE': '1318.20',
                    'STAT_NAME': '환율',
                    'ITEM_NAME1': 'USD'
                }
            ]
        }
    }


@pytest.fixture
def mock_kcci_data():
    """Mock KCCI index data."""
    return {
        'success': True,
        'week_date': '2024-01-15',
        'comprehensive': {
            'current_index': 1234.56,
            'change_week': 12.34,
            'change_rate': 1.01
        },
        'routes': [
            {'route': 'Asia-Europe', 'index': 1500.0, 'change': 10.0},
            {'route': 'Asia-US West', 'index': 1200.0, 'change': -5.0}
        ]
    }


# ============================================================
# Markers
# ============================================================

def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
