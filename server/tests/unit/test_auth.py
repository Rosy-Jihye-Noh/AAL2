"""
Unit Tests for Authentication Module
Tests for password hashing, validation, and utility functions
"""
import pytest
import sys
from pathlib import Path

# Add server directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestPasswordHashing:
    """Tests for password hashing functions"""
    
    def test_hash_password_returns_string(self):
        """Test hash_password returns a string"""
        from auth.auth_backend import hash_password
        
        result = hash_password("TestPassword123")
        assert isinstance(result, str)
    
    def test_hash_password_different_for_same_input(self):
        """Test hash_password produces different hashes (due to salt)"""
        from auth.auth_backend import hash_password
        
        hash1 = hash_password("TestPassword123")
        hash2 = hash_password("TestPassword123")
        
        # Same password should produce different hashes due to random salt
        assert hash1 != hash2
    
    def test_hash_password_produces_bcrypt_format(self):
        """Test hash_password produces bcrypt format hash"""
        from auth.auth_backend import hash_password
        
        result = hash_password("TestPassword123")
        
        # bcrypt hashes start with $2b$ or $2a$
        assert result.startswith('$2')
    
    def test_verify_password_correct_password(self):
        """Test verify_password returns True for correct password"""
        from auth.auth_backend import hash_password, verify_password
        
        password = "TestPassword123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_wrong_password(self):
        """Test verify_password returns False for wrong password"""
        from auth.auth_backend import hash_password, verify_password
        
        hashed = hash_password("TestPassword123")
        
        assert verify_password("WrongPassword123", hashed) is False
    
    def test_verify_password_case_sensitive(self):
        """Test verify_password is case sensitive"""
        from auth.auth_backend import hash_password, verify_password
        
        password = "TestPassword123"
        hashed = hash_password(password)
        
        assert verify_password("testpassword123", hashed) is False
        assert verify_password("TESTPASSWORD123", hashed) is False


class TestEmailValidation:
    """Tests for email validation function"""
    
    def test_valid_email_standard(self):
        """Test valid standard email format"""
        from auth.auth_backend import validate_email
        
        assert validate_email("user@example.com") is True
        assert validate_email("test.user@domain.org") is True
        assert validate_email("user123@test.co.kr") is True
    
    def test_valid_email_with_plus(self):
        """Test valid email with plus sign"""
        from auth.auth_backend import validate_email
        
        assert validate_email("user+tag@example.com") is True
    
    def test_valid_email_with_subdomain(self):
        """Test valid email with subdomain"""
        from auth.auth_backend import validate_email
        
        assert validate_email("user@mail.example.com") is True
    
    def test_invalid_email_no_at(self):
        """Test invalid email without @ symbol"""
        from auth.auth_backend import validate_email
        
        assert validate_email("userexample.com") is False
    
    def test_invalid_email_no_domain(self):
        """Test invalid email without domain"""
        from auth.auth_backend import validate_email
        
        assert validate_email("user@") is False
        assert validate_email("user@.com") is False
    
    def test_invalid_email_no_tld(self):
        """Test invalid email without TLD"""
        from auth.auth_backend import validate_email
        
        assert validate_email("user@example") is False
    
    def test_invalid_email_empty(self):
        """Test invalid empty email"""
        from auth.auth_backend import validate_email
        
        assert validate_email("") is False
    
    def test_invalid_email_spaces(self):
        """Test invalid email with spaces"""
        from auth.auth_backend import validate_email
        
        assert validate_email("user @example.com") is False
        assert validate_email(" user@example.com") is False


class TestPasswordValidation:
    """Tests for password validation function"""
    
    def test_valid_password(self):
        """Test valid password passes validation"""
        from auth.auth_backend import validate_password
        
        is_valid, message = validate_password("Password123")
        assert is_valid is True
        assert message == ""
    
    def test_valid_password_with_special_chars(self):
        """Test valid password with special characters"""
        from auth.auth_backend import validate_password
        
        is_valid, _ = validate_password("Password123!@#")
        assert is_valid is True
    
    def test_invalid_password_too_short(self):
        """Test password too short fails validation"""
        from auth.auth_backend import validate_password
        
        is_valid, message = validate_password("Pass1")
        assert is_valid is False
        assert "8자" in message or "8" in message
    
    def test_invalid_password_no_letters(self):
        """Test password without letters fails validation"""
        from auth.auth_backend import validate_password
        
        is_valid, message = validate_password("12345678")
        assert is_valid is False
        assert "영문" in message
    
    def test_invalid_password_no_numbers(self):
        """Test password without numbers fails validation"""
        from auth.auth_backend import validate_password
        
        is_valid, message = validate_password("PasswordOnly")
        assert is_valid is False
        assert "숫자" in message
    
    def test_password_exactly_8_chars(self):
        """Test password with exactly 8 characters"""
        from auth.auth_backend import validate_password
        
        is_valid, _ = validate_password("Pass1234")
        assert is_valid is True
    
    def test_password_7_chars_fails(self):
        """Test password with 7 characters fails"""
        from auth.auth_backend import validate_password
        
        is_valid, _ = validate_password("Pass123")
        assert is_valid is False


class TestUserTypeValidation:
    """Tests for user type constants"""
    
    def test_user_types_exist(self):
        """Test user type enum exists"""
        from auth.models import UserType
        
        assert hasattr(UserType, 'shipper') or 'shipper' in [e.value for e in UserType]
        assert hasattr(UserType, 'forwarder') or 'forwarder' in [e.value for e in UserType]
    
    def test_valid_user_types(self):
        """Test valid user types"""
        valid_types = ['shipper', 'forwarder']
        
        for user_type in valid_types:
            assert user_type in ['shipper', 'forwarder']


# ============================================================
# Integration-like tests (still unit tests but test more flow)
# ============================================================

class TestAuthFlow:
    """Tests for authentication flow logic"""
    
    def test_password_hash_and_verify_flow(self):
        """Test complete password hash and verify flow"""
        from auth.auth_backend import hash_password, verify_password
        
        original_password = "SecurePassword123!"
        
        # Hash the password
        hashed = hash_password(original_password)
        
        # Verify with correct password
        assert verify_password(original_password, hashed) is True
        
        # Verify with wrong password
        assert verify_password("WrongPassword123!", hashed) is False
    
    def test_multiple_users_different_hashes(self):
        """Test multiple users get different hashes for same password"""
        from auth.auth_backend import hash_password, verify_password
        
        password = "SharedPassword123"
        
        # Simulate multiple users with same password
        user1_hash = hash_password(password)
        user2_hash = hash_password(password)
        user3_hash = hash_password(password)
        
        # All hashes should be different
        assert user1_hash != user2_hash
        assert user2_hash != user3_hash
        assert user1_hash != user3_hash
        
        # But all should verify correctly
        assert verify_password(password, user1_hash)
        assert verify_password(password, user2_hash)
        assert verify_password(password, user3_hash)


# ============================================================
# Run tests
# ============================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
