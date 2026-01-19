# AAL (All About Logistics) 시스템 기획문서

**Version**: 1.0  
**Date**: 2026-01-19  
**Status**: Production

---

## 1. 시스템 개요

### 1.1 프로젝트 정의

**AAL (All About Logistics)**는 B2B 물류 플랫폼으로, 화주(Shipper)와 포워더(Forwarder)를 연결하여 견적 요청, 비딩, 계약, 배송 추적까지 원스톱 물류 서비스를 제공합니다.

### 1.2 핵심 가치

| 가치 | 설명 |
|------|------|
| **실시간 견적** | AI 기반 즉시 운임 견적 제공 |
| **투명한 비딩** | 다수 포워더의 경쟁 입찰로 최적 가격 도출 |
| **통합 관리** | 견적 → 비딩 → 계약 → 배송 → 정산 원스톱 처리 |
| **시장 인텔리전스** | 해운 지수, 환율, 뉴스 등 시장 데이터 제공 |
| **AI 어시스턴트** | 자연어 기반 업무 자동화 |

### 1.3 사용자 유형

```
┌─────────────────────────────────────────────────────────────┐
│                     AAL Platform                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   Guest     │    │   Shipper   │    │  Forwarder  │     │
│  │  (비로그인)  │    │   (화주)    │    │  (포워더)   │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│        │                  │                  │              │
│        ▼                  ▼                  ▼              │
│  • 운임 조회        • 견적 요청         • 비딩 목록 조회   │
│  • 시장 데이터      • 비딩 관리         • 입찰 제출       │
│  • 뉴스 조회        • 입찰 비교/낙찰    • 입찰 현황       │
│                     • 계약/배송 관리    • 계약/배송 관리   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. 시스템 아키텍처

### 2.1 전체 구조

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Frontend                                   │
│                    (HTML/CSS/JavaScript)                            │
│   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐      │
│   │Dashboard│ │Quotation│ │ Bidding │ │ Market  │ │   AI    │      │
│   │         │ │         │ │  List   │ │  Data   │ │Assistant│      │
│   └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘      │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                         HTTP/REST API
                                │
┌───────────────────────────────┼─────────────────────────────────────┐
│                               ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │              Flask Server (Port 5000)                        │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │    │
│  │  │ BOK API  │ │ AI API   │ │News API  │ │Auth API  │        │    │
│  │  │(환율/지표)│ │(Gemini)  │ │(뉴스수집) │ │(인증)    │        │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘        │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │    │
│  │  │GDELT API │ │KCCI API  │ │Shipping  │ │Report API│        │    │
│  │  │(글로벌경고)│ │(KOBC지수)│ │Indices   │ │(리포트)  │        │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘        │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                               │                                      │
│                               ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │           FastAPI Server (Port 8001)                         │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │    │
│  │  │ Quote    │ │ Bidding  │ │ Contract │ │ Shipment │        │    │
│  │  │ Request  │ │ System   │ │Management│ │ Tracking │        │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘        │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │    │
│  │  │ Freight  │ │ Commerce │ │ PDF Gen  │ │ Email    │        │    │
│  │  │ Rates    │ │ System   │ │          │ │ Service  │        │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘        │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│                          Backend Layer                               │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Database Layer                               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│  │  quote.db   │ │  users.db   │ │news_intel.db│ │shipping.db  │   │
│  │ (견적/비딩)  │ │  (인증)     │ │  (뉴스)     │ │ (해운지수)  │   │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 기술 스택

| 레이어 | 기술 | 용도 |
|--------|------|------|
| **Frontend** | HTML5/CSS3/JavaScript (ES6+) | 웹 UI |
| **Backend (Main)** | Python Flask | API Gateway, 정적 파일 서빙 |
| **Backend (Quote)** | Python FastAPI | 견적/비딩/계약 비즈니스 로직 |
| **AI** | Google Gemini API | AI 어시스턴트, 뉴스 분석 |
| **Database** | SQLite + SQLAlchemy | 데이터 저장 |
| **Scheduler** | APScheduler | 주기적 데이터 수집 |
| **PDF** | ReportLab | RFQ PDF 생성 |
| **Email** | SMTP | 알림 이메일 발송 |

---

## 3. 기능 모듈 상세

### 3.1 견적 요청 시스템 (Quote Request)

**경로**: `quote_backend/`

#### 3.1.1 기능 개요

| 기능 | 설명 |
|------|------|
| 견적 요청 생성 | 화주가 운송 조건 입력하여 견적 요청 |
| 즉시 견적 | 등록된 운임 기반 실시간 예상 운임 제공 |
| 비딩 자동 생성 | 견적 요청 시 자동으로 비딩 생성 |
| RFQ PDF 생성 | 견적 요청서 PDF 자동 생성 |

#### 3.1.2 데이터 모델

```
QuoteRequest (견적 요청)
├── id: PK
├── request_no: 요청번호 (EXSEA00001)
├── customer_id: FK → Customer
├── trade_mode: export/import/domestic
├── shipping_type: ocean/air/truck
├── load_type: FCL/LCL/AIR/FTL/LTL
├── pol/pod: 출발/도착지
├── etd/eta: 출발/도착 예정일
├── incoterms: 인코텀즈
├── status: pending/processing/quoted/accepted
├── created_at: 생성일시
│
├── cargo_details: [CargoDetail] (1:N)
│   ├── container_type / truck_type
│   ├── qty: 수량
│   ├── gross_weight / cbm
│   └── chargeable_weight
│
└── bidding: Bidding (1:1)
```

#### 3.1.3 API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/quote-requests` | 견적 요청 생성 |
| GET | `/api/quote-requests/{id}` | 견적 상세 조회 |
| GET | `/api/quote-requests/customer/{email}` | 고객별 견적 목록 |
| PUT | `/api/quote-requests/{id}` | 견적 수정 |
| DELETE | `/api/quote-requests/{id}` | 견적 취소 |
| GET | `/api/freight/estimate` | 즉시 운임 견적 |

