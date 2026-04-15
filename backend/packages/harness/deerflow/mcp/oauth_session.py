"""Short-lived OAuth session store for authorization_code / PKCE flows.

Used by the Gateway `/api/mcp/oauth/start` and `/api/mcp/oauth/callback`
routes to correlate the popup-initiated authorization URL with the redirect
that delivers the `code`. State is persisted to per-session JSON files so
sessions survive short-lived process restarts during development.
"""

from __future__ import annotations

import base64
import hashlib
import json
import logging
import os
import secrets
import time
from dataclasses import asdict, dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_TTL_SECONDS = 600  # 10 minutes


def _default_sessions_dir() -> Path:
    base = os.getenv("DEER_FLOW_DATA_DIR")
    if base:
        return Path(base) / "oauth_sessions"
    # Mirror how ThreadDataMiddleware picks its base directory
    backend_dir = Path(__file__).resolve().parents[4]
    return backend_dir / ".deer-flow" / "oauth_sessions"


@dataclass
class OAuthSession:
    state: str
    preset_id: str
    code_verifier: str
    redirect_uri: str
    created_at: float

    def is_expired(self, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> bool:
        return (time.time() - self.created_at) > ttl_seconds


class OAuthSessionStore:
    """File-backed store for in-flight OAuth authorization_code sessions."""

    def __init__(self, directory: Path | None = None) -> None:
        self._dir = directory or _default_sessions_dir()
        self._dir.mkdir(parents=True, exist_ok=True)

    def create(self, preset_id: str, redirect_uri: str) -> OAuthSession:
        state = secrets.token_urlsafe(32)
        code_verifier = secrets.token_urlsafe(64)
        session = OAuthSession(
            state=state,
            preset_id=preset_id,
            code_verifier=code_verifier,
            redirect_uri=redirect_uri,
            created_at=time.time(),
        )
        path = self._path_for(state)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(session), f)
        os.chmod(path, 0o600)
        self._cleanup_expired()
        return session

    def pop(self, state: str) -> OAuthSession | None:
        path = self._path_for(state)
        if not path.exists():
            return None
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            session = OAuthSession(**data)
        except Exception as e:
            logger.warning(f"Failed to read oauth session {state}: {e}")
            path.unlink(missing_ok=True)
            return None
        finally:
            path.unlink(missing_ok=True)
        if session.is_expired():
            return None
        return session

    def _path_for(self, state: str) -> Path:
        # state is URL-safe base64, already filesystem-safe
        return self._dir / f"{state}.json"

    def _cleanup_expired(self) -> None:
        for path in self._dir.glob("*.json"):
            try:
                if time.time() - path.stat().st_mtime > DEFAULT_TTL_SECONDS:
                    path.unlink(missing_ok=True)
            except OSError:
                pass


def pkce_challenge(code_verifier: str) -> str:
    """Compute the S256 PKCE challenge for a given code_verifier."""
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


_default_store: OAuthSessionStore | None = None


def get_session_store() -> OAuthSessionStore:
    global _default_store
    if _default_store is None:
        _default_store = OAuthSessionStore()
    return _default_store
