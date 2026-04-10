"""User offboarding via Keycloak Admin REST API."""

import json
import os
import urllib.request
import urllib.error
from langchain_core.tools import tool

from .user_onboard import _get_admin_token, _keycloak_api


@tool
def user_offboard(email: str, disable_only: bool = True) -> str:
    """Offboard a team member from Start-Cloud.

    By default, disables the account (preserving data). Use disable_only=False to permanently delete.

    Args:
        email: Email of the user to offboard
        disable_only: If True, disable account. If False, permanently delete. (default: True)
    """
    results = []

    # Step 1: Auth
    try:
        token = _get_admin_token()
    except Exception as e:
        return f"❌ Failed to authenticate with Keycloak: {e}"

    # Step 2: Find user
    status, users = _keycloak_api("GET", f"/users?email={email}", token)
    if status != 200 or not isinstance(users, list) or len(users) == 0:
        return f"❌ User '{email}' not found in Keycloak"

    user = users[0]
    user_id = user["id"]
    name = f"{user.get('firstName', '')} {user.get('lastName', '')}".strip()

    if disable_only:
        # Disable account
        status, resp = _keycloak_api("PUT", f"/users/{user_id}", token, {"enabled": False})
        if status in (200, 204):
            results.append(f"✅ Account disabled for {name} ({email})")
            results.append("   User can no longer log in to any Start-Cloud service.")
            results.append("   Account data is preserved. Re-enable anytime.")
        else:
            return f"❌ Failed to disable account (status {status}): {resp}"
    else:
        # Permanent delete
        status, resp = _keycloak_api("DELETE", f"/users/{user_id}", token)
        if status in (200, 204):
            results.append(f"✅ Account permanently deleted for {name} ({email})")
            results.append("   ⚠️ This action is irreversible.")
        else:
            return f"❌ Failed to delete account (status {status}): {resp}"

    return "\n".join(results)
