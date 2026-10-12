from run_ay1_d1c_governed_human_review_ui import merge_decisions
base={"entries":[{"candidate":{"candidate_id":"candidate:x"},"human_decision":{"decision":"","reviewer_id":"","reviewer_role":"principal_investigator","rationale":"","confirmed_source":"a","confirmed_target":"b","confirmed_relation":"extends"}}],"decision_count":0}
for payload in ([],[{"candidate_id":"other","human_decision":{}}],[{"candidate_id":"candidate:x","human_decision":{"decision":"auto_approve","reviewer_role":"principal_investigator"}}],[{"candidate_id":"candidate:x","human_decision":{"decision":"approve","reviewer_role":"bot"}}]):
 try:merge_decisions({"entries":[dict(base["entries"][0])],"decision_count":0},payload);raise AssertionError("unsafe payload accepted")
 except ValueError:pass
print("AY1_D1C_GOVERNED_HUMAN_REVIEW_UI_DEGRADATION_OK")
