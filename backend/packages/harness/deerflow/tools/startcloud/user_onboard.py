"""User onboarding via Keycloak Admin REST API."""

import json
import os
import ssl
import urllib.request
import urllib.error
from langchain_core.tools import tool


KEYCLOAK_URL = os.environ.get("KEYCLOAK_ADMIN_URL", "https://dev.drfuturewalker.com:8445")
REALM = os.environ.get("KEYCLOAK_REALM", "startcloud")
ADMIN_USER = os.environ.get("KEYCLOAK_ADMIN_USER", "admin")
ADMIN_PASS = os.environ.get("KEYCLOAK_ADMIN_PASSWORD", "admin")

# Internal Caddy uses self-signed certs — skip verification for service-to-service calls
_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode = ssl.CERT_NONE


def _get_admin_token() -> str:
    """Get Keycloak admin access token."""
    url = f"{KEYCLOAK_URL}/realms/master/protocol/openid-connect/token"
    data = (
        f"grant_type=password"
        f"&client_id=admin-cli"
        f"&username={ADMIN_USER}"
        f"&password={ADMIN_PASS}"
    ).encode("utf-8")

    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with urllib.request.urlopen(req, timeout=10, context=_ssl_ctx) as resp:
            body = json.loads(resp.read())
            return body["access_token"]
    except Exception as e:
        raise RuntimeError(f"Failed to get admin token: {e}")


def _keycloak_api(method: str, path: str, token: str, body: dict = None) -> tuple[int, dict | str]:
    """Make a Keycloak Admin REST API call."""
    url = f"{KEYCLOAK_URL}/admin/realms/{REALM}{path}"
    data = json.dumps(body).encode("utf-8") if body else None

    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=15, context=_ssl_ctx) as resp:
            content = resp.read().decode("utf-8")
            try:
                return resp.status, json.loads(content) if content else {}
            except json.JSONDecodeError:
                return resp.status, content
    except urllib.error.HTTPError as e:
        content = e.read().decode("utf-8") if e.fp else ""
        return e.code, content


@tool
def user_onboard(email: str, first_name: str, last_name: str, role: str = "member", temporary_password: str = "Welcome123!") -> str:
    """Onboard a new team member to Start-Cloud. Call this tool ONCE with all required parameters.

    Creates a user account in Keycloak with SSO access to all connected services
    (Vaultwarden, NocoDB, Twenty CRM). After calling this tool, present the result
    to the user immediately. Do NOT call this tool again.

    For Korean names like "김사라": last_name="김", first_name="사라".
    For English names like "John Kim": first_name="John", last_name="Kim".

    Args:
        email: User's email address (required, e.g. "sara.kim@company.com")
        first_name: User's given name (required, e.g. "사라" or "Sara")
        last_name: User's family name (required, e.g. "김" or "Kim")
        role: Role to assign - 'admin' or 'member' (default: member)
        temporary_password: Temporary password for first login (default: Welcome123!)
    """
    results = []

    # Step 1: Get admin token
    try:
        token = _get_admin_token()
        results.append("✅ Keycloak admin authentication successful")
    except Exception as e:
        return f"❌ Failed to authenticate with Keycloak: {e}"

    # Step 2: Create user
    user_payload = {
        "username": email,
        "email": email,
        "firstName": first_name,
        "lastName": last_name,
        "enabled": True,
        "emailVerified": True,
        "credentials": [
            {
                "type": "password",
                "value": temporary_password,
                "temporary": True,
            }
        ],
        "realmRoles": [role],
    }

    status, resp = _keycloak_api("POST", "/users", token, user_payload)
    if status == 201:
        results.append(f"✅ User '{email}' created in Keycloak")
    elif status == 409:
        results.append(f"⚠️ User '{email}' already exists in Keycloak")
    else:
        return f"❌ Failed to create user (status {status}): {resp}"

    # Step 3: Get user ID for role assignment
    status, users = _keycloak_api("GET", f"/users?email={email}", token)
    if status == 200 and isinstance(users, list) and len(users) > 0:
        user_id = users[0]["id"]
        results.append(f"✅ User ID: {user_id}")
    else:
        results.append("⚠️ Could not retrieve user ID for role assignment")
        user_id = None

    # Step 4: Assign role
    if user_id:
        # Get realm role
        status, roles = _keycloak_api("GET", f"/roles/{role}", token)
        if status == 200 and isinstance(roles, dict):
            role_id = roles.get("id")
            role_payload = [{"id": role_id, "name": role}]
            status, _ = _keycloak_api("POST", f"/users/{user_id}/role-mappings/realm", token, role_payload)
            if status in (200, 204):
                results.append(f"✅ Role '{role}' assigned")
            else:
                results.append(f"⚠️ Role assignment returned status {status}")
        else:
            results.append(f"⚠️ Role '{role}' not found in realm")

    # Step 5: Summary
    results.append("")
    results.append("=== Onboarding Summary ===")
    results.append(f"Name:     {first_name} {last_name}")
    results.append(f"Email:    {email}")
    results.append(f"Role:     {role}")
    results.append(f"Password: {temporary_password} (temporary, must change on first login)")
    results.append("")
    results.append("Services accessible via SSO:")
    results.append(f"  🔑 Vaultwarden (Passwords): https://dev.drfuturewalker.com:8443")
    results.append(f"  📊 Teable (Spreadsheets):    https://dev.drfuturewalker.com:8444")
    results.append(f"  💼 Twenty CRM:               https://dev.drfuturewalker.com:8446")
    results.append("")
    results.append(f"SSO Login: https://dev.drfuturewalker.com:8445/realms/startcloud/account")
    results.append(f"The user can log in to any service using their email and temporary password.")

    return "\n".join(results)
