from run_ay1_d1c_governed_human_review import validate_entry
b={"candidate":{"candidate_id":"candidate:x","source":"a","target":"b","relation":"extends"},"candidate_payload_hash":"c","evidence_payload_hash":"e","human_decision":{"decision":"approve","reviewer_id":"h","reviewer_role":"principal_investigator","rationale":"r","confirmed_source":"a","confirmed_target":"b","confirmed_relation":"extends"}}
for m in ({"decision":""},{"reviewer_id":""},{"reviewer_role":"bot"},{"rationale":""},{"confirmed_target":"c"}):
 e={**b,"human_decision":dict(b["human_decision"])};e["human_decision"].update(m)
 try:validate_entry(e);raise AssertionError("unsafe accepted")
 except (ValueError,PermissionError):pass
print("AY1_D1C_GOVERNED_HUMAN_CAMPAIGN_DEGRADATION_OK")
