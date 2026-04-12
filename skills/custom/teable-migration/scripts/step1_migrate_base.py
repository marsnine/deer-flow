import requests
import json
import time

AIRTABLE_PAT = "YOUR_AIRTABLE_PAT"
AIRTABLE_BASE_ID = "YOUR_AIRTABLE_BASE_ID"

TEABLE_URL = "YOUR_TEABLE_API_URL"
TEABLE_BASE_ID = "YOUR_TEABLE_BASE_ID"
TEABLE_API_KEY = "YOUR_TEABLE_API_KEY"

requests.packages.urllib3.disable_warnings()

def get_airtable_headers():
    return {"Authorization": f"Bearer {AIRTABLE_PAT}"}

def get_teable_headers():
    return {
        "Authorization": f"Bearer {TEABLE_API_KEY}",
        "Content-Type": "application/json"
    }

def fetch_airtable_schema():
    res = requests.get(f"https://api.airtable.com/v0/meta/bases/{AIRTABLE_BASE_ID}/tables", headers=get_airtable_headers())
    res.raise_for_status()
    return res.json()["tables"]

def map_field_type(at_field):
    at_type = at_field.get("type")
    
    if at_type in ["singleLineText", "email", "url", "phoneNumber"]:
        return {"type": "singleLineText"}
    elif at_type in ["multilineText", "richText"]:
        return {"type": "longText"}
    elif at_type in ["number", "currency", "percent", "rating"]:
        return {"type": "number"}
    elif at_type == "checkbox":
        return {"type": "checkbox"}
    elif at_type == "singleSelect":
        choices = at_field.get("options", {}).get("choices", [])
        return {"type": "singleSelect", "options": {"choices": [{"name": c["name"]} for c in choices]}}
    elif at_type == "multipleSelects":
        choices = at_field.get("options", {}).get("choices", [])
        return {"type": "multipleSelect", "options": {"choices": [{"name": c["name"]} for c in choices]}}
    elif at_type in ["date", "dateTime"]:
        return {"type": "date"}
    elif at_type == "multipleRecordLinks":
        return {"type": "__link__"}
    elif at_type in ["formula", "rollup", "multipleLookupValues"]:
        return {"type": "__skip__"}
    else:
        return {"type": "singleLineText"}

def convert_value_for_teable(value, mapped_type):
    if value is None:
        return None
    
    if mapped_type == "singleLineText" or mapped_type == "longText":
        if isinstance(value, list) or isinstance(value, dict):
            return json.dumps(value, ensure_ascii=False)
        return str(value)
    elif mapped_type == "number":
        try:
            return float(value)
        except:
            return None
    elif mapped_type == "checkbox":
        return bool(value)
    elif mapped_type in ["singleSelect", "multipleSelect", "date"]:
        return value
    return str(value)

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

def create_teable_table(name, fields_schema):
    payload = {
        "name": name,
        "fields": fields_schema
    }
    res = requests.post(
        f"{TEABLE_URL}/api/base/{TEABLE_BASE_ID}/table", 
        headers=get_teable_headers(), 
        json=payload,
        verify=False
    )
    if res.status_code not in [200, 201]:
        print(f"Error creating table {name}: {res.text}")
        print("Retrying with all fields as singleLineText...")
        fallback_fields = [{"name": f["name"], "type": "singleLineText"} for f in fields_schema]
        payload["fields"] = fallback_fields
        res = requests.post(
            f"{TEABLE_URL}/api/base/{TEABLE_BASE_ID}/table", 
            headers=get_teable_headers(), 
            json=payload,
            verify=False
        )
        res.raise_for_status()
        return res.json()["id"], {f["name"]: "singleLineText" for f in fallback_fields}
        
    return res.json()["id"], {f["name"]: f["type"] for f in fields_schema}

def insert_teable_records(table_id, records_payload, at_records=None):
    id_map = {}
    chunk_size = 100
    for i in range(0, len(records_payload), chunk_size):
        chunk = records_payload[i:i+chunk_size]
        res = requests.post(
            f"{TEABLE_URL}/api/table/{table_id}/record",
            headers=get_teable_headers(),
            json={"records": chunk},
            verify=False
        )
        if res.status_code not in [200, 201]:
            print(f"Error inserting records: {res.text}")
            res.raise_for_status()
        if at_records:
            created = res.json().get("records", [])
            at_chunk = at_records[i:i+chunk_size]
            for j, c_rec in enumerate(created):
                if j < len(at_chunk):
                    id_map[at_chunk[j]["id"]] = c_rec["id"]
        time.sleep(0.2)
    return id_map

def create_link_field(teable_table_id, field_name, foreign_table_id, relationship="manyMany"):
    payload = {
        "name": field_name,
        "type": "link",
        "options": {
            "foreignTableId": foreign_table_id,
            "relationship": relationship
        }
    }
    res = requests.post(
        f"{TEABLE_URL}/api/table/{teable_table_id}/field",
        headers=get_teable_headers(),
        json=payload,
        verify=False
    )
    if res.status_code not in [200, 201]:
        print(f"  Failed to create link field '{field_name}': {res.text}")
        return None
    return res.json()

def update_link_records(teable_table_id, updates):
    chunk_size = 100
    success, fail = 0, 0
    for i in range(0, len(updates), chunk_size):
        chunk = updates[i:i+chunk_size]
        res = requests.patch(
            f"{TEABLE_URL}/api/table/{teable_table_id}/record",
            headers=get_teable_headers(),
            json={"records": chunk},
            verify=False
        )
        if res.status_code in [200, 201]:
            success += len(chunk)
        else:
            fail += len(chunk)
            print(f"  Error updating link records: {res.text}")
        time.sleep(0.2)
    return success, fail

