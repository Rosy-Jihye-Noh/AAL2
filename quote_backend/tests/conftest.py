"""
Pytest Configuration and Fixtures for Quote Backend Tests
"""
import pytest
import sys
import os
from pathlib import Path

# Add quote_backend directory to path
quote_backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(quote_backend_dir))

# Set test environment
os.environ['TESTING'] = 'true'


@pytest.fixture(scope='session')
def anyio_backend():
    """Configure async backend for pytest-asyncio."""
    return 'asyncio'


@pytest.fixture(scope='session')
def test_db_url():
    """Use in-memory SQLite for testing."""
    return 'sqlite:///./test_quote.db'


@pytest.fixture(scope='function')
async def async_client():
    """Create async test client for FastAPI."""
    from httpx import AsyncClient, ASGITransport
    from main import app
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture(scope='function')
def sync_client():
    """Create sync test client for FastAPI."""
    from fastapi.testclient import TestClient
    from main import app
    
    return TestClient(app)


@pytest.fixture
def sample_quote_request():
    """Sample quote request data."""
    return {
        'trade_mode': 'export',
        'shipping_type': 'ocean',
        'load_type': 'FCL',
        'pol': 'KRPUS',
        'pod': 'USLAX',
        'etd': '2024-02-01',
        'container_type': '40HC',
        'container_qty': 2,
        'customer_company': 'Test Shipper Co.',
        'customer_name': 'John Doe',
        'customer_email': 'john@example.com'
    }


@pytest.fixture
def sample_bid_data():
    """Sample bid data for forwarder."""
    return {
        'bidding_no': 'BID-2024-0001',
        'forwarder_id': 1,
        'ocean_freight': 1500.00,
        'thc_origin': 150.00,
        'thc_dest': 180.00,
        'doc_fee': 50.00,
        'total_amount': 1880.00,
        'currency': 'USD',
        'validity_days': 14,
        'transit_days': 21,
        'remark': 'Best rate for this route'
    }


@pytest.fixture
def sample_port_data():
    """Sample port data."""
    return [
        {'code': 'KRPUS', 'name': 'Busan Port', 'country': 'South Korea', 'port_type': 'ocean'},
        {'code': 'USLAX', 'name': 'Los Angeles', 'country': 'United States', 'port_type': 'ocean'},
        {'code': 'NLRTM', 'name': 'Rotterdam', 'country': 'Netherlands', 'port_type': 'ocean'},
        {'code': 'CNSHA', 'name': 'Shanghai', 'country': 'China', 'port_type': 'ocean'},
    ]


@pytest.fixture
def sample_container_types():
    """Sample container type data."""
    return [
        {'code': '20DC', 'name': '20 Dry Container', 'max_weight_kg': 21770, 'max_cbm': 33.0},
        {'code': '40DC', 'name': '40 Dry Container', 'max_weight_kg': 26680, 'max_cbm': 67.0},
        {'code': '40HC', 'name': '40 High Cube', 'max_weight_kg': 26460, 'max_cbm': 76.0},
    ]


# ============================================================
# Database Fixtures
# ============================================================

@pytest.fixture(scope='function')
def test_db_session():
    """Create test database session."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from database import Base
    
    # Use in-memory SQLite
    engine = create_engine('sqlite:///:memory:', echo=False)
    Base.metadata.create_all(bind=engine)
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(bind=engine)


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
    config.addinivalue_line(
        "markers", "asyncio: marks tests as async tests"
    )