---

### 3.2 비딩 시스템 (Bidding)

**경로**: `quote_backend/`

#### 3.2.1 기능 개요

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  화주       │     │   비딩      │     │  포워더     │
│  (Shipper)  │     │  (Bidding)  │     │ (Forwarder) │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       │ 견적 요청         │                   │
       │──────────────────▶│                   │
       │                   │                   │
       │                   │ 비딩 자동 생성    │
       │                   │──────────────────▶│ 입찰 가능 목록
       │                   │                   │
       │                   │◀──────────────────│ 입찰 제출
       │                   │         Bid       │
       │                   │                   │
       │ 입찰 비교         │                   │
       │◀──────────────────│                   │
       │                   │                   │
       │ 낙찰 결정         │                   │
       │──────────────────▶│──────────────────▶│ 낙찰 통보
       │                   │                   │
       │                   │ 계약 자동 생성    │
       │                   │──────────────────▶│
       │                   │                   │
```

#### 3.2.2 비딩 상태

| 상태 | 설명 |
|------|------|
| `open` | 진행 중 (입찰 가능) |
| `closed` | 마감됨 (입찰 불가) |
| `awarded` | 낙찰 완료 |
| `cancelled` | 취소됨 |
| `expired` | 만료됨 |

#### 3.2.3 API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/biddings` | 비딩 목록 조회 |
| GET | `/api/biddings/{id}` | 비딩 상세 조회 |
| GET | `/api/biddings/{id}/bids` | 비딩의 입찰 목록 |
| POST | `/api/biddings/{id}/bids` | 입찰 제출 |
| POST | `/api/biddings/{id}/award` | 낙찰 처리 |
| POST | `/api/biddings/{id}/close` | 비딩 마감 |

---

### 3.3 계약 및 배송 관리

**경로**: `quote_backend/`

#### 3.3.1 워크플로우

```
[낙찰] → [계약 생성] → [배송 생성] → [추적 업데이트] → [정산]
         │              │              │
         ▼              ▼              ▼
      Contract       Shipment    ShipmentTracking
```

