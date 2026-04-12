"""Teable record update tool."""

import json

from langchain_core.tools import tool

from .teable_client import check_configured, teable_patch


@tool
def teable_update_records(table_id: str, updates_json: str, typecast: bool = True) -> str:
    """Teable 테이블의 레코드를 수정합니다. 1건 또는 여러 건을 수정할 수 있습니다.

    Args:
        table_id: 테이블 ID
        updates_json: 수정 JSON 배열. 각 항목에 recordId와 수정할 fields를 포함합니다.
                      예: '[{"recordId":"recXXX","fields":{"상태":"완료"}}]'
                      복수: '[{"recordId":"recXXX","fields":{"상태":"완료"}},{"recordId":"recYYY","fields":{"상태":"진행중"}}]'
        typecast: true면 값 자동 타입 변환 (기본 true)
    """
    err = check_configured()
    if err:
        return err

    try:
        updates = json.loads(updates_json)
    except json.JSONDecodeError as e:
        return f"JSON 파싱 오류: {e}"

    if not isinstance(updates, list):
        updates = [updates]

    results = []
    errors = []

    for upd in updates:
        rec_id = upd.get("recordId", "")
        fields = upd.get("fields", {})
        if not rec_id:
            errors.append("recordId가 없는 항목이 있습니다.")
            continue

        body = {
            "fieldKeyType": "name",
            "typecast": typecast,
            "record": {"fields": fields},
        }

        result = teable_patch(f"/table/{table_id}/record/{rec_id}", body)
        if isinstance(result, str):
            errors.append(f"{rec_id}: {result}")
        else:
            results.append(rec_id)

    lines = []
    if results:
        lines.append(f"=== {len(results)}건 레코드 수정 완료 ===")
        for rid in results:
            lines.append(f"  {rid}")
    if errors:
        lines.append(f"\n=== {len(errors)}건 오류 ===")
        for e in errors:
            lines.append(f"  {e}")

    return "\n".join(lines) if lines else "수정할 레코드가 없습니다."
