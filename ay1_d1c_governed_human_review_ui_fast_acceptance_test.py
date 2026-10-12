from pathlib import Path
from run_ay1_d1c_governed_human_review_ui import merge_decisions, validate_workbook_path
entry={"candidate":{"candidate_id":"candidate:x"},"human_decision":{"decision":"","reviewer_id":"","reviewer_role":"principal_investigator","rationale":"","confirmed_source":"a","confirmed_target":"b","confirmed_relation":"extends"}}
w={"entries":[entry],"decision_count":0}
p=[{"candidate_id":"candidate:x","human_decision":{"decision":"approve","reviewer_id":"colin","reviewer_role":"principal_investigator","rationale":"reviewed","confirmed_source":"tamper","confirmed_target":"tamper","confirmed_relation":"tamper"}}]
r,n=merge_decisions(w,p);assert n==1;h=r["entries"][0]["human_decision"];assert h["confirmed_source"]=="a" and h["confirmed_target"]=="b" and h["confirmed_relation"]=="extends"
print("AY1_D1C_GOVERNED_HUMAN_REVIEW_UI_FAST_ACCEPTANCE_OK")