#### 3.3.2 데이터 모델

```
Contract (계약)
├── contract_no: 계약번호
├── bidding_id: FK → Bidding
├── forwarder_id: FK → Forwarder
├── total_amount / currency
├── status: draft/active/completed
└── terms / special_instructions

Shipment (배송)
├── shipment_no: 배송번호
├── contract_id: FK → Contract
├── bl_number / awb_number / tracking_no
├── status: pending/in_transit/delivered
├── actual_departure / actual_arrival
└── tracking_history: [ShipmentTracking] (1:N)

Settlement (정산)
├── settlement_no: 정산번호
├── contract_id: FK → Contract
├── amount / currency
├── status: pending/paid/cancelled
└── invoice_no / payment_date
```

---

### 3.4 AI 어시스턴트

**경로**: `server/gemini_backend.py`, `server/ai_tools.py`

#### 3.4.1 기능 개요

| 기능 | 설명 |
|------|------|
| **자연어 견적** | "부산에서 로테르담 40HC 운임 알려줘" |
| **비딩 조회** | "내 비딩 현황 알려줘" |
| **시장 정보** | "BDI 지수랑 최신 뉴스 보여줘" |
| **페이지 이동** | "견적 페이지로 이동해줘" |
| **복합 요청** | "운임 조회하고 바로 비딩 진행해줘" |

#### 3.4.2 사용자 유형별 동작

| 사용자 | 비딩 조회 결과 |
|--------|---------------|
| **Guest** | 로그인 필요 안내 |
| **Shipper** | 자신의 비딩만 표시 |
| **Forwarder** | 전체 입찰 가능 비딩 표시 |

#### 3.4.3 도구 (Tools)

| 도구 | 용도 | 접근 권한 |
|------|------|----------|
| `get_ocean_rates` | 해상 운임 조회 | 전체 |
| `get_air_rates` | 항공 운임 조회 | 전체 |
| `get_bidding_status` | 비딩 현황 조회 | Shipper/Forwarder |
| `create_quote_request` | 견적 요청 생성 | Shipper |
| `submit_bid` | 입찰 제출 | Forwarder |
| `award_bid` | 낙찰 처리 | Shipper |
| `get_shipping_indices` | 해운 지수 조회 | 전체 |
| `get_latest_news` | 뉴스 조회 | 전체 |
| `navigate_to_page` | 페이지 이동 | 전체 |

#### 3.4.4 API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/ai/chat` | AI 대화 |
| GET | `/api/ai/history` | 대화 이력 조회 |

---

### 3.5 시장 데이터 (Market Data)

**경로**: `server/shipping_indices/`, `server/bok/`

#### 3.5.1 해운 지수

| 지수 | 설명 | 데이터 소스 |
|------|------|------------|
| **BDI** | Baltic Dry Index (건화물 운임) | Excel 파일 |
| **SCFI** | Shanghai Containerized Freight Index | Excel 파일 |
| **CCFI** | China Containerized Freight Index | Excel 파일 |
| **KCCI** | Korea Container Composite Index | 외부 API |

#### 3.5.2 경제 지표

| 지표 | 설명 | 데이터 소스 |
|------|------|------------|
| 환율 | USD, EUR, JPY 등 9개 통화 | 한국은행 ECOS API |
| GDP | 국내총생산 | 한국은행 ECOS API |
| 물가 | 소비자물가지수 | 한국은행 ECOS API |
| 금리 | 기준금리, 시장금리 | 한국은행 ECOS API |

#### 3.5.3 API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/shipping-indices/bdi` | BDI 지수 조회 |
| GET | `/api/shipping-indices/scfi` | SCFI 지수 조회 |
| GET | `/api/shipping-indices/ccfi` | CCFI 지수 조회 |
| GET | `/api/market/indices` | 경제 지표 조회 |

---

### 3.6 뉴스 인텔리전스 (News Intelligence)

**경로**: `server/news_intelligence/`

#### 3.6.1 기능 개요

