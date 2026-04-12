import requests
import json
import re
import urllib3
import time
urllib3.disable_warnings()

AIRTABLE_BASE = 'YOUR_AIRTABLE_BASE_ID'
AIRTABLE_PAT = 'YOUR_AIRTABLE_PAT'

TEABLE_URL = 'YOUR_TEABLE_API_URL/api'
TEABLE_BASE = 'YOUR_TEABLE_BASE_ID'
TEABLE_KEY = 'YOUR_TEABLE_API_KEY'
TB_HEADERS = {'Authorization': f'Bearer {TEABLE_KEY}', 'Content-Type': 'application/json'}

def get_airtable_schema():
    res = requests.get(f'https://api.airtable.com/v0/meta/bases/{AIRTABLE_BASE}/tables',
                       headers={'Authorization': f'Bearer {AIRTABLE_PAT}'}).json()
    return res.get('tables', [])

def get_teable_schema():
    return requests.get(f'{TEABLE_URL}/base/{TEABLE_BASE}/table', headers=TB_HEADERS, verify=False).json()

def get_teable_fields(table_id):
    return requests.get(f'{TEABLE_URL}/table/{table_id}/field', headers=TB_HEADERS, verify=False).json()

def main():
    at_tables = get_airtable_schema()
    tb_tables = get_teable_schema()
    
    at_field_map = {}
    at_formulas = []
    
    for t in at_tables:
        t_name = t['name']
        at_field_map[t_name] = {}
        for f in t['fields']:
            at_field_map[t_name][f['id']] = f['name']
            if f['type'] == 'formula':
                at_formulas.append({
                    'table_name': t_name,
                    'field_name': f['name'],
                    'at_fld_id': f['id'],
                    'formula': f.get('options', {}).get('formula', '')
                })

    tb_field_map = {}
    tb_field_obj = {}
    tb_table_id_map = {}
    
    for t in tb_tables:
        t_name = t['name']
        t_id = t['id']
        tb_table_id_map[t_name] = t_id
        
        fields = get_teable_fields(t_id)
        tb_field_map[t_name] = {}
        tb_field_obj[t_name] = {}
        for f in fields:
            tb_field_map[t_name][f['name']] = f['id']
            tb_field_obj[t_name][f['name']] = f
            
    success_count = 0
    fail_count = 0
    
    manual_mapping = {
        '조합 ID': '3-1) 조합(Fund)',
        '조합원': '3-2) 조합원명부(Contribution)',
        '조합원명부 ID': '3-2) 조합원명부(Contribution)',
        '기업명': '2-2) 투자기업(Portfolio)',
        '조합명 (from 조합 ID) (from 4-1) 투자현황(Invest)) Rollup (from 기업명)': '조합명 (from 4-1) 투자현황(Invest) (from 조합 ID)) Rollup (from 기업명)'
    }
    
    # Unsupported Airtable functions — fall back to placeholder string
    unsupported_patterns = ['REGEX_MATCH', 'REGEX_REPLACE', 'REGEX_EXTRACT', 'IRR']

    for item in at_formulas:
        t_name = item['table_name']
        f_name = item['field_name']
        raw_formula = item['formula']

        if t_name not in tb_table_id_map:
            continue

        tb_t_id = tb_table_id_map[t_name]

        # Check for unsupported functions
        has_unsupported = False
        for pattern in unsupported_patterns:
            if pattern in raw_formula:
                has_unsupported = True
                converted_expression = f'"{pattern} unsupported"'
                print(f"  [{t_name}] {f_name}: Contains unsupported function {pattern}, using placeholder.")
                break

        if not has_unsupported:
            missing_dep = False
            def replacer(match):
                nonlocal missing_dep
                at_id = match.group(1)
                at_name = at_field_map[t_name].get(at_id)
                if not at_name:
                    missing_dep = True
                    return match.group(0)

                mapped_name = manual_mapping.get(at_name, at_name)

                tb_id = tb_field_map[t_name].get(mapped_name)
                if not tb_id:
                    for tn, tid in tb_field_map[t_name].items():
                        if at_name in tn or tn in at_name:
                            tb_id = tid
                            break
                    if not tb_id:
                        print(f"  Cannot find mapped field for '{at_name}' in Teable table '{t_name}'.")
                        missing_dep = True
                        return match.group(0)

                return f"{{{tb_id}}}"

            converted_expression = re.sub(r'\{(fld[a-zA-Z0-9]+)\}', replacer, raw_formula)

            if missing_dep:
                print(f"❌ [{t_name}] {f_name}: Missing dependency. Skipping.")
                fail_count += 1
                continue

        tb_f_obj = tb_field_obj[t_name].get(f_name)

        payload = {
            "type": "formula",
            "options": {
                "expression": converted_expression
            }
        }

        if tb_f_obj:
            res = requests.patch(f'{TEABLE_URL}/table/{tb_t_id}/field/{tb_f_obj["id"]}', headers=TB_HEADERS, json=payload, verify=False)
            if res.status_code in [200, 201]:
                print(f"✅ [{t_name}] {f_name}: Patched.")
                success_count += 1
            else:
                print(f"❌ [{t_name}] {f_name}: Patch failed. {res.text[:200]}")
                fail_count += 1
        else:
            payload["name"] = f_name
            res = requests.post(f'{TEABLE_URL}/table/{tb_t_id}/field', headers=TB_HEADERS, json=payload, verify=False)
            if res.status_code in [200, 201]:
                print(f"✅ [{t_name}] {f_name}: Created.")
                success_count += 1
            else:
                print(f"❌ [{t_name}] {f_name}: Create failed. {res.text[:200]}")
                fail_count += 1

    print(f"\nFormulas: {success_count} success, {fail_count} failed.")

if __name__ == '__main__':
    main()
