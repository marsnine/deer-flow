"""Health monitoring for the Start-Cloud service stack."""

import json
import subprocess
import os
import urllib.request
import urllib.error
from langchain_core.tools import tool


COMPOSE_DIR = os.environ.get("STARTCLOUD_COMPOSE_DIR", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "..")))

# teable/twenty were migrated to a separate server; deer-flow reaches them over
# the VPC via the URLs in .env (TEABLE_API_URL / TWENTY_API_URL), so they are no
# longer local docker-compose containers. For these the container check is
# skipped (remote=True) and only the HTTP health endpoint is reported.
TEABLE_URL = os.environ.get("TEABLE_API_URL", "http://localhost:8002")
TWENTY_URL = os.environ.get("TWENTY_API_URL", "http://localhost:3002")

SERVICES = {
    "vaultwarden": {"url": "http://localhost:8003", "health": "/alive", "description": "Password Manager", "remote": False},
    "teable": {"url": TEABLE_URL, "health": "/health", "description": "Spreadsheet / Database (Teable)", "remote": True},
    "twenty-server": {"url": TWENTY_URL, "health": "/healthz", "description": "CRM (Twenty)", "remote": True},
}


def _check_http(url: str, timeout: int = 5) -> tuple[bool, int]:
    """Check if an HTTP endpoint is responding."""
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return True, resp.status
    except urllib.error.HTTPError as e:
        return e.code < 500, e.code
    except Exception:
        return False, 0


def _get_container_status() -> dict:
    """Get Docker container statuses."""
    try:
        result = subprocess.run(
            ["docker", "compose", "-f", f"{COMPOSE_DIR}/docker-compose.yml", "ps", "--format", "json"],
            capture_output=True, text=True, timeout=15, cwd=COMPOSE_DIR,
        )
        containers = {}
        for line in result.stdout.strip().split("\n"):
            if line.strip():
                try:
                    c = json.loads(line)
                    containers[c.get("Service", c.get("Name", "unknown"))] = {
                        "state": c.get("State", "unknown"),
                        "status": c.get("Status", "unknown"),
                    }
                except json.JSONDecodeError:
                    pass
        return containers
    except Exception as e:
        return {"error": str(e)}


@tool
def stack_status() -> str:
    """Check the health status of all Start-Cloud services.

    Returns a summary showing:
    - Container status (running/stopped)
    - HTTP health check results
    - Service URLs for browser access
    """
    containers = _get_container_status()

    lines = ["=== Start-Cloud Service Status ===\n"]

    for svc_name, svc_info in SERVICES.items():
        http_ok, http_code = _check_http(f"{svc_info['url']}{svc_info['health']}")
        health_icon = "✅" if http_ok else "❌"

        lines.append(f"{health_icon} {svc_name}")
        lines.append(f"   Description: {svc_info['description']}")
        if svc_info.get("remote"):
            lines.append("   Location:    remote server (migrated, VPC)")
        else:
            container = containers.get(svc_name, {})
            c_state = container.get("state", "not found")
            c_status = container.get("status", "")
            lines.append(f"   Container:   {c_state} ({c_status})")
        lines.append(f"   HTTP:        {'OK' if http_ok else 'FAIL'} (status {http_code})")
        lines.append(f"   URL:         {svc_info['url']}")
        lines.append("")

    # Infrastructure services
    for infra in ["postgres", "redis"]:
        container = containers.get(infra, {})
        c_state = container.get("state", "not found")
        c_status = container.get("status", "")
        icon = "✅" if c_state == "running" else "❌"
        lines.append(f"{icon} {infra}")
        lines.append(f"   Container: {c_state} ({c_status})")
        lines.append("")

    return "\n".join(lines)