def main():
    print("Fetching Airtable schema...")
    at_tables = fetch_airtable_schema()

    # Collect link field metadata
    link_field_info = {}
    for at_table in at_tables:
        at_table_id = at_table["id"]
        link_field_info[at_table_id] = []
        for f in at_table.get("fields", []):
            if f["type"] == "multipleRecordLinks":
                link_field_info[at_table_id].append({
                    "field_name": f["name"],
                    "linked_at_table_id": f["options"]["linkedTableId"],
                    "at_field_id": f["id"],
                    "inverse_field_id": f["options"].get("inverseLinkFieldId")
                })

    # Pre-fetch all Airtable records
    at_all_records = {}
    for at_table in at_tables:
        at_table_id = at_table["id"]
        print(f"Fetching records for '{at_table['name']}'...")
        at_all_records[at_table_id] = fetch_airtable_records(at_table_id)
        print(f"  {len(at_all_records[at_table_id])} records.")

    # ── PHASE A: Create tables with non-link fields + insert records ──
    print("\n" + "=" * 60)
    print("  PHASE A: Create tables & insert records (non-link fields)")
    print("=" * 60)

    at_to_teable_table = {}
    at_to_teable_rec = {}

    for at_table in at_tables:
        at_table_id = at_table["id"]
        table_name = at_table["name"]
        print(f"\nProcessing table: {table_name}")

        teable_fields = []
        final_field_types = {}
        link_field_names = set()

        for f in at_table.get("fields", []):
            field_name = f["name"]
            mapped = map_field_type(f)

            if mapped["type"] == "__link__":
                link_field_names.add(field_name)
                continue
            if mapped["type"] == "__skip__":
                continue

            mapped["name"] = field_name
            teable_fields.append(mapped)
            final_field_types[field_name] = mapped["type"]

        print(f"  Creating Teable table '{table_name}'...")
        teable_table_id, final_field_types = create_teable_table(table_name, teable_fields)
        at_to_teable_table[at_table_id] = teable_table_id
        print(f"  Created: {teable_table_id}")

        at_records = at_all_records[at_table_id]
        if not at_records:
            continue

        teable_records_payload = []
        for rec in at_records:
            fields = rec.get("fields", {})
            new_fields = {}
            for k, v in fields.items():
                if k in final_field_types and k not in link_field_names:
                    new_fields[k] = convert_value_for_teable(v, final_field_types[k])
            teable_records_payload.append({"fields": new_fields})

        print(f"  Inserting {len(teable_records_payload)} records...")
        id_map = insert_teable_records(teable_table_id, teable_records_payload, at_records)
        at_to_teable_rec.update(id_map)
        print(f"  Mapped {len(id_map)} record IDs.")

    # ── PHASE B: Create link fields ──
    print("\n" + "=" * 60)
    print("  PHASE B: Create link fields")
    print("=" * 60)

    processed_link_fields = set()
    link_fields_created = []

    for at_table in at_tables:
        at_table_id = at_table["id"]
        teable_table_id = at_to_teable_table.get(at_table_id)
        if not teable_table_id:
            continue

        for lf in link_field_info[at_table_id]:
            if lf["at_field_id"] in processed_link_fields:
                continue

            linked_teable_table_id = at_to_teable_table.get(lf["linked_at_table_id"])
            if not linked_teable_table_id:
                print(f"  Skipping '{lf['field_name']}': target table not migrated.")
                continue

            table_name = next(t["name"] for t in at_tables if t["id"] == at_table_id)
            target_name = next((t["name"] for t in at_tables if t["id"] == lf["linked_at_table_id"]), "?")
            print(f"  Creating link: '{table_name}'.'{lf['field_name']}' -> '{target_name}'")

            result = create_link_field(teable_table_id, lf["field_name"], linked_teable_table_id)
            if result:
                processed_link_fields.add(lf["at_field_id"])
                if lf["inverse_field_id"]:
                    processed_link_fields.add(lf["inverse_field_id"])
                link_fields_created.append({
                    "at_table_id": at_table_id,
                    "teable_table_id": teable_table_id,
                    "field_name": lf["field_name"]
                })

    # ── PHASE C: Populate link data ──
    print("\n" + "=" * 60)
    print("  PHASE C: Populate link data")
    print("=" * 60)

    total_success, total_fail = 0, 0

    for lf in link_fields_created:
        at_table_id = lf["at_table_id"]
        teable_table_id = lf["teable_table_id"]
        field_name = lf["field_name"]

        at_records = at_all_records[at_table_id]
        updates = []

        for at_rec in at_records:
            at_link_ids = at_rec.get("fields", {}).get(field_name)
            if not at_link_ids or not isinstance(at_link_ids, list):
                continue

            teable_rec_id = at_to_teable_rec.get(at_rec["id"])
            if not teable_rec_id:
                continue

            teable_link_values = []
            for at_link_id in at_link_ids:
                teable_linked_id = at_to_teable_rec.get(at_link_id)
                if teable_linked_id:
                    teable_link_values.append({"id": teable_linked_id})

            if teable_link_values:
                updates.append({
                    "id": teable_rec_id,
                    "fields": {field_name: teable_link_values}
                })

        if updates:
            print(f"  Updating {len(updates)} records for '{field_name}'...")
            s, f = update_link_records(teable_table_id, updates)
            total_success += s
            total_fail += f
        else:
            print(f"  No link data for '{field_name}'.")

    print(f"\nMigration completed! Link updates: {total_success} success, {total_fail} fail.")

if __name__ == '__main__':
    main()
