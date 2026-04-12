"""Teable aggregation and SQL query tool."""

import json

from langchain_core.tools import tool

from .teable_client import check_configured, teable_get, teable_post


@tool
def teable_aggregate(
    table_id: str,
    action: str = "row_count",
    field_id: str = "",
    aggregation: str = "sum",
    base_id: str = "",
    sql: str = "",
) -> str:
    """Teable 테이블의 집계 데이터를 조회하거나 SQL을 실행합니다.

    Args:
        action: 'row_count', 'aggregate', 'sql' 중 하나
        table_id: 테이블 ID
        field_id: aggregate 시 필요. 집계할 필드 ID
        aggregation: 집계 함수. sum, avg, min, max, count, empty, filled, unique, percentEmpty, percentFilled
        base_id: sql 시 필요. Base ID
        sql: sql 시 필요. SQL 쿼리 문자열. 예: 'SELECT * FROM table_name WHERE amount > 100'
    """
    err = check_configured()
    if err:
        return err

    if action == "row_count":
        result = teable_get(f"/table/{table_id}/aggregation/row-count")
        if isinstance(result, str):
            return result
        count = result.get("rowCount", result)
        return f"총 레코드 수: {count}"

    elif action == "aggregate":
        if not field_id:
            return "aggregate에는 field_id가 필요합니다."
        params = {
            "field": json.dumps({field_id: [aggregation]}),
        }
        result = teable_get(f"/table/{table_id}/aggregation", params=params)
        if isinstance(result, str):
            return result
        aggregations = result.get("aggregations", [result])
        lines = [f"=== 집계 결과 ({aggregation}) ===\n"]
        if isinstance(aggregations, list):
            for agg in aggregations:
                for k, v in agg.items():
                    lines.append(f"  {k}: {v}")
        elif isinstance(aggregations, dict):
            for k, v in aggregations.items():
                lines.append(f"  {k}: {v}")
        else:
            lines.append(f"  결과: {aggregations}")
        return "\n".join(lines)

    elif action == "sql":
        if not base_id:
            return "sql에는 base_id가 필요합니다."
        if not sql:
            return "sql에는 sql 쿼리가 필요합니다."
        body = {"sql": sql}
        result = teable_post(f"/base/{base_id}/table/{table_id}/sql-query", body)
        if isinstance(result, str):
            return result
        columns = result.get("columns", [])
        rows = result.get("rows", [])
        if not rows:
            return "SQL 쿼리 결과가 비어 있습니다."
        lines = [f"=== SQL 쿼리 결과 ({len(rows)}건) ===\n"]
        # Header
        col_names = [c.get("name", "?") if isinstance(c, dict) else str(c) for c in columns]
        if col_names:
            lines.append("  | ".join(col_names))
            lines.append("  " + "-" * (len("  | ".join(col_names))))
        # Rows
        for row in rows[:50]:
            if isinstance(row, dict):
                vals = [str(row.get(c, "")) for c in col_names]
            elif isinstance(row, list):
                vals = [str(v) for v in row]
            else:
                vals = [str(row)]
            lines.append("  | ".join(vals))
        if len(rows) > 50:
            lines.append(f"\n... 외 {len(rows) - 50}건")
        return "\n".join(lines)

    else:
        return f"알 수 없는 action: {action}. 사용 가능: row_count, aggregate, sql"
