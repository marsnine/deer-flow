import requests
import json
import urllib3
import time
import os
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
    print("Fetching Airtable schema...")
    at_tables = get_airtable_schema()
    
    at_global_fields = {}
    tasks = [] # lookups and rollups to create
    
    for t in at_tables:
        for f in t['fields']:
            at_global_fields[f['id']] = {
                'table_name': t['name'],
                'field_name': f['name'],
                'type': f['type'],
                'options': f.get('options', {})
            }
            if f['type'] in ['multipleLookupValues', 'rollup']:
                tasks.append({
                    'table_name': t['name'],
                    'field_name': f['name'],
                    'type': f['type'],
                    'options': f.get('options', {})
                })
                
    tb_tables = get_teable_schema()
    tb_table_id_map = {t['name']: t['id'] for t in tb_tables}
    
    tb_global_fields_by_name = {}
    
    for t_name, t_id in tb_table_id_map.items():
        fields = get_teable_fields(t_id)
        tb_global_fields_by_name[t_name] = {}
        for f in fields:
            f['tableId'] = t_id
            tb_global_fields_by_name[t_name][f['name']] = f
            
    success = 0
    fail = 0
    
    manual_mapping = {
        '연락처 ID': '1-1) 연락처(Contact)',
        '투자자명': '이름',
        '투자자 이메일': '이메일',
        '생년월일': '주민등록번호',
        '조합원 ID': '2-1) 투자자(Investor)',
        '분개 ID': '거래일시', 
        '출자금액(현재)': '출자좌수(현재)'
    }
    
    for pass_num in range(1):
        for task in tasks:
            t_name = task['table_name']
            f_name = task['field_name']
            opts = task['options']
            
            if t_name not in tb_table_id_map:
                continue
                
            tb_t_id = tb_table_id_map[t_name]
            tb_f_obj = tb_global_fields_by_name[t_name].get(f_name)
            
            if tb_f_obj and (tb_f_obj.get('isLookup') or tb_f_obj['type'] == 'rollup'):
                continue
                
            at_link_id = opts.get('recordLinkFieldId')
            at_target_id = opts.get('fieldIdInLinkedTable')
            
            if not at_link_id or not at_target_id:
                continue
                
            at_link_fld = at_global_fields.get(at_link_id)
            at_target_fld = at_global_fields.get(at_target_id)
            
            tb_link_fld = tb_global_fields_by_name[t_name].get(at_link_fld['field_name'])
            
            if not tb_link_fld or tb_link_fld['type'] != 'link':
                link_candidates = [f for f in tb_global_fields_by_name[t_name].values() if f['type'] == 'link' and f['name'] == at_link_fld['field_name']]
                if not link_candidates:
                    tb_foreign_table_name = at_target_fld['table_name']
                    if tb_foreign_table_name in tb_table_id_map:
                        foreign_t_id = tb_table_id_map[tb_foreign_table_name]
                        potential_links = [f for f in tb_global_fields_by_name[t_name].values() 
                                         if f['type'] == 'link' and f.get('options', {}).get('foreignTableId') == foreign_t_id]
                        if potential_links:
                            tb_link_fld = potential_links[0]
                        else:
                            continue
                    else:
                        continue
                else:
                    tb_link_fld = link_candidates[0]
                
            tb_target_table_name = at_target_fld['table_name']
            tb_target_fld = tb_global_fields_by_name.get(tb_target_table_name, {}).get(at_target_fld['field_name'])
            
            if not tb_target_fld:
                target_field_name = at_target_fld['field_name']
                if target_field_name in manual_mapping:
                    mapped_name = manual_mapping[target_field_name]
                    tb_target_fld = tb_global_fields_by_name.get(tb_target_table_name, {}).get(mapped_name)
                    if tb_target_fld:
                        pass
                
                if not tb_target_fld:
                    potential_targets = [f for f in tb_global_fields_by_name.get(tb_target_table_name, {}).values() if f['name'].startswith(target_field_name) or target_field_name.startswith(f['name'])]
                    if potential_targets:
                        tb_target_fld = potential_targets[0]
                    else:
                        continue
                
            payload = {}
            if task['type'] == 'multipleLookupValues':
                payload = {
                    "type": tb_target_fld['type'],
                    "isLookup": True,
                    "lookupOptions": {
                        "foreignTableId": tb_target_fld['tableId'],
                        "lookupFieldId": tb_target_fld['id'],
                        "linkFieldId": tb_link_fld['id']
                    }
                }
                # If target is link type, the lookup must also be multipleSelect but it sometimes throws errors, 
                # so we can use singleLineText or keep it matching
                if tb_target_fld['type'] == 'link':
                    payload['type'] = 'link' 
            elif task['type'] == 'rollup':
                expression = "array_join({values})"
                if tb_target_fld['type'] in ['number', 'currency', 'rating']:
                    expression = "sum({values})"
                    
                payload = {
                    "type": "rollup",
                    "options": {
                        "expression": expression
                    },
                    "lookupOptions": {
                        "foreignTableId": tb_target_fld['tableId'],
                        "lookupFieldId": tb_target_fld['id'],
                        "linkFieldId": tb_link_fld['id']
                    }
                }
                
            if tb_f_obj:
                res = requests.patch(f'{TEABLE_URL}/table/{tb_t_id}/field/{tb_f_obj["id"]}', headers=TB_HEADERS, json=payload, verify=False)
            else:
                payload['name'] = f_name
                res = requests.post(f'{TEABLE_URL}/table/{tb_t_id}/field', headers=TB_HEADERS, json=payload, verify=False)
                
            if res.status_code in [200, 201]:
                print(f"✅ [{t_name}] {f_name}: Migrated.")
                success += 1
            else:
                print(f"❌ [{t_name}] {f_name}: Failed -> {res.text}")
                fail += 1
                
    print(f"\nFinal: Success={success}, Failed={fail}")

if __name__ == '__main__':
    main()
