from pathlib import Path
s=(Path(__file__).resolve().parent/"run_ay1_d1c_governed_human_review_ui.py").read_text(encoding="utf-8")
for token in ('127.0.0.1','X-Session-Token','APPLIQUER LES 12 DECISIONS','atomic_json','validate_entry','apply_workbook','auto_promotion_performed=false'):
 assert token in s,token
assert '0.0.0.0' not in s
print("AY1_D1C_GOVERNED_HUMAN_REVIEW_UI_FINAL_LOCK_OK")
