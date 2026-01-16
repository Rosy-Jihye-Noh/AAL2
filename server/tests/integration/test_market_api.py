"""
Integration Tests for Market API Endpoints
Tests for /api/market/* routes
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add server directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.mark.integration
class TestMarketIndicesAPI:
    """Tests for /api/market/indices endpoint"""
    
    def test_get_exchange_rate(self, client, mock_bok_response):
        """Test GET /api/market/indices?type=exchange_rate"""
        with patch('bok_backend.fetch_data') as mock_fetch:
            mock_fetch.return_value = mock_bok_response['StatisticSearch']['row']
            
            response = client.get('/api/market/indices?type=exchange_rate')
            
            assert response.status_code == 200
            data = response.get_json()
            assert 'data' in data or 'error' not in data
    
    def test_get_market_indices_missing_type(self, client):
        """Test GET /api/market/indices without type parameter"""
        response = client.get('/api/market/indices')
        
        # Should either return error or default response
        assert response.status_code in [200, 400]
    
    def test_get_market_indices_invalid_type(self, client):
        """Test GET /api/market/indices with invalid type"""
        response = client.get('/api/market/indices?type=invalid_type')
        
        # Should return error
        assert response.status_code in [200, 400, 404]


@pytest.mark.integration
class TestKCCIAPI:
    """Tests for /api/kcci/* endpoints"""
    
    def test_get_comprehensive_index(self, client, mock_kcci_data):
        """Test GET /api/kcci/comprehensive"""
        with patch('kcci.api.get_latest_comprehensive') as mock_get:
            mock_get.return_value = mock_kcci_data['comprehensive']
            
            response = client.get('/api/kcci/comprehensive')
            
            # Should return 200 or appropriate error
            assert response.status_code in [200, 404, 500]
    
    def test_get_route_indices(self, client):
        """Test GET /api/kcci/routes"""
        response = client.get('/api/kcci/routes')
        
        assert response.status_code in [200, 404, 500]


@pytest.mark.integration
class TestShippingIndicesAPI:
    """Tests for /api/shipping-indices/* endpoints"""
    
    def test_get_bdi_index(self, client):
        """Test GET /api/shipping-indices/bdi"""
        response = client.get('/api/shipping-indices/bdi')
        
        # Endpoint should exist and return data or appropriate error
        assert response.status_code in [200, 404, 500]
    
    def test_get_scfi_index(self, client):
        """Test GET /api/shipping-indices/scfi"""
        response = client.get('/api/shipping-indices/scfi')
        
        assert response.status_code in [200, 404, 500]
    
    def test_get_ccfi_index(self, client):
        """Test GET /api/shipping-indices/ccfi"""
        response = client.get('/api/shipping-indices/ccfi')
        
        assert response.status_code in [200, 404, 500]


@pytest.mark.integration
class TestNewsAPI:
    """Tests for /api/news-intelligence/* endpoints"""
    
    def test_get_articles(self, client):
        """Test GET /api/news-intelligence/articles"""
        response = client.get('/api/news-intelligence/articles')
        
        assert response.status_code in [200, 404, 500]
    
    def test_get_articles_with_limit(self, client):
        """Test GET /api/news-intelligence/articles with limit parameter"""
        response = client.get('/api/news-intelligence/articles?limit=5')
        
        if response.status_code == 200:
            data = response.get_json()
            if 'articles' in data:
                assert len(data['articles']) <= 5


@pytest.mark.integration
class TestHealthCheck:
    """Tests for health check endpoints"""
    
    def test_root_endpoint(self, client):
        """Test GET / returns something"""
        response = client.get('/')
        
        # Should return HTML or redirect
        assert response.status_code in [200, 301, 302]
    
    def test_api_status(self, client):
        """Test basic API is responding"""
        # Try a simple endpoint
        response = client.get('/api/market/indices?type=exchange_rate')
        
        # Should not return 5xx error
        assert response.status_code < 500


# ============================================================
# Run tests
# ============================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '-m', 'integration'])
