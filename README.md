# AAL - All About Logistics

물류 관련 시장 데이터 및 환율 정보를 제공하는 웹 플랫폼입니다.

## 📋 프로젝트 개요

AAL (All About Logistics)는 한국은행 ECOS API를 활용하여 실시간 환율 데이터를 시각화하고, 물류 관련 시장 정보를 제공하는 웹 애플리케이션입니다.

### 주요 기능

- **실시간 환율 차트**: SVG 기반 인터랙티브 차트로 다중 통화 환율 추이 시각화
- **환율 계산기**: 9개 주요 통화의 원화 변환 계산
- **환율 테이블**: 현재 환율 및 전일 대비 변동률 표시
- **기간 필터링**: 1주, 1개월, 3개월, 1년 단위 데이터 조회
- **인터랙티브 툴팁**: 차트 호버 시 날짜별 상세 환율 정보 표시

## 🛠 기술 스택

### 백엔드
- **Python 3.x**
- **Flask**: 웹 프레임워크
- **Flask-CORS**: CORS 지원
- **requests**: HTTP 클라이언트
- **python-dotenv**: 환경 변수 관리

### 프론트엔드
- **HTML5 / CSS3**: 반응형 웹 디자인
- **Vanilla JavaScript**: ES6+ 모던 JavaScript
- **SVG**: 인터랙티브 차트 렌더링

### 외부 API
- **한국은행 ECOS API**: 경제 통계 데이터 (환율, 물가, GDP 등)

## 📁 프로젝트 구조

```
AAL/
├── server/                    # Flask 백엔드 서버
│   ├── main.py               # Flask 메인 애플리케이션
│   ├── bok_backend.py        # 한국은행 ECOS API 연동 모듈
│   └── requirements.txt      # Python 의존성
│
├── frontend/                  # 프론트엔드
│   └── ai_studio_code_F2.html # 메인 HTML 파일 (단일 파일 구조)
│
├── docs/                      # 문서
│   ├── CURRENCY_MAPPING_TABLE.md # 통화 매핑 테이블
│   ├── currency_mapping_table.json # 통화 매핑 JSON
│   └── api/                   # API 문서
│       └── ecos/              # 한국은행 ECOS API 개발 명세서
│
├── .cursor/                   # Cursor 설정
│   └── rules/                # 개발 작업 규칙
│       ├── frontend-rule/    # 프론트엔드 개발 규칙
│       ├── backend-rule/     # 백엔드 개발 규칙
│       ├── uiux-rule/        # UI/UX 개발 규칙
│       └── Planner/          # 기획 규칙
│
├── scripts/                   # 유틸리티 스크립트
│   └── validate_integration.py # 통합 검증 스크립트
│
├── .gitignore                # Git 무시 파일
├── .env.example              # 환경 변수 예시
└── README.md                 # 프로젝트 문서
```

## 🚀 시작하기

### 사전 요구사항

