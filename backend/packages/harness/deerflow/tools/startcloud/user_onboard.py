"""User onboarding — stub pending Phase 3 (Agent-as-IdP rewrite).

After Keycloak removal, users authenticate directly via Google OIDC.
Automated onboarding via Google Admin SDK + service APIs is planned for Phase 3.
"""

from langchain_core.tools import tool


@tool
def user_onboard(email: str, first_name: str, last_name: str, role: str = "member", temporary_password: str = "Welcome123!") -> str:
    """Onboard a new team member to Start-Cloud. Call this tool ONCE with all required parameters.

    Currently returns manual onboarding instructions since Keycloak has been removed.
    Automated onboarding via Google Admin SDK + service APIs is Phase 3.

    For Korean names like "김사라": last_name="김", first_name="사라".
    For English names like "John Kim": first_name="John", last_name="Kim".

    Args:
        email: User's email address (required, e.g. "sara.kim@company.com")
        first_name: User's given name (required, e.g. "사라" or "Sara")
        last_name: User's family name (required, e.g. "김" or "Kim")
        role: Role to assign - 'admin' or 'member' (default: member)
        temporary_password: Temporary password for first login (default: Welcome123!)
    """
    return (
        f"=== 온보딩 안내 ===\n"
        f"이름: {first_name} {last_name}\n"
        f"이메일: {email}\n"
        f"역할: {role}\n\n"
        f"현재 모든 서비스는 Google OIDC로 인증합니다.\n"
        f"사용자가 Google Workspace 계정이 있다면, 각 서비스에서 바로 로그인할 수 있습니다.\n\n"
        f"서비스 접속 URL:\n"
        f"  🔑 Vaultwarden (비밀번호): https://vault.david.sprintsolo.dev\n"
        f"  📊 Teable (스프레드시트):  https://teable.david.sprintsolo.dev\n"
        f"  💼 Twenty CRM:            https://crm.david.sprintsolo.dev\n\n"
        f"각 서비스에서 'Google로 로그인' 버튼을 클릭하면 됩니다.\n\n"
        f"⚠️ Google Admin SDK + 서비스 API를 통한 자동 온보딩은 Phase 3에서 구현 예정입니다."
    )