| 기능 | 설명 |
|------|------|
| **자동 수집** | RSS, Google News, Naver News에서 물류 뉴스 수집 |
| **AI 분석** | Gemini로 카테고리, 위기 여부, 영향도 분석 |
| **카테고리 분류** | Ocean, Air, Inland, Economy, Crisis 등 |
| **위기 뉴스 필터** | 파업, 사고, 공급망 이슈 등 긴급 뉴스 식별 |

#### 3.6.2 뉴스 카테고리

| 카테고리 | 설명 |
|---------|------|
| `Crisis` | 위기/사고 뉴스 |
| `Ocean` | 해운 관련 뉴스 |
| `Air` | 항공 관련 뉴스 |
| `Inland` | 육상/내륙 운송 뉴스 |
| `Economy` | 경제 뉴스 |
| `ETC` | 기타 |

#### 3.6.3 API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/news` | 뉴스 목록 조회 |
| GET | `/api/news/{id}` | 뉴스 상세 조회 |
| GET | `/api/news/crisis` | 위기 뉴스만 조회 |

---

### 3.7 GDELT 글로벌 경고 (Global Alerts)

**경로**: `server/gdelt/`

#### 3.7.1 기능 개요

| 기능 | 설명 |
|------|------|
| **자동 수집** | GDELT 데이터셋에서 글로벌 이벤트 수집 |
| **위기 감지** | 물류 영향 이벤트 자동 감지 |
| **지역별 필터** | 국가/지역별 이벤트 필터링 |

#### 3.7.2 API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/gdelt/alerts` | 글로벌 경고 조회 |
| GET | `/api/gdelt/events` | GDELT 이벤트 조회 |

---

### 3.8 인증 시스템 (Authentication)

**경로**: `server/auth/`

#### 3.8.1 사용자 유형

| 유형 | 설명 | 주요 기능 |
|------|------|----------|
| **Shipper** | 화주 (화물 운송 의뢰) | 견적 요청, 비딩 관리, 낙찰 |
| **Forwarder** | 포워더 (운송 서비스 제공) | 비딩 조회, 입찰 제출 |

#### 3.8.2 API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/auth/register` | 회원가입 |
| POST | `/api/auth/login` | 로그인 |
| POST | `/api/auth/logout` | 로그아웃 |
| GET | `/api/auth/me` | 내 정보 조회 |

---

## 4. 프론트엔드 페이지 구조

### 4.1 페이지 목록

| 페이지 | 파일 | 설명 |
|--------|------|------|
| **메인** | `ai_studio_code_F2.html` | 랜딩 페이지 |
| **견적 요청** | `quotation.html` | 견적 요청 폼 |
| **비딩 목록** | `bidding-list.html` | 비딩 목록 (포워더) |
| **내 견적** | `shipper-bidding.html` | 내 비딩 목록 (화주) |
| **시장 데이터** | `market-data.html` | 해운 지수, 환율 |
| **뉴스** | `news-intelligence.html` | 물류 뉴스 |
| **대시보드 (화주)** | `dashboard-shipper.html` | 화주 대시보드 |
| **대시보드 (포워더)** | `dashboard-forwarder.html` | 포워더 대시보드 |
| **계약 관리** | `contract-management.html` | 계약 관리 |
| **배송 추적** | `shipment-tracking.html` | 배송 추적 |
| **리포트** | `report-insight.html` | 리포트 및 인사이트 |
| **마이페이지** | `mypage.html` | 회원 정보 |

### 4.2 JavaScript 모듈

