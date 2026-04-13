"""Teable proxy API for fast table listing and view sharing.

Provides direct Teable API access without going through the agent,
enabling fast (~100ms) table list loading for the Table workspace.
Also handles auto-provisioning of the teable-agent.
"""

import json
import logging
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import yaml
from fastapi import APIRouter, HTTPException

from deerflow.config.agents_config import load_agent_config
from deerflow.config.paths import get_paths

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/teable", tags=["teable"])

# ---------------------------------------------------------------------------
# Teable HTTP helpers (inlined to avoid startcloud/__init__.py import issues)
# ---------------------------------------------------------------------------


def _load_teable_env():
    """Load TEABLE_ env vars from parent .env if not already set."""
    if os.environ.get("TEABLE_API_TOKEN"):
        return
    candidate = Path(__file__).resolve()
    for _ in range(12):
        candidate = candidate.parent
        env_file = candidate / ".env"
        if env_file.is_file():
            try:
                for line in env_file.read_text().splitlines():
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, _, value = line.partition("=")
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key.startswith("TEABLE_") and key not in os.environ:
                            os.environ[key] = value
            except OSError:
                pass
            if os.environ.get("TEABLE_API_TOKEN"):
                break


_load_teable_env()

TEABLE_API_URL = os.environ.get("TEABLE_API_URL", "http://localhost:8002")
TEABLE_API_TOKEN = os.environ.get("TEABLE_API_TOKEN", "")
TEABLE_PUBLIC_URL = os.environ.get("TEABLE_PUBLIC_URL", "")
TEABLE_DEFAULT_BASE_ID = os.environ.get("TEABLE_DEFAULT_BASE_ID", "")


def _teable_request(method, path, body=None, params=None, timeout=30):
    url = f"{TEABLE_API_URL}/api{path}"
    if params:
        qs = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None}, doseq=True)
        if qs:
            url += f"?{qs}"
    data = json.dumps(body).encode() if body else None
    headers = {"Authorization": f"Bearer {TEABLE_API_TOKEN}", "Content-Type": "application/json"}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()[:500] if e.fp else ""
        return f"HTTP {e.code}: {err_body}"
    except Exception as e:
        return f"Error: {e}"


def _check_configured():
    if not TEABLE_API_TOKEN:
        return "TEABLE_API_TOKEN not configured"
    return None


# ---------------------------------------------------------------------------
# Teable agent
# ---------------------------------------------------------------------------

TEABLE_AGENT_NAME = "teable-agent"
TEABLE_AGENT_CONFIG = {
    "name": TEABLE_AGENT_NAME,
    "description": "Teable 데이터베이스 관리 전문 에이전트",
    "tool_groups": ["teable"],
    "skills": ["teable-data"],
}
TEABLE_AGENT_SOUL = f"""# Teable 데이터베이스 전문 에이전트

너는 Teable 데이터베이스 관리 전문가다. 사용자의 자연어 요청을 Teable API 도구로 변환하여 실행한다.

## 기본 Base 설정
- **기본 Base ID: {TEABLE_DEFAULT_BASE_ID or "bseGyJ75YRKdhTfy2Tj"}**
- 사용자가 테이블 이름만 말하면, 반드시 이 Base ID로 `teable_list_spaces(base_id="{TEABLE_DEFAULT_BASE_ID or "bseGyJ75YRKdhTfy2Tj"}")` 를 호출하여 테이블을 찾아라
- 절대로 다른 Base의 테이블을 사용하지 마라. 동일한 이름의 테이블이 여러 Base에 있을 수 있다

## 핵심 원칙
- 사용자가 "테이블"이라고 하면 Teable 데이터베이스를 의미한다
- 데이터를 조회하거나 보여달라고 하면 `teable_show_view`로 오른쪽 패널에 표시하라
- 데이터 삭제 전 반드시 사용자에게 확인을 요청하라
- 10건 이상 일괄 수정 시 미리보기를 먼저 보여주라
- 한국어로 응답하라

## 작업 순서 (권장)
1. `teable_list_spaces(base_id="{TEABLE_DEFAULT_BASE_ID or "bseGyJ75YRKdhTfy2Tj"}")` → 대상 테이블 찾기 (반드시 기본 Base ID 사용)
2. `teable_get_fields(table_id)` → 스키마 파악
3. `teable_show_view(table_id)` → 오른쪽 패널에 표시
4. CRUD 도구로 데이터 작업
5. → iframe이 WebSocket으로 자동 업데이트
"""


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.get("/config")
async def get_config() -> dict:
    """Return Teable configuration for the frontend."""
    err = _check_configured()
    if err:
        raise HTTPException(status_code=503, detail=err)
    return {
        "base_id": TEABLE_DEFAULT_BASE_ID,
        "public_url": TEABLE_PUBLIC_URL or TEABLE_API_URL,
    }


