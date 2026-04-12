"""Teable table field/column discovery tool."""

from langchain_core.tools import tool

from .teable_client import check_configured, teable_get


@tool
def teable_get_fields(table_id: str) -> str:
    """테이블의 모든 필드(컬럼) 정보를 조회합니다.
    필드 이름, 타입, ID, 옵션을 반환합니다.
    다른 도구 사용 전에 반드시 호출하여 테이블 구조를 파악하세요.

    Args:
        table_id: 테이블 ID (예: 'tblXXXXXX')
    """
    err = check_configured()
    if err:
        return err

    result = teable_get(f"/table/{table_id}/field")
    if isinstance(result, str):
        return result

    fields = result if isinstance(result, list) else result.get("fields", result)
    if not fields:
        return f"테이블 {table_id}에 필드가 없습니다."

    lines = [f"=== 테이블 {table_id} 필드 목록 ({len(fields)}개) ===\n"]
    for f in fields:
        fid = f.get("id", "?")
        name = f.get("name", "?")
        ftype = f.get("type", "?")
        is_primary = f.get("isPrimary", False)
        primary_tag = " [PRIMARY]" if is_primary else ""

        lines.append(f"  {name} ({ftype}) — ID: {fid}{primary_tag}")

        # Show options for select fields
        options = f.get("options", {})
        if ftype in ("singleSelect", "multipleSelect") and options:
            choices = options.get("choices", [])
            if choices:
                choice_names = [c.get("name", "?") for c in choices[:10]]
                lines.append(f"    선택지: {', '.join(choice_names)}")
                if len(choices) > 10:
                    lines.append(f"    ... 외 {len(choices) - 10}개")

        # Show link target for link fields
        if ftype == "link" and options:
            foreign_table = options.get("foreignTableId", "")
            if foreign_table:
                lines.append(f"    연결: {foreign_table}")

    return "\n".join(lines)
