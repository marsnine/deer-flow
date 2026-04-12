# Teable 실시간 Split View CRUD 도구 + 스킬 구현 문서

**상태**: 구현 진행 중
**날짜**: 2026-04-11

---

## 개요

DeerFlow AI 대화창(왼쪽)에서 자연어로 Teable 데이터를 CRUD하면, 오른쪽 아티팩트 패널에서 Teable 테이블 뷰가 **실시간으로 반영**되는 기능.

**핵심 메커니즘**: Agent가 Teable API로 데이터 수정 → Teable의 WebSocket(ShareDB)이 변경사항을 iframe에 자동 푸시 → 새로고침 없이 실시간 반영

---

## 아키텍처

```
┌──────────────────────────────────────────────────────────────┐
│ DeerFlow Frontend (Next.js)                                  │
│ ┌─────────────────────┬─────────┬──────────────────────────┐ │
│ │   Chat Panel (60%)  │ Resize  │  Artifact Panel (40%)    │ │
│ │                     │ Handle  │                          │ │
│ │  "서울 고객 보여줘"  │   ↔    │  ┌────────────────────┐  │ │
│ │                     │         │  │  Teable Iframe      │  │ │
│ │  Agent: 필터 적용    │         │  │  (Share View)       │  │ │
│ │  완료! 23건 조회됨   │         │  │  실시간 WebSocket   │  │ │
│ │                     │         │  │  ← API 변경 자동반영 │  │ │
│ │  "김사라 추가해줘"   │         │  └────────────────────┘  │ │
│ └─────────────────────┴─────────┴──────────────────────────┘ │
└──────────────��────────────────────────────────────────────���──┘
         │                                      ▲
         │ teable_update_records()               │ WebSocket (ShareDB)
         ▼                                      │
┌─────────────────────────────────────────────────┐
│          Teable Server (localhost:8002)          │
│          PostgreSQL + WebSocket Gateway          │
└─────────────────────────────────────────────────┘
```

## 핵심 설계 결정: "Embed Artifact" 패턴

기존 DeerFlow 아티팩트 시스템의 `write-file:` prefix 패턴을 활용하여 `embed:` prefix를 추가.

| 대안 | 문제점 |
|---|---|
| HTML blob + 중첩 iframe | `sandbox="allow-scripts allow-forms"`에 `allow-same-origin` 없음 → WebSocket/Cookie 불가 |
| Gateway HTML 서빙 | XSS 방지를 위해 `Content-Disposition: attachment` 강제 → 다운로드됨 |
| sandbox 속성 전역 완화 | 보안 회귀 위험 |
| **embed: prefix (채택)** | **기존 패턴 준수, 보안 격리, 최소 변경** |

---

## 구현 파일 목록

### 새로 생성 (11개)

| # | 파일 | 역할 |
|---|---|---|
| 1 | `tools/startcloud/teable_client.py` | 공유 HTTP 클라이언트 |
| 2 | `tools/startcloud/teable_list_spaces.py` | Space → Base → Table 탐색 |
| 3 | `tools/startcloud/teable_get_fields.py` | 테이블 필드 구조 조회 |
| 4 | `tools/startcloud/teable_query_records.py` | 레코드 조회/검색/필터 |
| 5 | `tools/startcloud/teable_create_records.py` | 레코드 생성 |
| 6 | `tools/startcloud/teable_update_records.py` | 레코드 수정 |
| 7 | `tools/startcloud/teable_delete_records.py` | 레코드 삭제 |
| 8 | `tools/startcloud/teable_manage_table.py` | 테이블/필드 구조 관리 |
| 9 | `tools/startcloud/teable_aggregate.py` | 집계/SQL 쿼리 |
| 10 | `tools/startcloud/teable_show_view.py` | 뷰 생성 + 공유 + embed artifact 반환 |
| 11 | `agent/skills/custom/teable-data/SKILL.md` | LLM 스킬 프롬프트 |

### 수정 (7개)

| 파일 | 변경 |
|---|---|
| `tools/startcloud/__init__.py` | 9개 teable 도구 import |
| `agent/config.yaml` | `teable` tool_group + 9개 도구 등록 |
| `agent/extensions_config.json` | `teable-data` 스킬 enabled |
| `agent/backend/.deer-flow/agents/startcloud-admin/SOUL.md` | 데이터 관리 역할 추가 |
| `.env.sample` | `TEABLE_API_URL`, `TEABLE_API_TOKEN` 추가 |
| `agent/frontend/src/components/workspace/artifacts/artifact-file-detail.tsx` | embed: prefix 감지 + iframe 렌더링 |
| `agent/backend/packages/harness/deerflow/tools/startcloud/` | harness 복사 |

---

## 도구 설계 (9개)

### teable_list_spaces
- Space/Base/Table 계층 탐색
- API: `GET /api/space`, `GET /api/space/{id}/base`, `GET /api/base/{id}/table`

### teable_get_fields
- 테이블 필드 구조(이름, 타입, ID) 반환
- API: `GET /api/table/{tableId}/field`

### teable_query_records
- 필터/검색/정렬로 레코드 조회 (max 1000건)
- API: `GET /api/table/{tableId}/record`

### teable_create_records
- JSON 배열로 1~N개 레코드 생성
- API: `POST /api/table/{tableId}/record`

### teable_update_records
- recordId + fields로 레코드 수정
- API: `PATCH /api/table/{tableId}/record/{recordId}`

### teable_delete_records
- 쉼표 구분 record ID로 삭제
- API: `DELETE /api/table/{tableId}/record`

### teable_manage_table
- action 파라미터로 create_table/delete_table/create_field/update_field/delete_field 분기
- API: 각 action별 endpoint

### teable_aggregate
- row_count, field aggregation(sum/avg/min/max), SQL 쿼리
- API: `GET /api/table/{id}/aggregation/*`, `POST /api/base/{id}/table/{id}/sql-query`

### teable_show_view (핵심)
- 뷰 생성 → 공유 활성화 → `embed:` prefix artifact 등록
- `Command(update={"artifacts": ["embed:{url}"]})` 반환
- API: `POST /table/{tableId}/view`, `POST /table/{tableId}/view/{viewId}/enable-share`

---

## 프론트엔드 변경

`artifact-file-detail.tsx`에 `embed:` prefix 감지 로직 추가:
- `isEmbed` / `embedUrl` useMemo 추가
- embed일 때 직접 `<iframe src={embedUrl}>` 렌더링 (sandbox 제한 없음)
- 기존 코드는 `!isEmbed` 조건 분기로 영향 없음

---

## 환경 변수

```
TEABLE_API_URL=http://localhost:8002
TEABLE_API_TOKEN=your-teable-personal-access-token
TEABLE_PUBLIC_URL=https://teable.david.sprintsolo.dev
```

---

## 검증 방법

1. Teable Personal Access Token 발급
2. 프론트엔드 `embed:` iframe 렌더링 확인
3. 각 도구 Python 직접 호출 테스트
4. DeerFlow 채팅 E2E 테스트
5. 실시간 동기화 확인 (CRUD → iframe 자동 갱신)

---

**문서 버전**: 1.0
**최종 업데이트**: 2026-04-11