@router.get("/spaces")
async def list_spaces() -> dict:
    """List all Teable spaces."""
    err = _check_configured()
    if err:
        raise HTTPException(status_code=503, detail=err)

    result = _teable_request("GET", "/space")
    if isinstance(result, str):
        raise HTTPException(status_code=502, detail=result)

    spaces = result if isinstance(result, list) else result.get("spaces", result)
    return {"spaces": spaces or []}


@router.get("/spaces/{space_id}/bases")
async def list_bases(space_id: str) -> dict:
    """List all bases in a space."""
    err = _check_configured()
    if err:
        raise HTTPException(status_code=503, detail=err)

    result = _teable_request("GET", f"/space/{space_id}/base")
    if isinstance(result, str):
        raise HTTPException(status_code=502, detail=result)

    bases = result if isinstance(result, list) else result.get("bases", result)
    return {"bases": bases or []}


@router.get("/bases/{base_id}/tables")
async def list_tables(base_id: str) -> dict:
    """List all tables in a Teable base."""
    err = _check_configured()
    if err:
        raise HTTPException(status_code=503, detail=err)

    result = _teable_request("GET", f"/base/{base_id}/table")
    if isinstance(result, str):
        raise HTTPException(status_code=502, detail=result)

    tables = result if isinstance(result, list) else result.get("tables", result)
    return {"tables": tables or []}


@router.get("/tables/{table_id}/share-view")
async def get_share_view(table_id: str, view_type: str = "grid") -> dict:
    """Create a shared view for embedding and return the embed URL."""
    err = _check_configured()
    if err:
        raise HTTPException(status_code=503, detail=err)

    # 1. Create view
    view_body = {"name": f"Embed ({view_type})", "type": view_type}
    view_result = _teable_request("POST", f"/table/{table_id}/view", view_body)
    if isinstance(view_result, str):
        raise HTTPException(status_code=502, detail=f"View creation failed: {view_result}")

    view_id = view_result.get("id")
    if not view_id:
        raise HTTPException(status_code=502, detail="No view ID in response")

    # 2. Enable sharing
    share_result = _teable_request("POST", f"/table/{table_id}/view/{view_id}/enable-share", {})
    if isinstance(share_result, str):
        raise HTTPException(status_code=502, detail=f"Share enable failed: {share_result}")

    share_id = share_result.get("shareId") or view_result.get("shareId")
    if not share_id:
        raise HTTPException(status_code=502, detail="No share ID in response")

    # 3. Build embed URL
    public_url = (TEABLE_PUBLIC_URL or TEABLE_API_URL).rstrip("/")
    embed_url = f"{public_url}/share/{share_id}/view?embed=true&hideToolBar=true"

    return {
        "embed_url": embed_url,
        "view_id": view_id,
        "share_id": share_id,
    }


@router.post("/ensure-agent")
async def ensure_agent() -> dict:
    """Auto-provision the teable-agent if it doesn't exist."""
    try:
        existing = load_agent_config(TEABLE_AGENT_NAME)
        if existing:
            return {"status": "exists", "agent_name": TEABLE_AGENT_NAME}
    except (FileNotFoundError, ValueError):
        pass

    agent_dir = get_paths().agent_dir(TEABLE_AGENT_NAME)
    agent_dir.mkdir(parents=True, exist_ok=True)

    config_file = agent_dir / "config.yaml"
    with open(config_file, "w", encoding="utf-8") as f:
        yaml.dump(TEABLE_AGENT_CONFIG, f, default_flow_style=False, allow_unicode=True)

    soul_file = agent_dir / "SOUL.md"
    soul_file.write_text(TEABLE_AGENT_SOUL, encoding="utf-8")

    logger.info(f"Auto-provisioned teable-agent at {agent_dir}")
    return {"status": "created", "agent_name": TEABLE_AGENT_NAME}
