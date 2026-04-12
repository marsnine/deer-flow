"""Teable record deletion tool."""

from langchain_core.tools import tool

from .teable_client import check_configured, teable_delete


@tool
def teable_delete_records(table_id: str, record_ids: str) -> str:
    """Teable 테이블에서 레코드를 삭제합니다.
    WARNING: 삭제된 레코드는 복구할 수 없습니다!

    Args:
        table_id: 테이블 ID
        record_ids: 삭제할 레코드 ID (쉼표 구분). 예: 'recXXX,recYYY,recZZZ'
    """
    err = check_configured()
    if err:
        return err

    ids = [rid.strip() for rid in record_ids.split(",") if rid.strip()]
    if not ids:
        return "삭제할 레코드 ID가 지정되지 않았습니다."

    params = {"recordIds": ids}
    result = teable_delete(f"/table/{table_id}/record", params=params)
    if isinstance(result, str):
        return f"삭제 오류: {result}"

    return f"=== {len(ids)}건 레코드 삭제 완료 ===\n삭제된 ID: {', '.join(ids)}"
