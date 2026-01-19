# 데이터 모델 정의서 (Data Model Specification)

> **Version**: 1.0.0  
> **Last Updated**: 2026-01-19  
> **ORM**: SQLAlchemy  
> **Database**: SQLite

---

## 목차

1. [데이터베이스 구조](#1-데이터베이스-구조)
2. [마스터 데이터](#2-마스터-데이터)
3. [트랜잭션 데이터](#3-트랜잭션-데이터)
4. [사용자 데이터](#4-사용자-데이터)
5. [시장 데이터](#5-시장-데이터)
6. [ER 다이어그램](#6-er-다이어그램)

---

## 1. 데이터베이스 구조

### 1.1 데이터베이스 목록

| DB 파일 | 위치 | 용도 |
|---------|------|------|
| **quote.db** | `quote_backend/` | 견적, 비딩, 마스터 데이터 |
| **users.db** | `server/auth/` | 사용자, AI 대화 이력 |
| **shipping_indices.db** | `server/` | 해운 지수 (BDI, SCFI, CCFI) |
| **news_intelligence.db** | `server/` | 뉴스 데이터 |

### 1.2 테이블 구성

```
quote.db
├── 마스터 데이터
│   ├── ports              # 항구/공항
│   ├── container_types    # 컨테이너 유형
│   ├── truck_types        # 트럭 유형
│   ├── incoterms          # 인코텀즈
│   ├── freight_categories # 운임 카테고리
│   ├── freight_codes      # 운임 코드
│   └── freight_units      # 운임 단위
│
├── 트랜잭션 데이터
│   ├── customers          # 고객 (화주)
│   ├── quote_requests     # 견적 요청
│   ├── cargo_details      # 화물 상세
│   ├── biddings           # 비딩
│   ├── forwarders         # 포워더
│   ├── bids               # 입찰
│   ├── contracts          # 계약
│   ├── shipments          # 배송
│   └── settlements        # 정산
│
└── 운임 데이터
    ├── ocean_rate_sheets  # 해상 운임표
    ├── ocean_rate_items   # 해상 운임 항목
    └── trucking_rates     # 내륙 운송 요금
```

---

## 2. 마스터 데이터

### 2.1 ports (항구/공항)

| 컬럼 | 타입 | Null | 설명 |
|------|------|------|------|
| **id** | INTEGER | PK | 고유 ID |
| **code** | VARCHAR(10) | NOT NULL, UNIQUE | 항구 코드 (KRPUS, NLRTM) |
| **name** | VARCHAR(100) | NOT NULL | 영문명 (BUSAN) |
| **name_ko** | VARCHAR(100) | NULL | 한글명 (부산) |
| **country** | VARCHAR(50) | NOT NULL | 국가명 (KOREA) |
| **country_code** | VARCHAR(2) | NOT NULL | 국가 코드 (KR) |
| **port_type** | VARCHAR(20) | NOT NULL | ocean/air/both |
| **is_active** | BOOLEAN | DEFAULT TRUE | 활성 상태 |
| **created_at** | DATETIME | DEFAULT NOW | 생성일 |

**인덱스**:
- `ix_ports_code` (code)
- `ix_ports_country_code` (country_code)
- `ix_ports_port_type` (port_type)

**예시 데이터**:
```sql
INSERT INTO ports (code, name, name_ko, country, country_code, port_type)
VALUES 
('KRPUS', 'BUSAN', '부산', 'KOREA', 'KR', 'ocean'),
('KRICN', 'INCHEON', '인천', 'KOREA', 'KR', 'both'),
('NLRTM', 'ROTTERDAM', '로테르담', 'NETHERLANDS', 'NL', 'ocean'),
('DEHAM', 'HAMBURG', '함부르크', 'GERMANY', 'DE', 'ocean');
```

### 2.2 container_types (컨테이너 유형)

| 컬럼 | 타입 | Null | 설명 |
|------|------|------|------|
| **id** | INTEGER | PK | 고유 ID |
| **code** | VARCHAR(20) | NOT NULL, UNIQUE | 코드 (20DC, 40HC) |
| **name** | VARCHAR(50) | NOT NULL | 정식명 |
| **abbreviation** | VARCHAR(20) | NULL | 약어 (20'GP, 40'HC) |
| **description** | VARCHAR(200) | NULL | 설명 |
| **size** | VARCHAR(10) | NULL | 크기 (20, 40, 4H) |
| **category** | VARCHAR(10) | NULL | 카테고리 (DC, HC, RF) |
| **size_teu** | DECIMAL(3,1) | NULL | TEU 크기 |
| **iso_standard** | VARCHAR(20) | NULL | ISO 코드 |
| **tare_weight** | DECIMAL(10,2) | NULL | 자체 중량 (kg) |
| **max_weight_kg** | INTEGER | NULL | 최대 적재 중량 |
| **length_mm** | INTEGER | NULL | 내부 길이 (mm) |
| **width_mm** | INTEGER | NULL | 내부 너비 (mm) |
| **height_mm** | INTEGER | NULL | 내부 높이 (mm) |
| **max_cbm** | DECIMAL(5,2) | NULL | 최대 CBM |
| **is_active** | BOOLEAN | DEFAULT TRUE | 활성 상태 |
| **sort_order** | INTEGER | DEFAULT 0 | 정렬 순서 |
| **created_at** | DATETIME | DEFAULT NOW | 생성일 |

**예시 데이터**:
```sql
INSERT INTO container_types (code, name, abbreviation, size, category, max_weight_kg, max_cbm)
VALUES 
('20DC', '20 Dry Container', '20''GP', '20', 'DC', 21800, 33.2),
('40DC', '40 Dry Container', '40''GP', '40', 'DC', 26680, 67.7),
('40HC', '40 High Cube', '40''HC', '4H', 'HC', 26460, 76.3),
('20RF', '20 Reefer Container', '20''RF', '20', 'RF', 21500, 28.0),
('40RF', '40 Reefer Container', '40''RF', '40', 'RF', 26280, 59.0);
```

### 2.3 incoterms (인코텀즈)

| 컬럼 | 타입 | Null | 설명 |
|------|------|------|------|
| **id** | INTEGER | PK | 고유 ID |
| **code** | VARCHAR(3) | NOT NULL, UNIQUE | 코드 (EXW, FOB) |
| **name** | VARCHAR(50) | NOT NULL | 정식명 |
| **description** | VARCHAR(500) | NULL | 영문 설명 |
| **description_ko** | VARCHAR(500) | NULL | 한글 설명 |
| **seller_responsibility** | VARCHAR(200) | NULL | 매도인 책임 |
| **buyer_responsibility** | VARCHAR(200) | NULL | 매수인 책임 |
| **is_active** | BOOLEAN | DEFAULT TRUE | 활성 상태 |
| **sort_order** | INTEGER | DEFAULT 0 | 정렬 순서 |
| **created_at** | DATETIME | DEFAULT NOW | 생성일 |

### 2.4 freight_codes (운임 코드)

| 컬럼 | 타입 | Null | 설명 |
|------|------|------|------|
| **id** | INTEGER | PK | 고유 ID |
| **code** | VARCHAR(20) | NOT NULL, UNIQUE | 운임 코드 (FRT, THC) |
| **category_id** | INTEGER | FK | 카테고리 ID |
| **group_name** | VARCHAR(50) | NULL | 그룹명 |
| **name_en** | VARCHAR(100) | NOT NULL | 영문명 |
| **name_ko** | VARCHAR(100) | NULL | 한글명 |
| **vat_applicable** | BOOLEAN | DEFAULT FALSE | 부가세 대상 |
| **default_currency** | VARCHAR(3) | DEFAULT 'USD' | 기본 통화 |
| **is_active** | BOOLEAN | DEFAULT TRUE | 활성 상태 |
| **sort_order** | INTEGER | DEFAULT 0 | 정렬 순서 |
| **created_at** | DATETIME | DEFAULT NOW | 생성일 |

**주요 운임 코드**:
| 코드 | 명칭 | 설명 |
|------|------|------|
| FRT | Ocean Freight | 해상 운임 |
| AFT | Air Freight | 항공 운임 |
| BAF | Bunker Adjustment Factor | 유류할증료 |
| THC | Terminal Handling Charge | 터미널 작업비 |
| DOC | Document Fee | 서류비 |
| WFG | Wharfage | 부두 사용료 |
| CFS | CFS Charge | CFS 비용 |
| SEAL | Seal Fee | 씰 비용 |

---

## 3. 트랜잭션 데이터

### 3.1 customers (고객/화주)

| 컬럼 | 타입 | Null | 설명 |
|------|------|------|------|
| **id** | INTEGER | PK | 고유 ID |
| **company** | VARCHAR(50) | NOT NULL | 회사명 |
| **job_title** | VARCHAR(30) | NULL | 직책 |
| **name** | VARCHAR(30) | NOT NULL | 담당자명 |
| **email** | VARCHAR(30) | NOT NULL | 이메일 |
| **phone** | VARCHAR(30) | NOT NULL | 연락처 |
| **created_at** | DATETIME | DEFAULT NOW | 생성일 |

### 3.2 quote_requests (견적 요청)

| 컬럼 | 타입 | Null | 설명 |
|------|------|------|------|
| **id** | INTEGER | PK | 고유 ID |
| **customer_id** | INTEGER | FK | 고객 ID |
| **trade_mode** | ENUM | NOT NULL | export/import/domestic |
| **shipping_type** | ENUM | NOT NULL | ocean/air/truck/all |
| **load_type** | VARCHAR(10) | NULL | FCL/LCL/Air/FTL/LTL |
| **pol** | VARCHAR(100) | NOT NULL | 출발지 |
| **pod** | VARCHAR(100) | NOT NULL | 도착지 |
| **etd** | DATE | NOT NULL | 출발 예정일 |
| **incoterms** | VARCHAR(3) | NULL | 인코텀즈 코드 |
| **export_cc** | BOOLEAN | DEFAULT FALSE | 수출 통관 |
| **import_cc** | BOOLEAN | DEFAULT FALSE | 수입 통관 |
| **ship_insurance** | BOOLEAN | DEFAULT FALSE | 운송 보험 |
| **pickup_required** | BOOLEAN | DEFAULT FALSE | 픽업 필요 |
| **pickup_addr** | VARCHAR(200) | NULL | 픽업 주소 |
| **delivery_required** | BOOLEAN | DEFAULT FALSE | 배송 필요 |
| **delivery_addr** | VARCHAR(200) | NULL | 배송 주소 |
| **invoice_value** | DECIMAL(15,2) | NULL | 인보이스 금액 |
| **remark** | TEXT | NULL | 비고 |
| **cargo_summary** | VARCHAR(200) | NULL | 화물 요약 |
| **status** | ENUM | DEFAULT 'pending' | 상태 |
| **created_at** | DATETIME | DEFAULT NOW | 생성일 |
| **updated_at** | DATETIME | ON UPDATE NOW | 수정일 |

**상태 (QuoteStatusEnum)**:
- `pending`: 대기중
- `processing`: 처리중
- `quoted`: 견적 완료
- `accepted`: 수락됨
- `rejected`: 거절됨
- `cancelled`: 취소됨

### 3.3 cargo_details (화물 상세)

| 컬럼 | 타입 | Null | 설명 |
|------|------|------|------|
| **id** | INTEGER | PK | 고유 ID |
| **quote_request_id** | INTEGER | FK | 견적 요청 ID |
| **row_index** | INTEGER | DEFAULT 0 | 행 번호 |
| **container_type** | VARCHAR(20) | NULL | 컨테이너 타입 |
| **truck_type** | VARCHAR(20) | NULL | 트럭 타입 |
| **length** | INTEGER | NULL | 길이 (cm) |
| **width** | INTEGER | NULL | 너비 (cm) |
| **height** | INTEGER | NULL | 높이 (cm) |
| **qty** | INTEGER | DEFAULT 1 | 수량 |
| **gross_weight** | DECIMAL(10,2) | NULL | 총 중량 (kg) |
| **cbm** | DECIMAL(10,3) | NULL | CBM |
| **volume_weight** | INTEGER | NULL | 용적 중량 |
| **chargeable_weight** | INTEGER | NULL | 청구 중량 |
| **created_at** | DATETIME | DEFAULT NOW | 생성일 |

### 3.4 biddings (비딩)

| 컬럼 | 타입 | Null | 설명 |
|------|------|------|------|
| **id** | INTEGER | PK | 고유 ID |
| **bidding_no** | VARCHAR(20) | NOT NULL, UNIQUE | 비딩 번호 |
| **quote_request_id** | INTEGER | FK | 견적 요청 ID |
| **status** | ENUM | DEFAULT 'open' | 상태 |
| **deadline** | DATETIME | NOT NULL | 마감일 |
| **awarded_bid_id** | INTEGER | FK, NULL | 낙찰 입찰 ID |
| **awarded_at** | DATETIME | NULL | 낙찰일 |
| **created_at** | DATETIME | DEFAULT NOW | 생성일 |
| **updated_at** | DATETIME | ON UPDATE NOW | 수정일 |

**상태 (BiddingStatusEnum)**:
- `open`: 진행중
- `closed`: 마감
- `awarded`: 낙찰완료
- `expired`: 만료
- `cancelled`: 취소

### 3.5 forwarders (포워더)

| 컬럼 | 타입 | Null | 설명 |
|------|------|------|------|
| **id** | INTEGER | PK | 고유 ID |
| **company** | VARCHAR(100) | NOT NULL | 회사명 |
| **business_no** | VARCHAR(20) | NULL | 사업자번호 |
| **name** | VARCHAR(50) | NOT NULL | 담당자명 |
| **email** | VARCHAR(100) | NOT NULL, UNIQUE | 이메일 |
| **phone** | VARCHAR(30) | NOT NULL | 연락처 |
| **password_hash** | VARCHAR(255) | NOT NULL | 비밀번호 해시 |
| **is_active** | BOOLEAN | DEFAULT TRUE | 활성 상태 |
| **rating_avg** | DECIMAL(3,2) | DEFAULT 0 | 평균 평점 |
| **rating_count** | INTEGER | DEFAULT 0 | 평가 수 |
| **created_at** | DATETIME | DEFAULT NOW | 생성일 |
| **last_login_at** | DATETIME | NULL | 마지막 로그인 |

### 3.6 bids (입찰)

| 컬럼 | 타입 | Null | 설명 |
|------|------|------|------|
| **id** | INTEGER | PK | 고유 ID |
| **bidding_id** | INTEGER | FK | 비딩 ID |
| **forwarder_id** | INTEGER | FK | 포워더 ID |
| **freight_items** | TEXT | NOT NULL | 운임 항목 (JSON) |
| **total_usd** | DECIMAL(15,2) | DEFAULT 0 | USD 총액 |
| **total_krw** | DECIMAL(15,2) | DEFAULT 0 | KRW 총액 |
| **etd** | DATE | NULL | 출발 예정일 |
| **eta** | DATE | NULL | 도착 예정일 |
| **validity** | DATE | NULL | 유효기간 |
| **remark** | TEXT | NULL | 비고 |
| **status** | ENUM | DEFAULT 'submitted' | 상태 |
| **created_at** | DATETIME | DEFAULT NOW | 생성일 |
| **updated_at** | DATETIME | ON UPDATE NOW | 수정일 |

**상태 (BidStatusEnum)**:
- `draft`: 임시저장
- `submitted`: 제출됨
- `awarded`: 낙찰
- `rejected`: 탈락

**freight_items JSON 구조**:
```json
[
  {
    "code": "FRT",
    "name": "Ocean Freight",
    "currency": "USD",
    "unit_price": 2400,
    "unit": "CNTR",
    "quantity": 2,
    "amount": 4800,
    "tax_type": "영세"
  }
]
```

### 3.7 contracts (계약)

| 컬럼 | 타입 | Null | 설명 |
|------|------|------|------|
| **id** | INTEGER | PK | 고유 ID |
| **contract_no** | VARCHAR(20) | NOT NULL, UNIQUE | 계약 번호 |
| **bidding_id** | INTEGER | FK | 비딩 ID |
| **bid_id** | INTEGER | FK | 입찰 ID |
| **customer_id** | INTEGER | FK | 고객 ID |
| **forwarder_id** | INTEGER | FK | 포워더 ID |
| **status** | ENUM | DEFAULT 'pending' | 상태 |
| **confirmed_at** | DATETIME | NULL | 확정일 |
| **cancelled_at** | DATETIME | NULL | 취소일 |
| **cancel_reason** | TEXT | NULL | 취소 사유 |
| **created_at** | DATETIME | DEFAULT NOW | 생성일 |

### 3.8 shipments (배송)

| 컬럼 | 타입 | Null | 설명 |
|------|------|------|------|
| **id** | INTEGER | PK | 고유 ID |
| **shipment_no** | VARCHAR(20) | NOT NULL, UNIQUE | 배송 번호 |
| **contract_id** | INTEGER | FK | 계약 ID |
| **tracking_no** | VARCHAR(50) | NULL | 추적 번호 |
| **status** | ENUM | DEFAULT 'pending' | 상태 |
| **actual_etd** | DATETIME | NULL | 실제 출발일 |
| **actual_eta** | DATETIME | NULL | 실제 도착일 |
| **delivered_at** | DATETIME | NULL | 배송 완료일 |
| **created_at** | DATETIME | DEFAULT NOW | 생성일 |
| **updated_at** | DATETIME | ON UPDATE NOW | 수정일 |

---

## 4. 사용자 데이터

### 4.1 users (사용자)

**DB**: `users.db`

| 컬럼 | 타입 | Null | 설명 |
|------|------|------|------|
| **id** | INTEGER | PK | 고유 ID |
| **user_type** | VARCHAR(20) | NOT NULL | shipper/forwarder |
| **company** | VARCHAR(100) | NOT NULL | 회사명 |
| **business_no** | VARCHAR(20) | NULL | 사업자번호 |
| **name** | VARCHAR(50) | NOT NULL | 담당자명 |
| **email** | VARCHAR(100) | NOT NULL, UNIQUE | 이메일 |
| **phone** | VARCHAR(30) | NOT NULL | 연락처 |
| **password_hash** | VARCHAR(255) | NOT NULL | 비밀번호 (bcrypt) |
| **is_active** | BOOLEAN | DEFAULT TRUE | 활성 상태 |
| **is_verified** | BOOLEAN | DEFAULT FALSE | 인증 여부 |
| **created_at** | DATETIME | DEFAULT NOW | 생성일 |
| **updated_at** | DATETIME | ON UPDATE NOW | 수정일 |
| **last_login_at** | DATETIME | NULL | 마지막 로그인 |

### 4.2 ai_conversations (AI 대화 이력)

**DB**: `users.db`

| 컬럼 | 타입 | Null | 설명 |
|------|------|------|------|
| **id** | INTEGER | PK | 고유 ID |
| **user_id** | INTEGER | FK, NULL | 사용자 ID (비로그인 시 NULL) |
| **session_id** | VARCHAR(100) | NOT NULL | 세션 ID |
| **role** | VARCHAR(20) | NOT NULL | user/assistant |
| **content** | VARCHAR(10000) | NOT NULL | 메시지 내용 |
| **tool_used** | VARCHAR(500) | NULL | 사용된 Tool (JSON) |
| **quote_data** | VARCHAR(5000) | NULL | 견적 데이터 (JSON) |
| **navigation** | VARCHAR(500) | NULL | 네비게이션 (JSON) |
| **created_at** | DATETIME | DEFAULT NOW | 생성일 |

**인덱스**:
- `ix_ai_conv_user_id` (user_id)
- `ix_ai_conv_session_id` (session_id)

---

## 5. 시장 데이터

### 5.1 shipping_indices (해운 지수)

**DB**: `shipping_indices.db`

| 컬럼 | 타입 | Null | 설명 |
|------|------|------|------|
| **id** | INTEGER | PK | 고유 ID |
| **index_type** | VARCHAR(10) | NOT NULL | BDI/SCFI/CCFI |
| **date** | DATE | NOT NULL | 날짜 |
| **value** | DECIMAL(10,2) | NOT NULL | 지수값 |
| **change** | DECIMAL(10,2) | NULL | 변동값 |
| **change_percent** | DECIMAL(5,2) | NULL | 변동률 |
| **created_at** | DATETIME | DEFAULT NOW | 생성일 |

**인덱스**:
- `ix_indices_type_date` (index_type, date)

### 5.2 news (뉴스)

**DB**: `news_intelligence.db`

| 컬럼 | 타입 | Null | 설명 |
|------|------|------|------|
| **id** | INTEGER | PK | 고유 ID |
| **title** | VARCHAR(500) | NOT NULL | 제목 |
| **summary** | TEXT | NULL | 요약 |
| **content** | TEXT | NULL | 본문 |
| **category** | VARCHAR(20) | NOT NULL | 카테고리 |
| **severity** | VARCHAR(20) | NULL | 심각도 |
| **source** | VARCHAR(100) | NULL | 출처 |
| **url** | VARCHAR(500) | NULL | 원문 URL |
| **image_url** | VARCHAR(500) | NULL | 이미지 URL |
| **location_name** | VARCHAR(100) | NULL | 위치명 |
| **location_lat** | DECIMAL(10,6) | NULL | 위도 |
| **location_lng** | DECIMAL(10,6) | NULL | 경도 |
| **news_type** | VARCHAR(10) | DEFAULT 'GLOBAL' | KR/GLOBAL |
| **is_crisis** | BOOLEAN | DEFAULT FALSE | 위기 뉴스 |
| **published_at** | DATETIME | NOT NULL | 발행일 |
| **created_at** | DATETIME | DEFAULT NOW | 생성일 |

---

## 6. ER 다이어그램

### 6.1 견적/비딩 관계

```
┌──────────────┐     ┌───────────────────┐     ┌──────────────┐
│   Customer   │     │   QuoteRequest    │     │  CargoDetail │
├──────────────┤     ├───────────────────┤     ├──────────────┤
│ id (PK)      │1───N│ id (PK)           │1───N│ id (PK)      │
│ company      │     │ customer_id (FK)  │     │ quote_req_id │
│ name         │     │ trade_mode        │     │ container    │
│ email        │     │ shipping_type     │     │ qty          │
│ phone        │     │ pol, pod          │     │ weight       │
└──────────────┘     │ etd               │     └──────────────┘
                     │ incoterms         │
                     └─────────┬─────────┘
                               │1
                               │
                               │1
                     ┌─────────┴─────────┐
                     │     Bidding       │
                     ├───────────────────┤
                     │ id (PK)           │
                     │ bidding_no        │
                     │ quote_request_id  │
                     │ status            │1───N┌──────────────┐
                     │ deadline          │     │     Bid      │
                     │ awarded_bid_id    │     ├──────────────┤
                     └───────────────────┘     │ id (PK)      │
                                               │ bidding_id   │
                     ┌──────────────┐          │ forwarder_id │
                     │  Forwarder   │1────────N│ freight_items│
                     ├──────────────┤          │ total_usd    │
                     │ id (PK)      │          │ total_krw    │
                     │ company      │          │ status       │
                     │ email        │          └──────────────┘
                     │ rating_avg   │
                     └──────────────┘
```

### 6.2 계약/배송 관계

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Bidding    │     │   Contract   │     │   Shipment   │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ id (PK)      │1───1│ id (PK)      │1───1│ id (PK)      │
│ bidding_no   │     │ contract_no  │     │ shipment_no  │
│ status       │     │ bidding_id   │     │ contract_id  │
│              │     │ bid_id       │     │ tracking_no  │
│              │     │ status       │     │ status       │
└──────────────┘     └──────────────┘     └──────────────┘
        │                                         │
        │                                         │
        ▼                                         ▼
┌──────────────┐                         ┌──────────────────┐
│     Bid      │                         │ ShipmentTracking │
├──────────────┤                         ├──────────────────┤
│ id (PK)      │                         │ id (PK)          │
│ bidding_id   │                         │ shipment_id      │
│ forwarder_id │                         │ status           │
│ status       │                         │ location         │
└──────────────┘                         │ timestamp        │
                                         └──────────────────┘
```

### 6.3 사용자/AI 관계

```
┌──────────────┐     ┌───────────────────┐
│     User     │     │  AIConversation   │
├──────────────┤     ├───────────────────┤
│ id (PK)      │1───N│ id (PK)           │
│ user_type    │     │ user_id (FK)      │
│ company      │     │ session_id        │
│ email        │     │ role              │
│ password     │     │ content           │
└──────────────┘     │ tool_used         │
                     └───────────────────┘
```

---

## 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
|------|------|--------|-----------|
| 1.0.0 | 2026-01-19 | - | 초기 작성 |
