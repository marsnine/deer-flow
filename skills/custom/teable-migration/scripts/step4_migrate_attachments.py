"""Step 4: Migrate attachments — one table at a time.

Usage:
    python step4_migrate_attachments.py                  # list tables with attachments
    python step4_migrate_attachments.py "테이블이름"      # migrate one table
    python step4_migrate_attachments.py --all            # migrate all tables sequentially

Airtable attachment URLs expire after 2 hours, so this script fetches
fresh records at execution time for the target table only.
"""
import requests
import json
import time
import sys
import os

AIRTABLE_PAT = "YOUR_AIRTABLE_PAT"
AIRTABLE_BASE_ID = "YOUR_AIRTABLE_BASE_ID"

TEABLE_URL = "YOUR_TEABLE_API_URL"
TEABLE_BASE_ID = "YOUR_TEABLE_BASE_ID"
TEABLE_API_KEY = "YOUR_TEABLE_API_KEY"

requests.packages.urllib3.disable_warnings()

MAPPING_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "migration_mapping.json")


def get_airtable_headers():
    return {"Authorization": f"Bearer {AIRTABLE_PAT}"}


def get_teable_headers():
    return {
        "Authorization": f"Bearer {TEABLE_API_KEY}",
        "Content-Type": "application/json"
    }


def load_mapping():
    with open(MAPPING_PATH) as f:
        return json.load(f)


def fetch_airtable_records(table_id):
    records = []
    offset = None
    while True:
        url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{table_id}"
        params = {}
        if offset:
            params["offset"] = offset
        res = requests.get(url, headers=get_airtable_headers(), params=params)
        res.raise_for_status()
        data = res.json()
        records.extend(data.get("records", []))
        offset = data.get("offset")
        if not offset:
            break
        time.sleep(0.2)
    return records


def get_teable_fields(table_id):
    res = requests.get(
        f"{TEABLE_URL}/api/table/{table_id}/field",
        headers=get_teable_headers(),
        verify=False
    )
    res.raise_for_status()
    return res.json()


def upload_attachment(table_id, record_id, field_id, file_url):
    headers = {"Authorization": f"Bearer {TEABLE_API_KEY}"}
    res = requests.post(
        f"{TEABLE_URL}/api/table/{table_id}/record/{record_id}/{field_id}/uploadAttachment",
        headers=headers,
        data={"fileUrl": file_url},
        verify=False
    )
    if res.status_code not in [200, 201]:
        print(f"    FAIL ({res.status_code}): {res.text[:200]}")
        return False
    return True


def migrate_table(table_name, info, rec_map):
    at_table_id = info["at_table_id"]
    teable_table_id = info["teable_table_id"]
    attachment_field_names = info["fields"]

    print(f"\n{'=' * 60}")
    print(f"  Migrating attachments: {table_name}")
    print(f"  Fields: {', '.join(attachment_field_names)}")
    print(f"{'=' * 60}")

    # Fetch fresh Airtable records (URLs valid for 2 hours from now)
    print(f"  Fetching fresh Airtable records...")
    at_records = fetch_airtable_records(at_table_id)
    print(f"  {len(at_records)} records fetched.")

    # Resolve Teable attachment field IDs
    teable_fields = get_teable_fields(teable_table_id)
    field_name_to_id = {}
    for f in teable_fields:
        if f["name"] in attachment_field_names and f["type"] == "attachment":
            field_name_to_id[f["name"]] = f["id"]

    if not field_name_to_id:
        print(f"  ERROR: No attachment-type fields found in Teable. Skipping.")
        return 0, 0

    print(f"  Resolved {len(field_name_to_id)} attachment field(s): {list(field_name_to_id.keys())}")

    success, fail, skip = 0, 0, 0
    total_files = 0

    for at_rec in at_records:
        teable_rec_id = rec_map.get(at_rec["id"])
        if not teable_rec_id:
            skip += 1
            continue

        fields = at_rec.get("fields", {})
        for field_name, field_id in field_name_to_id.items():
            attachments = fields.get(field_name)
            if not attachments or not isinstance(attachments, list):
                continue

            for att in attachments:
                url = att.get("url")
                filename = att.get("filename", "?")
                if not url:
                    continue
                total_files += 1
                ok = upload_attachment(teable_table_id, teable_rec_id, field_id, url)
                if ok:
                    success += 1
                    if success % 10 == 0:
                        print(f"    Progress: {success} uploaded...")
                else:
                    fail += 1
                time.sleep(0.1)

    print(f"\n  Result: {success}/{total_files} uploaded, {fail} failed, {skip} records skipped")
    return success, fail


def list_tables(mapping):
    att = mapping.get("attachment_fields", {})
    if not att:
        print("No tables with attachment fields found in mapping.")
        return
    print(f"\nTables with attachments ({len(att)}):")
    print("-" * 50)
    for name, info in att.items():
        print(f"  {name}")
        print(f"    Airtable ID:  {info['at_table_id']}")
        print(f"    Teable ID:    {info['teable_table_id']}")
        print(f"    Fields:       {', '.join(info['fields'])}")
    print(f"\nRun: python step4_migrate_attachments.py \"테이블이름\"")


def main():
    if not os.path.exists(MAPPING_PATH):
        print(f"ERROR: {MAPPING_PATH} not found. Run step1_migrate_base.py first.")
        sys.exit(1)

    mapping = load_mapping()
    rec_map = mapping.get("at_to_teable_rec", {})
    att_tables = mapping.get("attachment_fields", {})

    if len(sys.argv) < 2:
        list_tables(mapping)
        return

    target = sys.argv[1]

    if target == "--all":
        print(f"Migrating ALL {len(att_tables)} table(s) with attachments...")
        total_s, total_f = 0, 0
        for name, info in att_tables.items():
            s, f = migrate_table(name, info, rec_map)
            total_s += s
            total_f += f
        print(f"\n{'=' * 60}")
        print(f"  ALL DONE: {total_s} uploaded, {total_f} failed")
        print(f"{'=' * 60}")
    elif target in att_tables:
        migrate_table(target, att_tables[target], rec_map)
    else:
        print(f"ERROR: Table '{target}' not found in mapping.")
        print(f"Available: {', '.join(att_tables.keys())}")
        sys.exit(1)


if __name__ == "__main__":
    main()
