"""Teable record query/search/filter tool."""

import json

from langchain_core.tools import tool

from .teable_client import check_configured, teable_get


@tool
def teable_query_records(
    table_id: str,
    filter_json: str = "",
    search: str = "",
    order_by: str = "",
    max_records: int = 50,
    skip: int = 0,
) -> str:
    """Teable 테이블에서 레코드를 조회합니다. 필터, 검색, 정렬을 지원합니다.

    Args:
        table_id: 테이블 ID
        filter_json: 필터 JSON. 예: '{"filterSet":[{"fieldId":"fldXXX","operator":"is","value":"서울"}],"conjunction":"and"}'
                     연산자: is, isNot, contains, doesNotContain, isGreater, isLess, isEmpty, isNotEmpty, isAnyOf, isNoneOf
        search: 텍스트 검색. 형식: '검색어' 또는 '검색어|필드ID' (필드 지정 검색)
        order_by: 정렬. 형식: 'fieldId:asc' 또는 'fieldId:desc'. 복수: 'fld1:asc,fld2:desc'
        max_records: 최대 반환 건수 (1-1000, 기본 50)
        skip: 건너뛸 레코드 수 (페이지네이션)
    """
    err = check_configured()
    if err:
        return err

    params = {
        "fieldKeyType": "name",
        "cellFormat": "text",
        "take": str(min(max(max_records, 1), 1000)),
        "skip": str(skip),
    }

    if filter_json:
        params["filter"] = filter_json

    if search:
        # search format: "term" or "term|fieldId"
        parts = search.split("|", 1)
        if len(parts) == 2:
            params["search"] = json.dumps([parts[0], parts[1]])
        else:
            params["search"] = json.dumps([parts[0]])

    if order_by:
        sort_objs = []
        for part in order_by.split(","):
            pair = part.strip().split(":")
            if len(pair) == 2:
                sort_objs.append({"fieldId": pair[0].strip(), "order": pair[1].strip()})
        if sort_objs:
            params["orderBy"] = json.dumps(sort_objs)

    result = teable_get(f"/table/{table_id}/record", params=params)
    if isinstance(result, str):
        return result

    records = result.get("records", [])
    total = result.get("total", len(records))

    if not records:
        return f"조건에 맞는 레코드가 없습니다. (총 {total}건 중 0건 조회)"

    lines = [f"=== 레코드 조회 결과 ({len(records)}건 / 총 {total}건) ===\n"]
    for i, rec in enumerate(records):
        rec_id = rec.get("id", "?")
        fields = rec.get("fields", {})
        lines.append(f"[{i + 1}] Record ID: {rec_id}")
        for fname, fval in fields.items():
            val_str = str(fval) if fval is not None else "(빈값)"
            if len(val_str) > 100:
                val_str = val_str[:100] + "..."
            lines.append(f"    {fname}: {val_str}")
        lines.append("")

    if total > skip + len(records):
        lines.append(f"다음 페이지: skip={skip + len(records)}")

    return "\n".join(lines)
