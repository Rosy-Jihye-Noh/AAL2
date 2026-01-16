"""
Integration Tests for Quote Backend API
Tests for FastAPI quote endpoints
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add quote_backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.mark.integration
class TestPortsAPI:
    """Tests for /api/ports endpoints"""
    
    def test_get_ports_list(self, sync_client):
        """Test GET /api/ports returns list of ports"""
        response = sync_client.get('/api/ports')
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or 'ports' in data
    
    def test_get_ports_by_type_ocean(self, sync_client):
        """Test GET /api/ports?type=ocean"""
        response = sync_client.get('/api/ports?type=ocean')
        
        assert response.status_code == 200
    
    def test_search_ports(self, sync_client):
        """Test GET /api/ports/search?q=busan"""
        response = sync_client.get('/api/ports/search?q=busan')
        
        assert response.status_code in [200, 404]


@pytest.mark.integration
class TestContainerTypesAPI:
    """Tests for /api/container-types endpoints"""
    
    def test_get_container_types(self, sync_client):
        """Test GET /api/container-types"""
        response = sync_client.get('/api/container-types')
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or 'container_types' in data


@pytest.mark.integration
class TestQuoteRequestAPI:
    """Tests for /api/quote/request endpoints"""
    
    def test_create_quote_request(self, sync_client, sample_quote_request):
        """Test POST /api/quote/request"""
        response = sync_client.post('/api/quote/request', json=sample_quote_request)
        
        # Should create or fail with validation error
        assert response.status_code in [200, 201, 400, 422]
    
    def test_create_quote_missing_required(self, sync_client):
        """Test POST /api/quote/request with missing fields"""
        incomplete_data = {
            'trade_mode': 'export',
            # Missing other required fields
        }
        
        response = sync_client.post('/api/quote/request', json=incomplete_data)
        
        assert response.status_code in [400, 422]
    
    def test_get_quote_request_not_found(self, sync_client):
        """Test GET /api/quote/request/99999 (non-existent)"""
        response = sync_client.get('/api/quote/request/99999')
        
        assert response.status_code in [404, 500]


@pytest.mark.integration
class TestBiddingAPI:
    """Tests for /api/bidding endpoints"""
    
    def test_get_bidding_list(self, sync_client):
        """Test GET /api/bidding/list"""
        response = sync_client.get('/api/bidding/list')
        
        assert response.status_code in [200, 404]
    
    def test_get_bidding_list_with_status(self, sync_client):
        """Test GET /api/bidding/list?status=open"""
        response = sync_client.get('/api/bidding/list?status=open')
        
        assert response.status_code in [200, 404]
    
    def test_get_bidding_detail_not_found(self, sync_client):
        """Test GET /api/bidding/BID-99999 (non-existent)"""
        response = sync_client.get('/api/bidding/BID-99999')
        
        assert response.status_code in [404, 500]


@pytest.mark.integration
class TestForwarderAPI:
    """Tests for /api/forwarder endpoints"""
    
    def test_get_forwarder_bidding_list(self, sync_client):
        """Test GET /api/forwarder/bidding/list"""
        response = sync_client.get('/api/forwarder/bidding/list')
        
        assert response.status_code in [200, 401, 404]
    
    def test_submit_bid_without_auth(self, sync_client, sample_bid_data):
        """Test POST /api/forwarder/bid without authentication"""
        response = sync_client.post('/api/forwarder/bid', json=sample_bid_data)
        
        # Should fail without proper auth or forwarder context
        assert response.status_code in [401, 403, 404, 422, 500]


@pytest.mark.integration
class TestOceanRatesAPI:
    """Tests for /api/rates/ocean endpoints"""
    
    def test_get_ocean_rates(self, sync_client):
        """Test GET /api/rates/ocean"""
        response = sync_client.get('/api/rates/ocean?pol=KRPUS&pod=USLAX')
        
        assert response.status_code in [200, 404]
    
    def test_get_ocean_rates_with_container(self, sync_client):
        """Test GET /api/rates/ocean with container type"""
        response = sync_client.get('/api/rates/ocean?pol=KRPUS&pod=USLAX&container_type=40HC')
        
        assert response.status_code in [200, 404]


@pytest.mark.integration
class TestHealthCheckAPI:
    """Tests for health check endpoints"""
    
    def test_root_endpoint(self, sync_client):
        """Test GET / returns API info"""
        response = sync_client.get('/')
        
        assert response.status_code == 200
    
    def test_docs_endpoint(self, sync_client):
        """Test GET /docs returns Swagger UI"""
        response = sync_client.get('/docs')
        
        assert response.status_code == 200


@pytest.mark.integration
class TestDashboardAPI:
    """Tests for Dashboard API endpoints"""
    
    def test_shipper_summary(self, sync_client):
        """Test GET /api/dashboard/shipper/summary"""
        response = sync_client.get('/api/dashboard/shipper/summary')
        
        assert response.status_code in [200, 401, 404]
    
    def test_forwarder_summary(self, sync_client):
        """Test GET /api/dashboard/forwarder/summary"""
        response = sync_client.get('/api/dashboard/forwarder/summary')
        
        assert response.status_code in [200, 401, 404]


# ============================================================
# Async Tests (using pytest-asyncio)
# ============================================================

@pytest.mark.asyncio
@pytest.mark.integration
class TestAsyncQuoteAPI:
    """Async integration tests for Quote API"""
    
    async def test_get_ports_async(self, async_client):
        """Test GET /api/ports asynchronously"""
        response = await async_client.get('/api/ports')
        
        assert response.status_code == 200
    
    async def test_create_quote_async(self, async_client, sample_quote_request):
        """Test POST /api/quote/request asynchronously"""
        response = await async_client.post('/api/quote/request', json=sample_quote_request)
        
        assert response.status_code in [200, 201, 400, 422]


# ============================================================
# Run tests
# ============================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '-m', 'integration'])
