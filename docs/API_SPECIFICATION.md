# API 명세서 (API Specification)

> **Version**: 1.0.0  
> **Last Updated**: 2026-01-19  
> **Base URLs**:
> - Flask Server: `http://localhost:5000`
> - FastAPI Server: `http://localhost:8001`

---

## 목차

1. [개요](#1-개요)
2. [인증 API](#2-인증-api)
3. [견적/비딩 API](#3-견적비딩-api)
4. [입찰 API](#4-입찰-api)
5. [시장 데이터 API](#5-시장-데이터-api)
6. [뉴스 API](#6-뉴스-api)
7. [AI API](#7-ai-api)
8. [에러 코드](#8-에러-코드)

---

## 1. 개요

### 1.1 서버 구분

| 서버 | Base URL | 담당 API |
|------|----------|----------|
| **Flask** | `:5000` | 인증, AI, 시장 데이터, 뉴스, 정적 파일 |
| **FastAPI** | `:8001` | 견적, 비딩, 입찰, 계약, 정산 |

### 1.2 공통 헤더

```http
Content-Type: application/json
Accept: application/json
```

### 1.3 응답 형식

**성공 응답**:
```json
{
  "success": true,
  "message": "처리 완료",
  "data": { ... }
}
```

**실패 응답**:
```json
{
  "success": false,
  "message": "오류 메시지",
  "error_code": "ERROR_CODE"
}
```

---

## 2. 인증 API

### 2.1 회원가입

```http
POST /api/auth/register
```

**Request Body**:
```json
{
  "user_type": "shipper",
  "company": "아로와랩스",
  "business_no": "123-45-67890",
  "name": "홍길동",
  "email": "user@example.com",
  "phone": "010-1234-5678",
  "password": "securePassword123!"
}
```

**Response (201)**:
```json
{
  "success": true,
  "message": "회원가입이 완료되었습니다.",
  "data": {
    "user_id": 1,
    "email": "user@example.com",
    "user_type": "shipper"
  }
}
```

### 2.2 로그인

```http
POST /api/auth/login
```

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securePassword123!"
}
```

**Response (200)**:
```json
{
  "success": true,
  "message": "로그인 성공",
  "data": {
    "id": 1,
    "user_type": "shipper",
    "company": "아로와랩스",
    "name": "홍길동",
    "email": "user@example.com"
  }
}
```

### 2.3 로그아웃

```http
POST /api/auth/logout
```

**Response (200)**:
```json
{
  "success": true,
  "message": "로그아웃 되었습니다."
}
```

---

## 3. 견적/비딩 API

### 3.1 포트 목록 조회

```http
GET /api/ports
```

**Query Parameters**:
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| search | string | N | 검색어 (2자 이상) |
| type | string | N | ocean/air/both |
| limit | number | N | 결과 수 (기본: 20) |

**Response (200)**:
```json
{
  "ports": [
    {
      "id": 1,
      "code": "KRPUS",
      "name": "BUSAN",
      "name_ko": "부산",
      "country": "KOREA",
      "country_code": "KR",
      "port_type": "ocean"
    },
    {
      "id": 2,
      "code": "KRICN",
      "name": "INCHEON",
      "name_ko": "인천",
      "country": "KOREA",
      "country_code": "KR",
      "port_type": "both"
    }
  ]
}
```

### 3.2 컨테이너 타입 조회

```http
GET /api/container-types
```

**Response (200)**:
```json
{
  "container_types": [
    {
      "id": 1,
      "code": "20DC",
      "name": "20 Dry Container",
      "abbreviation": "20'GP",
      "max_weight_kg": 21800,
      "max_cbm": 33.2
    },
    {
      "id": 2,
      "code": "40DC",
      "name": "40 Dry Container",
      "abbreviation": "40'GP",
      "max_weight_kg": 26680,
      "max_cbm": 67.7
    },
    {
      "id": 3,
      "code": "40HC",
      "name": "40 High Cube",
      "abbreviation": "40'HC",
      "max_weight_kg": 26460,
      "max_cbm": 76.3
    }
  ]
}
```

### 3.3 견적 요청 제출

```http
POST /api/quote/request
```

**Request Body**:
```json
{
  "trade_mode": "export",
  "shipping_type": "ocean",
  "load_type": "FCL",
  "pol": "KRPUS - BUSAN, KOREA",
  "pod": "NLRTM - ROTTERDAM, NETHERLANDS",
  "etd": "2026-01-25",
  "cargo_details": [
    {
      "container_type": "40HC",
      "qty": 2,
      "gross_weight": 25000
    }
  ],
  "export_cc": false,
  "import_cc": false,
  "ship_insurance": false,
  "pickup_required": false,
  "pickup_addr": null,
  "delivery_required": false,
  "delivery_addr": null,
  "incoterms": "FOB",
  "invoice_value": 50000,
  "remark": "",
  "customer": {
    "company": "아로와랩스",
    "job_title": "물류팀장",
    "name": "홍길동",
    "email": "user@example.com",
    "phone": "010-1234-5678"
  }
}
```

**Response (201)**:
```json
{
  "success": true,
  "message": "견적 요청이 등록되었습니다.",
  "data": {
    "request_id": 25,
    "bidding_no": "EXSEA00025",
    "deadline": "2026-01-22T23:59:59",
    "pdf_url": "/api/quote/rfq/EXSEA00025/pdf"
  }
}
```

### 3.4 실시간 운임 조회 (Quick Quote)

```http
GET /api/freight/estimate
```

**Query Parameters**:
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| pol | string | Y | 출발지 코드 (KRPUS) |
| pod | string | Y | 도착지 코드 (NLRTM) |
| container_type | string | Y | 컨테이너 타입 (40HC) |
| quantity | number | Y | 수량 |
| shipping_type | string | Y | ocean/air |

**Response (200) - 견적 가능**:
```json
{
  "success": true,
  "available": true,
  "route": {
    "pol": "KRPUS - BUSAN, KOREA",
    "pod": "NLRTM - ROTTERDAM, NETHERLANDS"
  },
  "container": "40'HC",
  "quantity": 2,
  "freight_items": [
    {
      "code": "FRT",
      "name": "Ocean Freight",
      "unit_price": 2500,
      "currency": "USD",
      "unit": "CNTR",
      "quantity": 2,
      "amount": 5000
    },
    {
      "code": "BAF",
      "name": "Bunker Adjustment Factor",
      "unit_price": 350,
      "currency": "USD",
      "unit": "CNTR",
      "quantity": 2,
      "amount": 700
    },
    {
      "code": "THC",
      "name": "Terminal Handling Charge",
      "unit_price": 200000,
      "currency": "KRW",
      "unit": "CNTR",
      "quantity": 2,
      "amount": 400000
    },
    {
      "code": "DOC",
      "name": "Document Fee",
      "unit_price": 50000,
      "currency": "KRW",
      "unit": "B/L",
      "quantity": 1,
      "amount": 50000
    }
  ],
  "total_usd": 5700,
  "total_krw": 450000
}
```

**Response (200) - 견적 불가**:
```json
{
  "success": true,
  "available": false,
  "message": "해당 구간은 즉시 견적을 제공하지 않습니다.",
  "guide": "견적 요청을 통해 포워더 비딩을 진행해주세요."
}
```

### 3.5 비딩 목록 조회

```http
GET /api/bidding/list
```

**Query Parameters**:
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| status | string | N | open/closed/awarded/expired |
| shipping_type | string | N | ocean/air/truck |
| search | string | N | 비딩번호 검색 |
| page | number | N | 페이지 (기본: 1) |
| limit | number | N | 페이지당 수 (기본: 10) |

**Response (200)**:
```json
{
  "success": true,
  "total": 45,
  "page": 1,
  "pages": 5,
  "biddings": [
    {
      "id": 25,
      "bidding_no": "EXSEA00025",
      "status": "open",
      "pol": "KRPUS - BUSAN, KOREA",
      "pod": "NLRTM - ROTTERDAM, NETHERLANDS",
      "shipping_type": "ocean",
      "load_type": "FCL",
      "cargo_summary": "40'HC × 2",
      "etd": "2026-01-25",
      "deadline": "2026-01-22T23:59:59",
      "bid_count": 3,
      "customer_company": "아로와랩스",
      "created_at": "2026-01-15T10:30:00Z"
    }
  ]
}
```

### 3.6 비딩 상세 조회

```http
GET /api/bidding/{bidding_no}/detail
```

**Response (200)**:
```json
{
  "success": true,
  "bidding": {
    "id": 25,
    "bidding_no": "EXSEA00025",
    "status": "open",
    "deadline": "2026-01-22T23:59:59",
    "bid_count": 3,
    "quote_request": {
      "id": 25,
      "trade_mode": "export",
      "shipping_type": "ocean",
      "load_type": "FCL",
      "pol": "KRPUS - BUSAN, KOREA",
      "pod": "NLRTM - ROTTERDAM, NETHERLANDS",
      "etd": "2026-01-25",
      "incoterms": "FOB",
      "cargo_details": [
        {
          "container_type": "40'HC",
          "qty": 2,
          "gross_weight": 25000
        }
      ],
      "export_cc": false,
      "import_cc": false,
      "ship_insurance": false,
      "pickup_required": false,
      "pickup_addr": null,
      "delivery_required": false,
      "delivery_addr": null,
      "remark": ""
    },
    "customer": {
      "company": "아로와랩스",
      "name": "홍길동"
    }
  }
}
```

### 3.7 비딩 통계 조회

```http
GET /api/bidding/stats
```

**Response (200)**:
```json
{
  "success": true,
  "stats": {
    "total": 45,
    "open": 38,
    "closing_soon": 5,
    "awarded": 12,
    "expired": 3,
    "cancelled": 2
  }
}
```

### 3.8 RFQ PDF 다운로드

```http
GET /api/quote/rfq/{bidding_no}/pdf
```

**Response (200)**:
- Content-Type: `application/pdf`
- Content-Disposition: `attachment; filename="RFQ_EXSEA00025.pdf"`

---

## 4. 입찰 API

### 4.1 입찰 제출

```http
POST /api/bid/submit
```

**Request Body**:
```json
{
  "bidding_no": "EXSEA00025",
  "forwarder_id": 1,
  "freight_items": [
    {
      "code": "FRT",
      "name": "Ocean Freight",
      "currency": "USD",
      "unit_price": 2400,
      "unit": "CNTR",
      "quantity": 2,
      "amount": 4800,
      "tax_type": "영세"
    },
    {
      "code": "BAF",
      "name": "Bunker Adjustment Factor",
      "currency": "USD",
      "unit_price": 200,
      "unit": "CNTR",
      "quantity": 2,
      "amount": 400,
      "tax_type": "영세"
    },
    {
      "code": "THC",
      "name": "Terminal Handling Charge",
      "currency": "KRW",
      "unit_price": 180000,
      "unit": "CNTR",
      "quantity": 2,
      "amount": 360000,
      "tax_type": "과세"
    },
    {
      "code": "DOC",
      "name": "Document Fee",
      "currency": "KRW",
      "unit_price": 45000,
      "unit": "B/L",
      "quantity": 1,
      "amount": 45000,
      "tax_type": "과세"
    }
  ],
  "etd": "2026-01-25",
  "eta": "2026-02-10",
  "validity": "2026-01-30",
  "remark": "20년 이상 유럽 노선 운영 경험, 주 3회 직항 서비스"
}
```

**Response (201)**:
```json
{
  "success": true,
  "message": "입찰이 제출되었습니다.",
  "data": {
    "bid_id": 15,
    "bidding_no": "EXSEA00025",
    "total_usd": 5200,
    "total_krw": 405000,
    "submitted_at": "2026-01-18T14:30:00Z"
  }
}
```

### 4.2 입찰 수정

```http
PUT /api/bid/{bid_id}
```

**Request Body**: 입찰 제출과 동일

**Response (200)**:
```json
{
  "success": true,
  "message": "입찰이 수정되었습니다.",
  "data": {
    "bid_id": 15,
    "updated_at": "2026-01-18T15:00:00Z"
  }
}
```

### 4.3 비딩별 입찰 목록 조회

```http
GET /api/bidding/{bidding_no}/bids
```

**Response (200)**:
```json
{
  "success": true,
  "bidding_no": "EXSEA00025",
  "total_bids": 3,
  "bids": [
    {
      "id": 15,
      "forwarder": {
        "id": 1,
        "company": "글로벌로지스틱스",
        "rating": 4.5
      },
      "freight_items": [...],
      "total_usd": 5200,
      "total_krw": 405000,
      "etd": "2026-01-25",
      "eta": "2026-02-10",
      "validity": "2026-01-30",
      "remark": "20년 이상 유럽 노선 경험",
      "status": "submitted",
      "submitted_at": "2026-01-18T14:30:00Z"
    }
  ]
}
```

### 4.4 낙찰 처리

```http
POST /api/bidding/{bidding_no}/award/{bid_id}
```

**Response (200)**:
```json
{
  "success": true,
  "message": "낙찰 처리가 완료되었습니다.",
  "data": {
    "bidding_no": "EXSEA00025",
    "awarded_bid_id": 15,
    "awarded_forwarder": {
      "id": 1,
      "company": "글로벌로지스틱스"
    },
    "contract_no": "CON-2026-00001"
  }
}
```

### 4.5 비딩 마감

```http
POST /api/bidding/{bidding_no}/close
```

**Response (200)**:
```json
{
  "success": true,
  "message": "비딩이 마감되었습니다.",
  "data": {
    "bidding_no": "EXSEA00025",
    "status": "closed",
    "closed_at": "2026-01-20T10:00:00Z"
  }
}
```

---

## 5. 시장 데이터 API

### 5.1 경제 지표 조회

```http
GET /api/market/indices
```

**Query Parameters**:
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| type | string | Y | exchange/interest/inflation/gdp |
| itemCode | string | N | 세부 항목 (USD, EUR 등) |
| startDate | string | N | 시작일 (YYYYMMDD) |
| endDate | string | N | 종료일 (YYYYMMDD) |
| cycle | string | N | D(일)/W(주)/M(월) |

**Response (200)**:
```json
{
  "success": true,
  "type": "exchange",
  "item": "USD/KRW",
  "data": [
    {
      "date": "2026-01-19",
      "value": 1432.50,
      "change": 3.20,
      "change_percent": 0.22
    },
    {
      "date": "2026-01-18",
      "value": 1429.30,
      "change": -2.10,
      "change_percent": -0.15
    }
  ],
  "stats": {
    "latest": 1432.50,
    "high": 1450.20,
    "low": 1420.10,
    "avg": 1435.15,
    "std_dev": 8.32
  }
}
```

### 5.2 해운 지수 조회

```http
GET /api/shipping/indices
```

**Query Parameters**:
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| index_type | string | Y | BDI/SCFI/CCFI/all |
| days | number | N | 조회 기간 (기본: 7) |

**Response (200)**:
```json
{
  "success": true,
  "indices": {
    "BDI": {
      "name": "Baltic Dry Index",
      "latest": 1523,
      "change": -15,
      "change_percent": -0.98,
      "updated_at": "2026-01-19",
      "history": [
        {"date": "2026-01-19", "value": 1523},
        {"date": "2026-01-18", "value": 1538},
        {"date": "2026-01-17", "value": 1545}
      ]
    },
    "SCFI": {
      "name": "Shanghai Containerized Freight Index",
      "latest": 1845.32,
      "change": 23.15,
      "change_percent": 1.27,
      "updated_at": "2026-01-17",
      "history": [...]
    },
    "CCFI": {
      "name": "China Containerized Freight Index",
      "latest": 1156.78,
      "change": 8.92,
      "change_percent": 0.78,
      "updated_at": "2026-01-17",
      "history": [...]
    }
  }
}
```

---

## 6. 뉴스 API

### 6.1 뉴스 목록 조회

```http
GET /api/news/list
```

**Query Parameters**:
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| category | string | N | crisis/ocean/air/inland/economy/etc |
| news_type | string | N | KR/GLOBAL |
| is_crisis | boolean | N | 위기 뉴스만 |
| keyword | string | N | 키워드 검색 |
| limit | number | N | 결과 수 (기본: 20) |
| offset | number | N | 시작 위치 |

**Response (200)**:
```json
{
  "success": true,
  "total": 1234,
  "news": [
    {
      "id": 1,
      "title": "홍해 지역 선박 공격 위험 증가, 보험료 급등",
      "summary": "예멘 후티 반군의 상선 공격이 계속되면서 홍해를 통과하는 선박들의 전쟁 위험 보험료가 급등하고 있다...",
      "category": "crisis",
      "severity": "severe",
      "source": "Lloyd's List",
      "url": "https://...",
      "image_url": "https://...",
      "location": {
        "name": "Red Sea",
        "country": "Yemen",
        "lat": 20.5,
        "lng": 38.5
      },
      "news_type": "GLOBAL",
      "published_at": "2026-01-19T10:30:00Z"
    }
  ]
}
```

### 6.2 위기 경고 조회

```http
GET /api/news/alerts
```

**Response (200)**:
```json
{
  "success": true,
  "alerts": [
    {
      "id": 1,
      "title": "홍해 지역 선박 공격 위험",
      "severity": "severe",
      "category": "crisis",
      "region": "Red Sea",
      "description": "후티 반군 공격 지속",
      "published_at": "2026-01-19T10:30:00Z"
    },
    {
      "id": 2,
      "title": "항만 파업 예고 - 부산항",
      "severity": "warning",
      "category": "inland",
      "region": "Busan, Korea",
      "description": "2월 1일 파업 예정",
      "published_at": "2026-01-18T15:00:00Z"
    }
  ]
}
```

### 6.3 키워드 분석

```http
GET /api/news/keywords
```

**Query Parameters**:
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| period | string | N | 24h/7d/30d (기본: 24h) |
| limit | number | N | 결과 수 (기본: 50) |

**Response (200)**:
```json
{
  "success": true,
  "period": "24h",
  "keywords": [
    {"word": "운임", "count": 156},
    {"word": "컨테이너", "count": 132},
    {"word": "홍해", "count": 98},
    {"word": "파업", "count": 45},
    {"word": "수에즈", "count": 42}
  ]
}
```

### 6.4 뉴스 통계

```http
GET /api/news/stats
```

**Response (200)**:
```json
{
  "success": true,
  "stats": {
    "total_24h": 1234,
    "by_region": {
      "KR": 456,
      "GLOBAL": 778
    },
    "by_category": {
      "crisis": 89,
      "ocean": 345,
      "air": 210,
      "inland": 156,
      "economy": 298,
      "etc": 136
    },
    "last_updated": "2026-01-19T11:00:00Z"
  }
}
```

---

## 7. AI API

### 7.1 AI 채팅

```http
POST /api/ai/chat
```

**Request Body**:
```json
{
  "session_id": "session_1705654321_abc123",
  "message": "부산에서 로테르담 40HC 운임 알려줘",
  "user_context": {
    "user_id": 1,
    "user_type": "shipper",
    "company": "아로와랩스",
    "name": "홍길동",
    "email": "user@example.com"
  }
}
```

**Response (200)**:
```json
{
  "success": true,
  "message": "📊 **해상 운임 조회 결과**\n\n구간: KRPUS(부산) → NLRTM(로테르담)\n컨테이너: 40'HC\n\n| 항목 | 금액 |\n|------|------|\n| 해상운임 (FRT) | $2,500 |\n| 유류할증료 (BAF) | $350 |\n| 터미널비 (THC) | ₩200,000 |\n| 서류비 (DOC) | ₩50,000 |\n\n**총액: $2,850 + ₩250,000**\n\n💡 견적 요청을 진행하시겠어요?",
  "tool_used": ["get_ocean_rates"],
  "navigation": null,
  "quote_data": {
    "pol": "KRPUS",
    "pod": "NLRTM",
    "container_type": "40HC",
    "rates": [...]
  }
}
```

### 7.2 대화 이력 조회

```http
GET /api/ai/history
```

**Query Parameters**:
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| session_id | string | Y | 세션 ID |
| limit | number | N | 최대 건수 (기본: 50) |

**Response (200)**:
```json
{
  "success": true,
  "session_id": "session_1705654321_abc123",
  "history": [
    {
      "id": 1,
      "role": "user",
      "content": "부산에서 로테르담 운임 알려줘",
      "timestamp": "2026-01-19T10:30:00Z"
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "📊 해상 운임 조회 결과...",
      "tool_used": ["get_ocean_rates"],
      "timestamp": "2026-01-19T10:30:02Z"
    }
  ]
}
```

---

## 8. 에러 코드

### 8.1 HTTP 상태 코드

| 코드 | 설명 |
|------|------|
| **200** | 성공 |
| **201** | 생성 성공 |
| **400** | 잘못된 요청 |
| **401** | 인증 필요 |
| **403** | 권한 없음 |
| **404** | 리소스 없음 |
| **409** | 충돌 (중복 등) |
| **500** | 서버 오류 |

### 8.2 비즈니스 에러 코드

| 코드 | 설명 | HTTP |
|------|------|------|
| `AUTH_REQUIRED` | 로그인 필요 | 401 |
| `AUTH_INVALID` | 인증 실패 | 401 |
| `PERMISSION_DENIED` | 권한 없음 | 403 |
| `NOT_FOUND` | 리소스 없음 | 404 |
| `DUPLICATE_EMAIL` | 이메일 중복 | 409 |
| `BIDDING_CLOSED` | 비딩 마감됨 | 400 |
| `ALREADY_AWARDED` | 이미 낙찰됨 | 400 |
| `INVALID_DATE` | 유효하지 않은 날짜 | 400 |
| `VALIDATION_ERROR` | 입력값 검증 실패 | 400 |

### 8.3 에러 응답 예시

```json
{
  "success": false,
  "message": "비딩이 이미 마감되었습니다.",
  "error_code": "BIDDING_CLOSED",
  "details": {
    "bidding_no": "EXSEA00025",
    "closed_at": "2026-01-22T23:59:59Z"
  }
}
```

---

## 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
|------|------|--------|-----------|
| 1.0.0 | 2026-01-19 | - | 초기 작성 |
