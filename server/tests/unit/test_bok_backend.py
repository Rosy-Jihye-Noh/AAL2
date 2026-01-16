"""
Unit Tests for BOK (Bank of Korea) Backend Module
Tests for RateLimiter, APICache, and data parsing functions
"""
import pytest
import time
import threading
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add server directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestRateLimiter:
    """Tests for RateLimiter class"""
    
    def test_rate_limiter_initialization(self):
        """Test RateLimiter initializes with correct default values"""
        from bok_backend import RateLimiter, RATE_LIMIT_INTERVAL
        
        limiter = RateLimiter()
        assert limiter.min_interval == RATE_LIMIT_INTERVAL
        assert limiter.request_count == 0
        assert limiter.max_requests == 250
    
    def test_rate_limiter_custom_interval(self):
        """Test RateLimiter with custom interval"""
        from bok_backend import RateLimiter
        
        limiter = RateLimiter(min_interval=1.0)
        assert limiter.min_interval == 1.0
    
    def test_wait_if_needed_first_call_immediate(self):
        """Test first API call passes immediately"""
        from bok_backend import RateLimiter
        
        limiter = RateLimiter(min_interval=0.5)
        start = time.time()
        limiter.wait_if_needed()
        elapsed = time.time() - start
        
        # First call should be nearly instant
        assert elapsed < 0.1
    
    def test_wait_if_needed_respects_interval(self):
        """Test that consecutive calls respect the minimum interval"""
        from bok_backend import RateLimiter
        
        limiter = RateLimiter(min_interval=0.1)
        
        # First call
        limiter.wait_if_needed()
        
        # Second call should wait
        start = time.time()
        limiter.wait_if_needed()
        elapsed = time.time() - start
        
        # Should have waited at least min_interval
        assert elapsed >= 0.09  # Allow small tolerance
    
    def test_rate_limiter_thread_safety(self):
        """Test RateLimiter is thread-safe"""
        from bok_backend import RateLimiter
        
        limiter = RateLimiter(min_interval=0.05)
        call_count = 0
        lock = threading.Lock()
        
        def make_request():
            nonlocal call_count
            limiter.wait_if_needed()
            with lock:
                call_count += 1
        
        threads = [threading.Thread(target=make_request) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert call_count == 5
    
    def test_request_count_increments(self):
        """Test request count increments correctly"""
        from bok_backend import RateLimiter
        
        limiter = RateLimiter(min_interval=0.01)
        
        initial_count = limiter.request_count
        limiter.wait_if_needed()
        
        assert limiter.request_count == initial_count + 1


class TestCacheEntry:
    """Tests for CacheEntry class"""
    
    def test_cache_entry_creation(self):
        """Test CacheEntry creates with correct data"""
        from bok_backend import CacheEntry
        
        entry = CacheEntry(data={'test': 'data'}, ttl=300)
        assert entry.data == {'test': 'data'}
        assert entry.ttl == 300
    
    def test_cache_entry_not_expired_initially(self):
        """Test CacheEntry is not expired when created"""
        from bok_backend import CacheEntry
        
        entry = CacheEntry(data='test', ttl=300)
        assert not entry.is_expired()
    
    def test_cache_entry_expires_after_ttl(self):
        """Test CacheEntry expires after TTL"""
        from bok_backend import CacheEntry
        
        entry = CacheEntry(data='test', ttl=0.1)
        time.sleep(0.15)
        assert entry.is_expired()
    
    def test_cache_entry_default_ttl(self):
        """Test CacheEntry uses default TTL"""
        from bok_backend import CacheEntry, CACHE_TTL_SECONDS
        
        entry = CacheEntry(data='test')
        assert entry.ttl == CACHE_TTL_SECONDS


class TestAPICache:
    """Tests for APICache class"""
    
    def test_api_cache_initialization(self):
        """Test APICache initializes empty"""
        from bok_backend import APICache
        
        cache = APICache()
        assert len(cache.cache) == 0
    
    def test_api_cache_set_and_get(self):
        """Test setting and getting cache values"""
        from bok_backend import APICache
        
        cache = APICache()
        cache.set('test_key', {'value': 123})
        
        result = cache.get('test_key')
        assert result == {'value': 123}
    
    def test_api_cache_returns_none_for_missing_key(self):
        """Test cache returns None for missing keys"""
        from bok_backend import APICache
        
        cache = APICache()
        result = cache.get('nonexistent_key')
        assert result is None
    
    def test_api_cache_returns_none_for_expired_entry(self):
        """Test cache returns None for expired entries"""
        from bok_backend import APICache
        
        cache = APICache()
        cache.set('test_key', 'test_value', ttl=0.1)
        
        time.sleep(0.15)
        
        result = cache.get('test_key')
        assert result is None
    
    def test_api_cache_clears_expired_entries(self):
        """Test cache clears expired entries"""
        from bok_backend import APICache
        
        cache = APICache()
        cache.set('key1', 'value1', ttl=0.1)
        cache.set('key2', 'value2', ttl=300)
        
        time.sleep(0.15)
        cache.clear_expired()
        
        assert cache.get('key1') is None
        assert cache.get('key2') == 'value2'
    
    def test_api_cache_thread_safety(self):
        """Test APICache is thread-safe"""
        from bok_backend import APICache
        
        cache = APICache()
        
        def set_values(start):
            for i in range(10):
                cache.set(f'key_{start}_{i}', f'value_{start}_{i}')
        
        threads = [threading.Thread(target=set_values, args=(i,)) for i in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All values should be accessible
        assert cache.get('key_0_5') == 'value_0_5'
        assert cache.get('key_2_9') == 'value_2_9'


class TestBOKDataParsing:
    """Tests for BOK API data parsing functions"""
    
    def test_parse_bok_response_valid_data(self):
        """Test parsing valid BOK API response"""
        from bok_backend import parse_bok_response
        
        mock_response = {
            'StatisticSearch': {
                'list_total_count': 2,
                'row': [
                    {'TIME': '20240101', 'DATA_VALUE': '1320.50'},
                    {'TIME': '20240102', 'DATA_VALUE': '1318.20'}
                ]
            }
        }
        
        result = parse_bok_response(mock_response)
        
        assert result is not None
        assert len(result) == 2
        assert result[0]['TIME'] == '20240101'
    
    def test_parse_bok_response_empty_data(self):
        """Test parsing empty BOK API response"""
        from bok_backend import parse_bok_response
        
        mock_response = {
            'StatisticSearch': {
                'list_total_count': 0,
                'row': []
            }
        }
        
        result = parse_bok_response(mock_response)
        
        assert result is not None
        assert len(result) == 0
    
    def test_parse_bok_response_error_response(self):
        """Test parsing BOK API error response"""
        from bok_backend import parse_bok_response
        
        mock_response = {
            'RESULT': {
                'CODE': 'ERROR',
                'MESSAGE': 'Invalid request'
            }
        }
        
        result = parse_bok_response(mock_response)
        
        assert result is None or len(result) == 0


class TestBOKMapping:
    """Tests for BOK_MAPPING configuration"""
    
    def test_bok_mapping_exists(self):
        """Test BOK_MAPPING is defined"""
        from bok_backend import BOK_MAPPING
        
        assert BOK_MAPPING is not None
        assert isinstance(BOK_MAPPING, dict)
    
    def test_bok_mapping_has_exchange_rate(self):
        """Test BOK_MAPPING includes exchange rate"""
        from bok_backend import BOK_MAPPING
        
        assert 'exchange_rate' in BOK_MAPPING
    
    def test_bok_mapping_structure(self):
        """Test BOK_MAPPING entries have required fields"""
        from bok_backend import BOK_MAPPING
        
        for key, value in BOK_MAPPING.items():
            assert 'stat_code' in value or 'items' in value


# ============================================================
# Decorator Tests
# ============================================================

class TestCacheDecorator:
    """Tests for cache decorator if implemented"""
    
    @pytest.mark.skip(reason="Decorator may not be implemented")
    def test_cached_function_returns_cached_value(self):
        """Test cached decorator returns cached values"""
        pass


# ============================================================
# Run tests
# ============================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
