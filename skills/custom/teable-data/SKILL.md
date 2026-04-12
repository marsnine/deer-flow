---
name: teable-data
description: Teable 데이터 CRUD 및 실시간 뷰 표시. 테이블, 데이터, 레코드, 필드, 스프레드시트, DB 관련 요청 시 활성화.
---

# Teable 데이터 관리

## 도구 목록
1. **teable_list_spaces** — Space/Base/Table 탐색
2. **teable_get_fields** — 테이블 스키마(필드 이름, 타입, ID) 조회
3. **teable_query_records** — 레코드 검색/필터/정렬
4. **teable_create_records** — 레코드 생성 (단건/복수)
5. **teable_update_records** — 레코드 수정
6. **teable_delete_records** — 레코드 삭제 (복구 불가)
7. **teable_manage_table** — 테이블/필드 구조 관리 (create_table, create_field, update_field, delete_field, delete_table)
8. **teable_aggregate** — 집계(row_count, sum, avg 등)/SQL 쿼리
9. **teable_show_view** — 오른쪽 패널에 Teable 뷰 실시간 표시 (iframe embed)

## 핵심 워크플로우

### 데이터 조회/수정 + 실시간 뷰 표시 (권장 패턴)
1. `teable_list_spaces()` → 대상 테이블 찾기
2. `teable_get_fields(table_id)` → 스키마 파악 (필드 이름, 타입, ID 확인)
3. `teable_show_view(table_id)` → 오른쪽 패널에 테이블 표시
4. `teable_query_records` / `teable_update_records` 등 → 데이터 CRUD
5. → iframe이 WebSocket으로 자동 업데이트되어 변경사항 즉시 반영

### 사용자가 "보여줘" / "표시해줘" 라고 하면
→ 반드시 `teable_show_view`를 호출하여 오른쪽 패널에 뷰를 표시하세요.

### 필터링된 뷰가 필요할 때
→ `teable_show_view(table_id, filter_json=...)` 으로 필터가 적용된 뷰를 생성하세요.

### 뷰 타입 변경
→ `teable_show_view(table_id, view_type="kanban")` 으로 다양한 뷰 타입을 보여줄 수 있습니다.
→ 사용 가능한 뷰 타입: grid, kanban, calendar, form, gallery

### 다단계 작업 (예: "3개월 미주문 고객 → 휴면 처리")
1. `teable_get_fields(table_id)` → 필드 ID 확인
2. `teable_query_records(table_id, filter_json=...)` → 대상 레코드 조회
3. `teable_update_records(table_id, updates_json=...)` → 일괄 수정
4. 결과 보고

## 안전 규칙

1. **삭제/대량수정 전 반드시 사용자 확인** — 사용자가 명시적으로 요청하기 전까지 레코드 삭제나 10건 이상 일괄 수정을 실행하지 마세요.
2. **10건 이상 일괄 수정 시 미리보기** — 대상 레코드 목록을 먼저 보여주고 확인을 받으세요.
3. **필터 결과 0건이면 즉시 알림** — "조건에 맞는 레코드가 없습니다"를 알려주세요.
4. **테이블/필드 삭제는 매우 신중하게** — 복구가 불가능합니다.

## 필터 문법 참고
```json
{
  "filterSet": [
    {"fieldId": "fldXXX", "operator": "is", "value": "서울"},
    {"fieldId": "fldYYY", "operator": "isGreater", "value": 100}
  ],
  "conjunction": "and"
}
```
연산자: is, isNot, contains, doesNotContain, isGreater, isLess, isGreaterEqual, isLessEqual, isEmpty, isNotEmpty, isAnyOf, isNoneOf

## 필드 타입 참고
- 쓰기가능: singleLineText, longText, number, singleSelect, multipleSelect, date, checkbox, rating, link, attachment, user
- 읽기전용: formula, createdTime, lastModifiedTime, rollup, autoNumber, createdBy, lastModifiedBy, lookup

## 언어
사용자가 사용하는 언어로 응답합니다 (기본 한국어).
