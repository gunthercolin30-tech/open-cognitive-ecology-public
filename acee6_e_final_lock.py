from pathlib import Path
p=Path('ontology/acee_installation_executor.py').read_text(encoding='utf-8')
for token in ['ACEE6_INVENTORY_UPDATE_COMPLETE','INVENTORY_UPDATING','INVENTORIES_UPDATED','inventory_update_manifest.json']:
 assert token in p,token
print('ACEE6_E_TRANSACTIONAL_INVENTORIES_FINAL_LOCK_OK')
