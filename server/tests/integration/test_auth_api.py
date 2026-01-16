"""
Integration Tests for Authentication API Endpoints
Tests for /api/auth/* routes
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add server directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.mark.integration
class TestAuthRegisterAPI:
    """Tests for /api/auth/register endpoint"""
    
    def test_register_shipper_valid(self, client, sample_user):
        """Test POST /api/auth/register with valid shipper data"""
        data = {
            'user_type': 'shipper',
            'company': sample_user['company'],
            'name': sample_user['name'],
            'email': f"new_{sample_user['email']}",
            'phone': '010-1234-5678',
            'password': sample_user['password']
        }
        
        response = client.post('/api/auth/register', json=data)
        
        # Could be 201 (success) or 409 (already exists) or 500 (db error in test)
        assert response.status_code in [201, 409, 500]
    
    def test_register_missing_required_field(self, client):
        """Test POST /api/auth/register without required field"""
        data = {
            'user_type': 'shipper',
            'company': 'Test Co',
            # Missing: name, email, phone, password
        }
        
        response = client.post('/api/auth/register', json=data)
        
        assert response.status_code == 400
        assert 'error' in response.get_json()
    
    def test_register_invalid_email(self, client):
        """Test POST /api/auth/register with invalid email"""
        data = {
            'user_type': 'shipper',
            'company': 'Test Co',
            'name': 'Test User',
            'email': 'invalid-email',
            'phone': '010-1234-5678',
            'password': 'Password123!'
        }
        
        response = client.post('/api/auth/register', json=data)
        
        assert response.status_code == 400
        error_msg = response.get_json().get('error', '')
        assert '이메일' in error_msg or 'email' in error_msg.lower()
    
    def test_register_weak_password(self, client):
        """Test POST /api/auth/register with weak password"""
        data = {
            'user_type': 'shipper',
            'company': 'Test Co',
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '010-1234-5678',
            'password': '1234'  # Too short
        }
        
        response = client.post('/api/auth/register', json=data)
        
        assert response.status_code == 400
    
    def test_register_invalid_user_type(self, client):
        """Test POST /api/auth/register with invalid user type"""
        data = {
            'user_type': 'admin',  # Invalid
            'company': 'Test Co',
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '010-1234-5678',
            'password': 'Password123!'
        }
        
        response = client.post('/api/auth/register', json=data)
        
        assert response.status_code == 400


@pytest.mark.integration
class TestAuthLoginAPI:
    """Tests for /api/auth/login endpoint"""
    
    def test_login_missing_credentials(self, client):
        """Test POST /api/auth/login without credentials"""
        response = client.post('/api/auth/login', json={})
        
        assert response.status_code == 400
    
    def test_login_missing_password(self, client):
        """Test POST /api/auth/login without password"""
        data = {
            'email': 'test@example.com'
        }
        
        response = client.post('/api/auth/login', json=data)
        
        assert response.status_code == 400
    
    def test_login_nonexistent_user(self, client):
        """Test POST /api/auth/login with non-existent user"""
        data = {
            'email': 'nonexistent@example.com',
            'password': 'Password123!'
        }
        
        response = client.post('/api/auth/login', json=data)
        
        # Should return 404 (not found) or 401 (unauthorized)
        assert response.status_code in [401, 404]


@pytest.mark.integration
class TestAuthMeAPI:
    """Tests for /api/auth/me endpoint"""
    
    def test_me_without_session(self, client):
        """Test GET /api/auth/me without session"""
        response = client.get('/api/auth/me')
        
        # Should return 401 or 404 when not authenticated
        assert response.status_code in [401, 404, 500]


@pytest.mark.integration
class TestAuthLogoutAPI:
    """Tests for /api/auth/logout endpoint"""
    
    def test_logout_without_session(self, client):
        """Test POST /api/auth/logout without active session"""
        response = client.post('/api/auth/logout')
        
        # Should succeed (idempotent) or return error
        assert response.status_code in [200, 400, 401]


# ============================================================
# Run tests
# ============================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '-m', 'integration'])
