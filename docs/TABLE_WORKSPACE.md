# Table Workspace - Teable 통합 3-Pane UI

## 개요

DeerFlow에 "Table" 메뉴를 추가하여 Teable 데이터베이스를 3-pane 구조로 사용할 수 있게 한다.
사용자는 자연어로 테이블 CRUD를 수행하고, 변경 사항이 실시간으로 캔버스에 반영된다.

### 핵심 설계 원칙

- **독립 라우트 방식**: 기존 채팅/아티팩트 코드를 수정하지 않아 upstream merge conflict 최소화
- **전용 에이전트**: `teable-agent`로 도구/스킬/메모리를 Teable에 최적화
- **확장 가능 패턴**: 향후 Twenty, Vault 등 다른 서비스에 동일 패턴 적용 가능

## 아키텍처

### 화면 구조 (3-Pane Layout)

```
┌──────────────────────────────────────────────────┐
│ Sidebar │  Chat (30%)  │ Tables (20%) │ Canvas (50%) │
│         │              │              │              │
│ Chats   │  자연어로     │  TableList   │  Teable      │
│ Agents  │  테이블       │  - 투자계약  │  iframe      │
│ ▶Table  │  CRUD 요청   │  - 회의록    │  (embed)     │
│         │              │  - 일정      │              │
│         │  InputBox    │              │              │
└──────────────────────────────────────────────────┘
```

### 데이터 흐름

```
1. 페이지 로드
   → GET /api/teable/config → base_id 획득
   → GET /api/teable/bases/{base_id}/tables → 테이블 목록 표시

2. 테이블 선택
   → GET /api/teable/tables/{table_id}/share-view → embed URL 획득
   → iframe에 embed URL 렌더링 (실시간 WebSocket 자동 업데이트)

3. 자연어 CRUD (왼쪽 채팅)
   → useThreadStream (agent_name: "teable-agent")
   → LangGraph Agent (teable 도구만 활성화)
   → teable_create/update/delete_records 도구 호출
   → Teable API 변경 → iframe WebSocket으로 자동 반영
```

## 전용 에이전트: teable-agent

기존 DeerFlow Agent 시스템을 활용하여 Table 전용 에이전트를 구성한다.

### 왜 전용 에이전트인가?

| 항목 | 기본 lead_agent | teable-agent |
|---|---|---|
| 활성 도구 | ~20개 (bash, web_search 등 전부) | 9개 (teable_* 전용) |
| 시스템 프롬프트 | 범용 | Teable 전문가 |
| 메모리 | 전역 공유 | 에이전트별 독립 |
| 스킬 | 전부 활성 | teable-data만 |

### 파일 구조

```
agents/teable-agent/
├── config.yaml    # 도구/스킬 필터링 설정
└── SOUL.md        # Teable 전문가 시스템 프롬프트
```

### config.yaml

```yaml
name: teable-agent
description: Teable 데이터베이스 관리 전문 에이전트
tool_groups:
  - teable
skills:
  - teable-data
```

### 프론트엔드 연동

```tsx
// table-workspace.tsx
const [thread, sendMessage] = useThreadStream({
  context: { ...settings.context, agent_name: "teable-agent" },
});
```

`agent_name`을 context에 전달하면, 백엔드의 `make_lead_agent()`가 자동으로:
- `agent_config.tool_groups` → Teable 도구만 로딩
- `agent_config.skills` → teable-data 스킬만 활성화
- `load_agent_soul("teable-agent")` → SOUL.md를 시스템 프롬프트에 주입
- `MemoryMiddleware(agent_name="teable-agent")` → 에이전트별 독립 메모리

## Backend 변경

### 1. Gateway Teable 라우터

**파일**: `backend/app/gateway/routers/teable.py`

에이전트를 거치지 않고 Teable API를 직접 호출하여 빠른 응답(~100ms)을 제공한다.

| 엔드포인트 | 설명 |
|---|---|
| `GET /api/teable/config` | 기본 base_id, public_url 반환 |
| `GET /api/teable/bases/{base_id}/tables` | 테이블 목록 |
| `GET /api/teable/tables/{table_id}/share-view` | 공유 뷰 URL 생성/반환 |

### 2. 환경변수

```env
TEABLE_DEFAULT_BASE_ID=bseGyJ75YRKdhTfy2Tj
```

### 3. 등록

`backend/app/gateway/app.py`에 teable 라우터 추가.

## Frontend 변경

### 1. 사이드바 메뉴

`workspace-nav-chat-list.tsx`에 "Table" 메뉴 항목 추가.

### 2. i18n

`en-US.ts`, `zh-CN.ts`, `types.ts`에 sidebar.table 키 추가.

### 3. Teable API 레이어

```
frontend/src/core/teable/
├── types.ts    # TeableTable, TeableConfig, TeableShareView
├── api.ts      # fetchTeableConfig, fetchTeableTables, fetchTeableShareView
├── hooks.ts    # useTeableConfig, useTeableTables, useTeableShareView (TanStack Query)
└── index.ts    # re-export
```

### 4. Table 라우트 & 컴포넌트

```
frontend/src/app/workspace/table/
├── layout.tsx                    # Provider 래핑
├── page.tsx                      # 신규 스레드 생성
└── [thread_id]/
    ├── layout.tsx
    └── page.tsx                  # 기존 스레드 이어서 진행

frontend/src/components/workspace/table/
├── table-workspace.tsx           # 3-pane ResizablePanel 레이아웃 (핵심)
├── table-resource-list.tsx       # 가운데 패널: 테이블 목록
├── table-canvas.tsx              # 오른쪽 패널: iframe embed
└── index.ts
```

## Upstream 충돌 영향도

| 파일 | 변경 | Conflict 리스크 |
|---|---|---|
| `workspace-nav-chat-list.tsx` | 메뉴 1개 추가 | 낮음 |
| `i18n/locales/*.ts` | 키 1개 추가 | 낮음 |
| `backend/app/gateway/app.py` | router 2줄 추가 | 낮음 |
| 신규 파일 ~15개 | - | 없음 |

## 향후 확장 패턴

| 메뉴 | 라우트 | 전용 에이전트 | 도구 |
|---|---|---|---|
| Table | `/workspace/table` | `teable-agent` | teable_* |
| CRM | `/workspace/crm` | `twenty-agent` | twenty_* |
| Vault | `/workspace/vault` | `vault-agent` | vault_* |

각 서비스 = 독립 라우트(3-pane) + 전용 에이전트(도구/스킬/프롬프트 최적화).
