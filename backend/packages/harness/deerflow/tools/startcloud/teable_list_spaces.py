"""Teable space/base/table discovery tool."""

from langchain_core.tools import tool

from .teable_client import check_configured, teable_get


@tool
def teable_list_spaces(space_id: str = "", base_id: str = "") -> str:
    """Teable의 Space, Base, Table을 탐색합니다.
    인자 없이 호출하면 전체 Space 목록을 보여줍니다.
    space_id를 넣으면 해당 Space의 Base 목록을, base_id를 넣으면 Table 목록을 보여줍니다.

    Args:
        space_id: Space ID (해당 Space의 Base 목록 조회)
        base_id: Base ID (해당 Base의 Table 목록 조회)
    """
    err = check_configured()
    if err:
        return err

    # List tables in a base
    if base_id:
        result = teable_get(f"/base/{base_id}/table")
        if isinstance(result, str):
            return result
        tables = result if isinstance(result, list) else result.get("tables", result)
        if not tables:
            return f"Base {base_id}에 테이블이 없습니다."
        lines = [f"=== Base {base_id}의 테이블 목록 ===\n"]
        for t in tables:
            tid = t.get("id", "?")
            name = t.get("name", "?")
            desc = t.get("description", "")
            lines.append(f"  {name} (ID: {tid})")
            if desc:
                lines.append(f"    설명: {desc}")
        return "\n".join(lines)

    # List bases in a space
    if space_id:
        result = teable_get(f"/space/{space_id}/base")
        if isinstance(result, str):
            return result
        bases = result if isinstance(result, list) else result.get("bases", result)
        if not bases:
            return f"Space {space_id}에 Base가 없습니다."
        lines = [f"=== Space {space_id}의 Base 목록 ===\n"]
        for b in bases:
            bid = b.get("id", "?")
            name = b.get("name", "?")
            lines.append(f"  {name} (ID: {bid})")
        return "\n".join(lines)

    # List all spaces
    result = teable_get("/space")
    if isinstance(result, str):
        return result
    spaces = result if isinstance(result, list) else result.get("spaces", result)
    if not spaces:
        return "접근 가능한 Space가 없습니다."
    lines = ["=== Teable Space 목록 ===\n"]
    for s in spaces:
        sid = s.get("id", "?")
        name = s.get("name", "?")
        role = s.get("role", "")
        lines.append(f"  {name} (ID: {sid}, role: {role})")
    return "\n".join(lines)