| 모듈 | 경로 | 기능 |
|------|------|------|
| **ai-assistant.js** | `js/features/` | AI 챗봇 사이드바 |
| **auth.js** | `js/features/` | 로그인/회원가입 |
| **biddingList.js** | `js/features/` | 비딩 목록 관리 |
| **shipperBidding.js** | `js/features/` | 화주 비딩 관리 |
| **dashboard.js** | `js/features/` | 대시보드 |
| **market/** | `js/features/market/` | 시장 데이터 차트 |
| **news-intelligence.js** | `js/features/` | 뉴스 표시 |

---

## 5. 데이터베이스 스키마

### 5.1 데이터베이스 목록

| DB 파일 | 용도 | 위치 |
|---------|------|------|
| `quote.db` | 견적, 비딩, 계약, 배송 | `quote_backend/` |
| `users.db` | 사용자 인증, AI 대화 이력 | `server/auth/` |
| `news_intelligence.db` | 뉴스 데이터 | `server/` |
| `shipping_indices.db` | 해운 지수 | `server/` |
| `kcci.db` | KOBC 컨테이너 지수 | `server/` |
| `reports.db` | 리포트 데이터 | `server/` |

### 5.2 주요 테이블 (quote.db)

```
┌─────────────────────────────────────────────────────────────┐
│                     Reference Data                          │
├─────────────────────────────────────────────────────────────┤
│ ports           │ container_types │ truck_types             │
│ incoterms       │ freight_codes   │ forwarders              │
│ customers       │ ocean_rates     │ trucking_rates          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Transaction Data                          │
├─────────────────────────────────────────────────────────────┤
│ quote_requests  │ cargo_details   │ biddings                │
│ bids            │ contracts       │ shipments               │
│ shipment_tracking│ settlements    │ notifications           │
│ messages        │ ratings         │                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. 키 생성 규칙

### 6.1 요청번호 (Request Number)

| 유형 | 형식 | 예시 |
|------|------|------|
| 수출 해상 | `EXSEA{5자리}` | EXSEA00001 |
| 수출 항공 | `EXAIR{5자리}` | EXAIR00001 |
| 수입 해상 | `IMSEA{5자리}` | IMSEA00001 |
| 수입 항공 | `IMAIR{5자리}` | IMAIR00001 |
| 통합 | `EXALL{5자리}` | EXALL00001 |

### 6.2 비딩번호 (Bidding Number)

- 형식: `BID-{YYYY}-{4자리}`
- 예시: `BID-2026-0001`

### 6.3 계약번호 (Contract Number)

- 형식: `CTR-{YYYY}-{4자리}`
- 예시: `CTR-2026-0001`

### 6.4 배송번호 (Shipment Number)

- 형식: `SHP-{YYYY}-{4자리}`
- 예시: `SHP-2026-0001`

---

## 7. 스케줄러 작업

### 7.1 주기적 작업

| 작업 | 주기 | 설명 |
|------|------|------|
| 뉴스 수집 | 1시간 | RSS, Google, Naver 뉴스 수집 |
| GDELT 수집 | 15분 | 글로벌 이벤트 수집 |
| 비딩 만료 처리 | 1시간 | 마감일 지난 비딩 상태 변경 |
| 해운 지수 업데이트 | 1일 | BDI, SCFI, CCFI 데이터 갱신 |

---

## 8. 외부 API 연동

### 8.1 연동 API 목록

| API | 용도 | 인증 |
|-----|------|------|
| Google Gemini | AI 어시스턴트, 뉴스 분석 | API Key |
| 한국은행 ECOS | 환율, 경제 지표 | API Key |
| GDELT | 글로벌 이벤트 | 없음 (공개) |
| Google News RSS | 뉴스 수집 | 없음 |
| Naver News | 뉴스 수집 | 없음 |

---

## 9. 환경 변수

### 9.1 필수 환경 변수

```env
# AI
GEMINI_API_KEY=your_gemini_api_key

# 한국은행
ECOS_API_KEY=your_ecos_api_key

# Email (선택)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email
SMTP_PASSWORD=your_password
```

---

## 10. 서버 실행

### 10.1 시작 명령

```bash
# 서버 디렉토리로 이동
cd server

# Flask 서버 시작 (Quote Backend 자동 시작)
python main.py
```

### 10.2 포트 구성

| 서비스 | 포트 | 설명 |
|--------|------|------|
| Flask | 5000 | 메인 서버, 정적 파일 |
| FastAPI | 8001 | Quote Backend API |

---

## 11. 버전 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.0 | 2026-01-19 | 초기 기획문서 작성 |

---

**End of Document**
