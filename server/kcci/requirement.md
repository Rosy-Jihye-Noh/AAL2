## 5.1 KCCI 종합지수 시계열

* 형태: Line Chart
* X축: 주차(Week)
* Y축: KCCI Index

## 5.2 항로별 KCCI 비교

* 형태: Multi-line Chart
* 기본값: KCCI

## 5.3 UI 표시 정보

### 상단 섹션 표기

* index name: KCCI(Korea Container Freight Index)
* index 값 (선택된 기간의 시작값 대비 금일 날짜의 증감액, 증감률)
* source: KOBC
* Presentation Frequency**:** Weekly (Every Monday at 2 PM)
* Last Updated**:** [Date/Time]
* from StartDate to EndDate 기간 중에 최고점, 최저점, 평균값

### 중간 그래프 표기

#### 조회 기간

* 빠른 기간 설정(1w, 1m, 6m, 1y, max 선택 가능)
  * 페이지 최초 랜딩 시
    * 사용자 로컬 시간 기준 오늘 날짜를 EndDate로 설정

#### 조회 기간에 따른 x축 표기 기준

| 기간                       | X축 표시 방식                                                                  | 라벨 형식 |
| -------------------------- | ------------------------------------------------------------------------------ | --------- |
| **1W (7일)**         | 매 발표일자 표시                                                               | MM-DD     |
| **1M (8~31일)**      | 매 발표일자 표시                                                               | MM-DD     |
| **6M (32~93일)**     | 각 월 표시                                                                     | MM        |
| **1Y (94~365일)**    | 각 월 표시``(현재 속한 월 포함 12달 앞의 달의 첫날을 start date로 설정) | MM        |
| **1Y 초과~(366일~)** | 연시                                                                           | YYYY      |

#### 여러 지수 선택 시 y축 표기 기준

* 복수 지수 선택 시, 차트의 Y축은 선택 기간 시작 시점을 0%로 한 상대적 변화율(%)로 표시
* 예시

| 날짜 | 지수 | Y값 |
| ---- | ---- | --- |

| 날짜   | 지수  | Y값    |
| ------ | ----- | ------ |
| 시작일 | 1,300 | 0.0%   |
| 25-01  | 1,320 | +1.54% |
| 25-08  | 1,310 | +0.77% |
| 25-15  | 1,280 | -1.54% |

#### 그래프 마우스 오버시 표기 기준

* 차트 Hover 시, 마우스 위치는 X축 기준 가장 가까운 실제 데이터 포인트 날짜로 snap되며,
  해당 날짜에 대해 X축 crosshair(점선)를 표시
* Tooltip은 데이터가 존재하는 날짜에서만 활성화되며,
  선택된 모든 지수 값과 선택 기간 시작 대비 변화율(%)을 단일 Tooltip에 표시

##### 세부 요청사항

1. 기본 원칙 (Interaction Philosophy)

> 사용자는 **임의의 위치**가 아니라
> **실제 데이터가 존재하는 시점**에서만
> 정확한 값을 확인할 수 있어야 한다.

2. Hover 트리거 기준

2.1 Hover 활성 조건

* 마우스 오버 시,
  * **가장 가까운 데이터 포인트(Date Index)** 기준으로 반응
  * X축 상의 **실제 데이터가 있는 날짜에서만 활성화**

❌ 자유 이동 Hover (Continuous Hover) 미사용
❌ 데이터 없는 날짜 생성 금지

---

3. Crosshair(점선) 표시 규칙

3.1 표시 요소

Hover 시 다음 요소를 표시한다:

* **세로 점선 (X-axis crosshair)**

3.2 표시 조건

| 항목     | 규칙                     |
| -------- | ------------------------ |
| X축 점선 | 선택된 날짜 기준         |
| 색상     | 연한 회색 (#DADCE0 수준) |
| 스타일   | dashed                   |

---

4. 포인트(Point) 처리 규칙

4.1 포인트 활성화

* Hover 시
  * **선택된 날짜의 실제 데이터 포인트에만 snap**
  * 각 통화의 point는:
    * Hover 중일 때만 표시
    * 기본 상태에서는 숨김

4.2 포인트 스타일

| 상태    | 스타일                |
| ------- | --------------------- |
| Default | Hidden                |
| Hover   | Circle (radius 3~4px) |
| Active  | Filled                |

---

5. Tooltip 표시 규칙

5.1 Tooltip 트리거

* Hover가 **유효한 데이터 포인트 날짜에 snap 되었을 때만 표시**
* 여러 통화 선택 시:
  * **단일 Tooltip 내에 모두 표시**

---

5.2 Tooltip 구성

상단

* 📅 **날짜 표시**
  * 예: `2025-12-15`
  * 포맷: 사용자 로컬 타임존

본문 (항로 별 Row)

각 선택된 항로에 대해 다음 정보 표시:

| 항목    | 설명                      |
| ------- | ------------------------- |
| 항로명  | 항로 영어 코드(예: KMDI)  |
| 현재 값 | 해당 날짜의 값            |
| 변화율  | 기간 시작 대비 증감률 (%) |
| 색상    | 라인 색상과 동일          |

예시:

`<span data-testid="renderer-code-block-line-1" data-ds--code--row="" class=""><span class="">Dec 15, 2025 </span></span><span data-testid="renderer-code-block-line-2" data-ds--code--row="" class="">KCCI   1,805   -0.06% ->KCCI는 디폴트 </span><span data-testid="renderer-code-block-line-3" data-ds--code--row="" class="">KMDI   3,905   +3.17% </span><span data-testid="renderer-code-block-line-4" data-ds--code--row="" class="">KNEI   2,767   +2.29%% </span><span data-testid="renderer-code-block-line-5" data-ds--code--row="" class=""></span>`

---

6. 변화율 계산 기준 (Tooltip)

> Tooltip에 표시되는 변화율은
> **선택된 기간의 시작값 대비 해당 날짜의 상대 변화율**이다.

`<span data-testid="renderer-code-block-line-1" data-ds--code--row="" class=""><span class="">Change (%) = (Value(t) - Value(start)) / Value(start) × 100 </span></span><span data-testid="renderer-code-block-line-2" data-ds--code--row="" class=""></span>`

❌ 일별 증감률 누적 사용 금지

---

7. X축 날짜 표시 규칙

* Tooltip과 함께
  * X축 하단에 **해당 날짜 라벨 강조**
* 비활성 날짜는 표시하지 않음

---

8. UX 제약 조건 (중요)

* Tooltip은 **1개만 표시**
* Hover 이동 시:
  * 날짜 단위로만 이동 (snap)
* 모바일:
  * Tap → 동일 동작
  * 두 번째 Tap → 해제