- Python 3.8 이상
- pip (Python 패키지 관리자)
- 한국은행 ECOS API 키 ([신청 링크](http://ecos.bok.or.kr/api/))

### 설치

1. **저장소 클론**
```bash
git clone <repository-url>
cd AAL
```

2. **Python 가상환경 생성 및 활성화** (권장)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. **의존성 설치**
```bash
cd server
pip install -r requirements.txt
```

4. **환경 변수 설정**

프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 추가합니다:

```env
ECOS_API_KEY=your_api_key_here
```

> **참고**: API 키가 없는 경우 `server/bok_backend.py`의 fallback 키가 사용됩니다 (개발용).

### 실행

1. **Flask 서버 시작**
```bash
cd server
python main.py
```

2. **브라우저에서 접속**
```
http://localhost:5000
```

서버가 정상적으로 시작되면 터미널에 다음과 같은 메시지가 표시됩니다:

```
==================================================
Starting Flask Server on http://localhost:5000
BASE_DIR: <프로젝트 경로>
HTML file exists: True
==================================================
```

## 📡 API 엔드포인트

### 환율 및 시장 데이터

#### 1. 한국은행 통계 조회
```
GET /api/bok/stats
```

**파라미터:**
- `statCode` (required): 통계표 코드 (예: "731Y001")
- `itemCode` (required): 항목 코드 (예: "0000001")
- `cycle` (optional): 주기 (D: 일, M: 월, Q: 분기, Y: 연) - 기본값: "D"
- `startDate` (required): 시작일자 (YYYYMMDD 형식)
- `endDate` (required): 종료일자 (YYYYMMDD 형식)

**예시:**
```
GET /api/bok/stats?statCode=731Y001&itemCode=0000001&cycle=D&startDate=20240101&endDate=20241231
```

#### 2. 시장 지수 조회 (단일)
```
GET /api/market/indices
```

**파라미터:**
- `type` (required): 카테고리 (exchange, inflation, gdp, money, sentiment, balance)
- `itemCode` (optional): 항목 코드
- `startDate` (required): 시작일자 (YYYYMMDD)
- `endDate` (required): 종료일자 (YYYYMMDD)
- `cycle` (optional): 주기

#### 3. 시장 지수 조회 (다중)
```
GET /api/market/indices/multi
```

**파라미터:**
- `type` (required): 카테고리
- `itemCode` (optional): 여러 개의 itemCode를 배열로 전달 가능
- `startDate` (required)
- `endDate` (required)
- `cycle` (optional)

#### 4. 카테고리 정보 조회
```
GET /api/market/categories
```

**파라미터:**
- `category` (optional): 특정 카테고리 정보만 조회

### 기타

#### 5. 뉴스 데이터 (목 데이터)
```
GET /api/news
```

#### 6. 물류 지수 (목 데이터)
```
GET /api/logistics
```

## 💱 지원 통화

현재 다음 9개 통화를 지원합니다:

| 통화 코드 | item_code | 통화명 |
|----------|-----------|--------|
| USD | 0000001 | 미국 달러 |
| EUR | 0000003 | 유로 |
| JPY | 0000002 | 일본 엔화 (100엔) |
| CNY | 0000053 | 중국 위안화 |
| GBP | 0000012 | 영국 파운드 |
| CHF | 0000014 | 스위스 프랑 |
| HKD | 0000015 | 홍콩 달러 |
| CAD | 0000013 | 캐나다 달러 |
| RUB | 0000043 | 러시아 루블 |

자세한 통화 매핑 정보는 [CURRENCY_MAPPING_TABLE.md](./docs/CURRENCY_MAPPING_TABLE.md)를 참고하세요.

## 🎨 주요 기능 상세

### 환율 차트
- SVG 기반 인터랙티브 차트
- 다중 통화 동시 표시 (최대 9개)
- 기간 필터링 (1W, 1M, 3M, 1Y)
- 호버 툴팁으로 날짜별 상세 정보 표시
- X축 요일 레이블 자동 생성

### 환율 계산기
- 실시간 원화 변환 계산
- 통화 선택 드롭다운
- 금액 입력 필드

### 환율 테이블
- 현재 환율 표시
- 전일 대비 변동률 계산
- 색상 및 아이콘으로 상승/하락 표시
  - 🔴 빨간색 + ↑ : 상승
  - 🟢 초록색 + ↓ : 하락

## 🔧 개발 가이드

### 통합 검증 프로세스

모든 개발 작업 전/후에 통합 검증 스크립트를 실행하여 시스템 일관성을 확인합니다:

```bash
python scripts/validate_integration.py
```

**검증 항목:**
- 파일 참조 관계 확인 (RULE.md에서 언급한 파일 존재 여부)
- 함수명 일관성 확인 (RULE.md와 실제 코드 간 일치)
- API 엔드포인트 일관성 확인
- CSS 변수 일관성 확인
- BOK_MAPPING 구조 확인
- 프론트엔드 HTML 구조 확인
- AGENT_RULE 파일 존재 확인

**각 Agent의 검증 프로세스:**
- 프론트엔드 Agent: `.cursor/rules/frontend-rule/RULE.md` 참고
- 백엔드 Agent: `.cursor/rules/backend-rule/RULE.md` 참고
- UI/UX Agent: `.cursor/rules/uiux-rule/RULE.md` 참고
- Planner Agent: `.cursor/rules/Planner/RULE.md` 참고

### 백엔드 개발

백엔드 코드는 `server/` 디렉토리에 위치합니다.

- `main.py`: Flask 애플리케이션 메인 파일
- `bok_backend.py`: 한국은행 ECOS API 연동 모듈

새로운 API 엔드포인트를 추가할 때는:
1. `server/main.py`에 라우트 추가
2. 필요시 `server/bok_backend.py`에 헬퍼 함수 추가
3. API 문서 업데이트
4. 통합 검증 스크립트 실행

### 프론트엔드 개발

메인 프론트엔드 파일은 `frontend/ai_studio_code_F2.html`입니다.

주요 JavaScript 함수:
- `processExchangeRateData()`: 환율 데이터 처리
- `updateChart()`: 차트 업데이트
- `updateCurrencyRatesTable()`: 환율 테이블 업데이트
- `showTooltip()` / `hideTooltip()`: 툴팁 관리
- `renderXAxisLabels()`: X축 레이블 렌더링

새로운 기능 추가 시:
1. 통합 검증 스크립트 실행 (작업 전)
2. 기존 코드 스타일 준수
3. 통합 검증 스크립트 재실행 (작업 후)

### API 연동

한국은행 ECOS API 연동 시:
1. `docs/api/ecos/` 디렉토리의 개발 명세서 참고
2. `server/bok_backend.py`의 `BOK_MAPPING`에 새로운 카테고리/항목 추가
3. `docs/CURRENCY_MAPPING_TABLE.md` 업데이트
4. 통합 검증 스크립트 실행하여 일관성 확인

## 📝 참고 문서

- [한국은행 ECOS API 개발 가이드](http://ecos.bok.or.kr/api/#/DevGuide/DevSpeciflcation)
- [통화 매핑 테이블](./docs/CURRENCY_MAPPING_TABLE.md)
- [API 개발 명세서](./docs/api/ecos/)
- [Cursor Rules](./.cursor/rules/) - 개발 작업 규칙

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

## 👥 팀

- 개발팀

## 📞 문의

프로젝트 관련 문의사항이 있으시면 이슈를 등록해주세요.

---

**Made with ❤️ for Logistics Professionals**
