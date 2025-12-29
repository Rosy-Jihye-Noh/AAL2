# ECOS API StatisticalCodeSearch 가이드

## 개요

StatisticalCodeSearch API는 한국은행 ECOS API에서 제공하는 통계표 코드 검색 기능입니다.
이 API를 통해 사용 가능한 모든 통계표 코드를 검색하고 조회할 수 있습니다.

**참고 문서**: https://ecos.bok.or.kr/api/#/DevGuide/StatisticalCodeSearch

## API 엔드포인트

```
GET /StatisticalCodeSearch/{KEY}/{언어}/{요청시작건수}/{요청종료건수}/{통계표코드}/{통계표명}
```

### 파라미터

| 파라미터 | 설명 | 필수 | 예시 |
|---------|------|------|------|
| KEY | ECOS API 인증 키 | 필수 | QC05D99HP8DZ9W23YBNI |
| 언어 | 응답 언어 (kr: 한국어, en: 영어) | 필수 | kr |
| 요청시작건수 | 페이징 시작 번호 | 필수 | 1 |
| 요청종료건수 | 페이징 종료 번호 | 필수 | 100 |
| 통계표코드 | 검색할 통계표 코드 (부분 검색 가능) | 선택 | 901Y |
| 통계표명 | 검색할 통계표명 (부분 검색 가능) | 선택 | 소비자물가지수 |

### URL 예시

```bash
# 전체 통계표 목록 조회
http://ecos.bok.or.kr/api/StatisticalCodeSearch/{KEY}/json/kr/1/100//

# 통계표 코드로 검색 (901Y로 시작하는 코드)
http://ecos.bok.or.kr/api/StatisticalCodeSearch/{KEY}/json/kr/1/100/901Y/

# 통계표명으로 검색
http://ecos.bok.or.kr/api/StatisticalCodeSearch/{KEY}/json/kr/1/100//소비자물가지수

# 통계표 코드와 이름으로 검색
http://ecos.bok.or.kr/api/StatisticalCodeSearch/{KEY}/json/kr/1/100/901Y/소비자물가지수
```

## 응답 형식

### 성공 응답 (JSON)

```json
{
  "StatisticalCodeSearch": {
    "list_total_count": 10,
    "row": [
      {
        "STAT_CODE": "901Y001",
        "STAT_NAME": "소비자물가지수",
        "CYCLE": "M",
        "SRCH_CNT": 1,
        "ORG_NAME": "한국은행"
      },
      {
        "STAT_CODE": "901Y009",
        "STAT_NAME": "4.2.1. 소비자물가지수",
        "CYCLE": "H",
        "SRCH_CNT": 1,
        "ORG_NAME": "한국은행"
      }
    ]
  }
}
```

### 응답 필드 설명

| 필드명 | 설명 | 예시 |
|--------|------|------|
| STAT_CODE | 통계표 코드 | "901Y001" |
| STAT_NAME | 통계표명 | "소비자물가지수" |
| CYCLE | 주기 (D: 일, M: 월, Q: 분기, H: 반기, A: 연) | "M" |
| SRCH_CNT | 검색 결과 건수 | 1 |
| ORG_NAME | 기관명 | "한국은행" |

### 오류 응답

```json
{
  "RESULT": {
    "CODE": "ERRO-001",
    "MESSAGE": "오류 메시지"
  }
}
```

## Python 구현 예제

```python
import requests
import json

ECOS_API_KEY = "QC05D99HP8DZ9W23YBNI"
API_BASE_URL = "http://ecos.bok.or.kr/api"

def search_statistical_codes(stat_code=None, stat_name=None, start_index=1, end_index=100):
    """
    통계표 코드를 검색합니다.
    
    Args:
        stat_code: 통계표 코드 (부분 검색 가능, 예: "901Y")
        stat_name: 통계표명 (부분 검색 가능, 예: "소비자물가지수")
        start_index: 요청 시작 건수 (기본값: 1)
        end_index: 요청 종료 건수 (기본값: 100)
    
    Returns:
        dict: 검색 결과 또는 에러 정보
    """
    # 파라미터 처리
    stat_code_param = stat_code if stat_code else ""
    stat_name_param = stat_name if stat_name else ""
    
    # URL 구성
    url = f"{API_BASE_URL}/StatisticalCodeSearch/{ECOS_API_KEY}/json/kr/{start_index}/{end_index}/{stat_code_param}/{stat_name_param}"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # 오류 확인
        if 'RESULT' in data:
            result_code = data['RESULT'].get('CODE', '')
            result_message = data['RESULT'].get('MESSAGE', '')
            
            if result_code != 'INFO-000':
                return {
                    "error": f"BOK API Error [{result_code}]: {result_message}",
                    "result_code": result_code,
                    "result_message": result_message
                }
        
        # 검색 결과 반환
        if 'StatisticalCodeSearch' in data:
            return data['StatisticalCodeSearch']
        else:
            return {"error": "Invalid API response format"}
            
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}

# 사용 예제
if __name__ == "__main__":
    # 전체 통계표 목록 조회
    result = search_statistical_codes()
    print(f"전체 통계표 개수: {result.get('list_total_count', 0)}")
    
    # 901Y로 시작하는 통계표 검색
    result = search_statistical_codes(stat_code="901Y")
    print(f"901Y로 시작하는 통계표: {result.get('list_total_count', 0)}개")
    for row in result.get('row', []):
        print(f"  - {row['STAT_CODE']}: {row['STAT_NAME']} (주기: {row['CYCLE']})")
    
    # "소비자물가지수" 검색
    result = search_statistical_codes(stat_name="소비자물가지수")
    print(f"소비자물가지수 관련 통계표: {result.get('list_total_count', 0)}개")
    for row in result.get('row', []):
        print(f"  - {row['STAT_CODE']}: {row['STAT_NAME']}")
```

