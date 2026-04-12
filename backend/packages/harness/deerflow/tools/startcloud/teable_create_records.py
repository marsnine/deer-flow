"""Teable record creation tool."""

import json

from langchain_core.tools import tool

from .teable_client import check_configured, teable_post


@tool
def teable_create_records(table_id: str, records_json: str, typecast: bool = True) -> str:
    """Teable 테이블에 레코드를 생성합니다. 1건 또는 여러 건을 한 번에 생성할 수 있습니다.

    Args:
        table_id: 테이블 ID
        records_json: 레코드 JSON 배열. 필드 이름을 키로 사용합니다.
                      예: '[{"fields":{"이름":"김사라","이메일":"sara@test.com"}}]'
                      복수: '[{"fields":{"이름":"김사라"}},{"fields":{"이름":"박지민"}}]'
        typecast: true면 값 자동 타입 변환 (기본 true). 날짜, 링크 등의 자동 변환에 유용.
    """
    err = check_configured()
    if err:
        return err

    try:
        records = json.loads(records_json)
    except json.JSONDecodeError as e:
        return f"JSON 파싱 오류: {e}"

    if not isinstance(records, list):
        records = [records]

    body = {
        "records": records,
        "fieldKeyType": "name",
        "typecast": typecast,
    }

    result = teable_post(f"/table/{table_id}/record", body)
    if isinstance(result, str):
        return result

    created = result.get("records", [])
    if not created:
        return "레코드 생성 결과를 확인할 수 없습니다."

    lines = [f"=== {len(created)}건 레코드 생성 완료 ===\n"]
    for rec in created:
        rec_id = rec.get("id", "?")
        fields = rec.get("fields", {})
        field_summary = ", ".join(f"{k}={v}" for k, v in list(fields.items())[:5])
        lines.append(f"  {rec_id}: {field_summary}")

    return "\n".join(lines)
