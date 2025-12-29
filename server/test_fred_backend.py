"""
FRED 백엔드 모듈 단위 테스트
"""

import unittest
from unittest.mock import patch, Mock
import fred_backend
from datetime import datetime


class TestFredBackend(unittest.TestCase):
    """FRED 백엔드 테스트 클래스"""
    
    def setUp(self):
        """테스트 전 설정"""
        # 캐시 초기화
        fred_backend._cache = {
            "data": None,
            "expires_at": None
        }
    
    @patch('fred_backend.requests.get')
    @patch('fred_backend.FRED_API_KEY', 'test_api_key')
    def test_get_latest_observation_success(self, mock_get):
        """get_latest_observation 성공 케이스"""
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.json.return_value = {
            'observations': [
                {
                    'date': '2025-01-20',
                    'value': '5.33'
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = fred_backend.get_latest_observation('DFF')
        
        self.assertNotIn('error', result)
        self.assertEqual(result['date'], '2025-01-20')
        self.assertEqual(result['value'], 5.33)
        self.assertEqual(result['series_id'], 'DFF')
    
    @patch('fred_backend.requests.get')
    @patch('fred_backend.FRED_API_KEY', 'test_api_key')
    def test_get_latest_observation_dot_value(self, mock_get):
        """get_latest_observation에서 "." 값 처리"""
        # Mock 응답 설정 (값이 "."인 경우)
        mock_response = Mock()
        mock_response.json.return_value = {
            'observations': [
                {
                    'date': '2025-01-20',
                    'value': '.'
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = fred_backend.get_latest_observation('DFF')
        
        self.assertNotIn('error', result)
        self.assertEqual(result['date'], '2025-01-20')
        self.assertIsNone(result['value'])
    
    @patch('fred_backend.requests.get')
    @patch('fred_backend.FRED_API_KEY', 'test_api_key')
    def test_get_latest_observation_empty_value(self, mock_get):
        """get_latest_observation에서 빈 값 처리"""
        # Mock 응답 설정 (값이 빈 문자열인 경우)
        mock_response = Mock()
        mock_response.json.return_value = {
            'observations': [
                {
                    'date': '2025-01-20',
                    'value': ''
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = fred_backend.get_latest_observation('DFF')
        
        self.assertNotIn('error', result)
        self.assertEqual(result['date'], '2025-01-20')
        self.assertIsNone(result['value'])
    
    @patch('fred_backend.requests.get')
    @patch('fred_backend.FRED_API_KEY', 'test_api_key')
    def test_get_latest_observation_no_observations(self, mock_get):
        """get_latest_observation에서 관측값이 없는 경우"""
        # Mock 응답 설정 (observations가 빈 배열)
        mock_response = Mock()
        mock_response.json.return_value = {
            'observations': []
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = fred_backend.get_latest_observation('DFF')
        
        self.assertIn('error', result)
        self.assertIsNone(result.get('value'))
    
    @patch('fred_backend.requests.get')
    @patch('fred_backend.FRED_API_KEY', 'test_api_key')
    def test_get_latest_observation_rate_limit(self, mock_get):
        """get_latest_observation에서 429 Rate Limit 에러 처리"""
        # Mock 응답 설정 (429 에러)
        mock_response = Mock()
        mock_response.status_code = 429
        mock_get.side_effect = fred_backend.requests.exceptions.HTTPError(response=mock_response)
        
        result = fred_backend.get_latest_observation('DFF')
        
        self.assertIn('error', result)
        self.assertIn('rate limit', result['error'].lower())
        self.assertEqual(result.get('status_code'), 429)
    
    @patch('fred_backend.get_latest_observation')
    def test_get_us_rates_success(self, mock_get_obs):
        """get_us_rates 성공 케이스"""
        # Mock get_latest_observation 응답
        def side_effect(series_id):
            if series_id == 'DFF':
                return {
                    'date': '2025-01-20',
                    'value': 5.33,
                    'series_id': 'DFF'
                }
            elif series_id == 'DFEDTARU':
                return {
                    'date': '2025-01-20',
                    'value': 5.50,
                    'series_id': 'DFEDTARU'
                }
        
        mock_get_obs.side_effect = side_effect
        
        result = fred_backend.get_us_rates()
        
        self.assertNotIn('error', result)
        self.assertEqual(result['source'], 'FRED')
        self.assertEqual(result['asOf'], '2025-01-20')
        self.assertEqual(result['effective']['ratePct'], 5.33)
        self.assertEqual(result['targetUpper']['ratePct'], 5.50)
    
    @patch('fred_backend.get_latest_observation')
    def test_get_us_rates_with_stale_cache(self, mock_get_obs):
        """get_us_rates에서 API 실패 시 stale 캐시 반환"""
        # 캐시에 데이터 설정
        cached_data = {
            "source": "FRED",
            "asOf": "2025-01-19",
            "effective": {
                "seriesId": "DFF",
                "date": "2025-01-19",
                "ratePct": 5.25
            },
            "targetUpper": {
                "seriesId": "DFEDTARU",
                "date": "2025-01-19",
                "ratePct": 5.50
            }
        }
        fred_backend._cache["data"] = cached_data
        
        # API 호출 실패 시뮬레이션
        mock_get_obs.return_value = {"error": "API request failed"}
        
        result = fred_backend.get_us_rates()
        
        # stale 캐시가 반환되어야 함
        self.assertIn('warning', result)
        self.assertEqual(result['effective']['ratePct'], 5.25)
    
    @patch('fred_backend.get_latest_observation')
    def test_get_us_rates_cache_hit(self, mock_get_obs):
        """get_us_rates 캐시 히트 테스트"""
        # 캐시에 유효한 데이터 설정
        cached_data = {
            "source": "FRED",
            "asOf": "2025-01-20",
            "effective": {"seriesId": "DFF", "date": "2025-01-20", "ratePct": 5.33},
            "targetUpper": {"seriesId": "DFEDTARU", "date": "2025-01-20", "ratePct": 5.50}
        }
        from datetime import timedelta
        fred_backend._cache["data"] = cached_data
        fred_backend._cache["expires_at"] = datetime.now() + timedelta(seconds=3600)
        
        result = fred_backend.get_us_rates()
        
        # 캐시에서 반환되어야 함 (API 호출 없음)
        self.assertNotIn('error', result)
        self.assertEqual(result['effective']['ratePct'], 5.33)
        # get_latest_observation이 호출되지 않아야 함
        mock_get_obs.assert_not_called()
    
    @patch('fred_backend.FRED_API_KEY', None)
    def test_get_latest_observation_no_api_key(self):
        """API 키가 없을 때 에러 반환"""
        result = fred_backend.get_latest_observation('DFF')
        
        self.assertIn('error', result)
        self.assertIn('FRED_API_KEY', result['error'])


if __name__ == '__main__':
    # 실제 API 키가 있을 때만 통합 테스트 실행
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    has_api_key = bool(os.getenv('FRED_API_KEY'))
    
    if not has_api_key:
        print("⚠️  FRED_API_KEY not set. Skipping integration tests.")
        print("   Running unit tests only...")
    
    unittest.main()