## Inflation 관련 통계표 코드 검색

Inflation(물가) 기능에 필요한 통계표 코드들을 검색하는 예제:

```python
# Inflation 관련 통계표 코드 검색
inflation_stat_codes = [
    "404Y014", "404Y015", "404Y016", "404Y017",
    "405Y006", "405Y007",
    "901Y009", "901Y010"
]

print("=" * 80)
print("Inflation 관련 통계표 코드 검색")
print("=" * 80)

for stat_code in inflation_stat_codes:
    result = search_statistical_codes(stat_code=stat_code)
    
    if 'error' in result:
        print(f"{stat_code}: {result['error']}")
    else:
        rows = result.get('row', [])
        if rows:
            for row in rows:
                print(f"{row['STAT_CODE']}: {row['STAT_NAME']} (주기: {row['CYCLE']})")
        else:
            print(f"{stat_code}: 검색 결과 없음")
    print()
```

## 활용 방안

### 1. 통계표 코드 자동 검색

프로젝트에서 사용할 통계표 코드를 자동으로 검색하고 매핑:

```python
def get_inflation_stat_codes():
    """Inflation 관련 통계표 코드 목록 조회"""
    # "물가" 또는 "소비자물가" 키워드로 검색
    result = search_statistical_codes(stat_name="물가")
    
    stat_codes = []
    for row in result.get('row', []):
        stat_codes.append({
            "stat_code": row['STAT_CODE'],
            "stat_name": row['STAT_NAME'],
            "cycle": row['CYCLE']
        })
    
    return stat_codes
```

### 2. 통계표 코드 유효성 검증

사용자가 입력한 통계표 코드가 유효한지 확인:

```python
def validate_stat_code(stat_code):
    """통계표 코드 유효성 검증"""
    result = search_statistical_codes(stat_code=stat_code)
    
    if 'error' in result:
        return False, result['error']
    
    rows = result.get('row', [])
    if len(rows) > 0:
        return True, rows[0]
    else:
        return False, "통계표 코드를 찾을 수 없습니다"
```

### 3. 통계표 코드 자동 완성

사용자 입력에 따라 통계표 코드를 자동 완성:

```python
def autocomplete_stat_code(partial_code):
    """통계표 코드 자동 완성"""
    result = search_statistical_codes(stat_code=partial_code)
    
    suggestions = []
    for row in result.get('row', [])[:10]:  # 최대 10개
        suggestions.append({
            "code": row['STAT_CODE'],
            "name": row['STAT_NAME']
        })
    
    return suggestions
```

## 주의사항

1. **페이징**: 한 번에 최대 1000건까지 조회 가능 (요청종료건수 최대 1000)
2. **검색 속도**: 전체 통계표 목록 조회 시 시간이 오래 걸릴 수 있음
3. **API 키**: ECOS API 인증 키가 필요함
4. **주기 정보**: CYCLE 필드는 해당 통계표의 기본 주기를 나타냄

## 관련 API

- **StatisticItemList**: 특정 통계표의 항목 목록 조회
- **StatisticSearch**: 통계 데이터 조회
- **StatisticMeta**: 통계표 메타데이터 조회

## 참고 자료

- [ECOS API 개발 가이드](https://ecos.bok.or.kr/api/#/DevGuide/StatisticalCodeSearch)
- [ECOS API 전체 문서](https://ecos.bok.or.kr/api/)










