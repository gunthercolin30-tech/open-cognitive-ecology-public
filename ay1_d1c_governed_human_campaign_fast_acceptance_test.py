from run_ay1_d1c_governed_human_review import validate_entry
e={"candidate":{"candidate_id":"candidate:x","source":"a","target":"b","relation":"extends"},"candidate_payload_hash":"c","evidence_payload_hash":"e","human_decision":{"decision":"approve","reviewer_id":"colin","reviewer_role":"principal_investigator","rationale":"explicit review","confirmed_source":"a","confirmed_target":"b","confirmed_relation":"extends"}}
r=validate_entry(e);assert r["decision_id"].startswith("decision:")
print("AY1_D1C_GOVERNED_HUMAN_CAMPAIGN_FAST_ACCEPTANCE_OK")
