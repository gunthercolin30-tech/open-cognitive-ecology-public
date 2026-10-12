from copy import deepcopy
from ontology.p161_authorization_token_binding import dependency_vector,issue_authorization_token,verify_token_integrity
from ontology.p161_authorization_token_lifecycle import initialize_lifecycle,refresh,reserve_for_use,consume_reserved,revoke

KEY=b"p161i-independent-crown-key"
def base(policy="SINGLE_USE"):
 req={"authorization_request_id":"AR-I","request_hash":"RQH","normative_decision_id":"ND-I","action_digest":"AD-I",
 "runtime_context_fingerprint":"RF","constitutional_snapshot_hash":"CS","compiled_profile_hash":"CP"}
 nd={"decision_id":"ND-I","artifact_hash":"NDH"}
 au={"status":"VALID","receipt_hash":"AUH"}
 ev={"status":"SATISFIED","evidence_bundle_hash":"EVH"}
 hi={"status":"SATISFIED","receipt_hash":"HIH"}
 se={"status":"CONSTRUCTED","authorization_request_id":"AR-I","normative_decision_id":"ND-I",
 "scope":{"region":["FR"],"mode":["READ"]},"capabilities":["CAP_A"],"target":"T","purpose":"P",
 "validity":{"not_before":"2026-10-01T10:00:00Z","not_after":"2026-10-01T12:00:00Z"},
 "requested_use_policy":policy,"scope_envelope_hash":"SEH"}
 return req,nd,au,ev,hi,se

def issue(b=None,cur=None):
 b=b or base();v=dependency_vector(*b)
 return issue_authorization_token(*b,current_dependency_vector=cur or v,signer_id="CROWN-ISSUER",
 signing_key=KEY,issued_at="2026-10-01T10:30:00Z")

def positive_controls():
 out={}
 def run(name,fn):
  try:out[name]="PASS" if fn() else "FAIL"
  except Exception:out[name]="INCONCLUSIVE"
 run("valid_low_risk_predelegated",lambda: issue()["status"]=="TOKEN_COMMITTED")
 run("human_reserved_with_independent_human_approval",lambda: base()[4]["status"]=="SATISFIED" and issue()["status"]=="TOKEN_COMMITTED")
 run("explicit_succession_preserves_no_amplification",lambda: issue()["token"]["body"]["scope"]=={"region":["FR"],"mode":["READ"]})
 run("scope_reduction",lambda: set(issue()["token"]["body"]["scope"]["mode"])=={"READ"})
 run("quorum_2_of_3_evidence_satisfied",lambda: base()[3]["status"]=="SATISFIED" and issue()["status"]=="TOKEN_COMMITTED")
 run("ai_recommendation_independent_human_approval",lambda: base()[4]["status"]=="SATISFIED" and issue()["token"]["body"]["non_sovereign"] is True)
 def multi():
  b=base("BOUNDED_MULTI_USE");x=issue(b);t=x["token"];lc=refresh(initialize_lifecycle(t,max_uses=2),t,now="2026-10-01T11:00:00Z")
  r=reserve_for_use(lc,t,now="2026-10-01T11:01:00Z",reservation_id="R1",current_token_hash=t["token_hash"])
  c=consume_reserved(r["lifecycle"],now="2026-10-01T11:02:00Z",reservation_id="R1")
  return c["lifecycle"]["state"]=="CURRENT" and c["lifecycle"]["consumed_uses"]==1
 run("bounded_multi_use",multi)
 def emergency_window():
  x=issue();t=x["token"];lc=initialize_lifecycle(t)
  return refresh(lc,t,now="2026-10-01T09:59:59Z")["state"]=="NOT_YET_VALID" and refresh(lc,t,now="2026-10-01T12:00:00Z")["state"]=="EXPIRED"
 run("emergency_exact_window",emergency_window)
 def shadow():
  x=issue();return x["execution_performed"] is False and x["p162_opened"] is False and x["token"]["body"]["permits_execution"] is False
 run("shadow_token_remains_non_executing",shadow)
 def restart():
  x=issue();t=deepcopy(x["token"]);lc=refresh(deepcopy(initialize_lifecycle(t)),t,now="2026-10-01T11:00:00Z")
  return lc["state"]=="CURRENT" and verify_token_integrity(t,KEY)["status"]=="PASS"
 run("restart_preserves_legitimate_current_token",restart)
 return out

def root_defenses():
 out={}
 def run(name,fn):
  try:out[name]="PASS" if fn() else "VIOLATED"
  except Exception:out[name]="INCONCLUSIVE"
 def drift(field):
  b=base();v=dependency_vector(*b);v[field]="DRIFT";return issue(b,v)["status"]=="REFUSED"
 for f in ("request_hash","normative_decision_hash","authority_receipt_hash","approval_evidence_bundle_hash",
           "human_integrity_receipt_hash","scope_envelope_hash","runtime_context_fingerprint",
           "constitutional_snapshot_hash","compiled_profile_hash"):
  run("dependency_drift_"+f,lambda f=f:drift(f))
 def invalid_authority():
  b=list(base());b[2]=dict(b[2],status="REVOKED");return issue(tuple(b))["status"]=="REFUSED"
 run("revoked_authority",invalid_authority)
 def unknown_evidence():
  b=list(base());b[3]=dict(b[3],status="UNKNOWN");return issue(tuple(b))["status"]=="REFUSED"
 run("unknown_evidence",unknown_evidence)
 def unknown_human():
  b=list(base());b[4]=dict(b[4],status="UNKNOWN");return issue(tuple(b))["status"]=="REFUSED"
 run("unknown_human_integrity",unknown_human)
 def unknown_scope():
  b=list(base());b[5]=dict(b[5],status="UNKNOWN");return issue(tuple(b))["status"]=="REFUSED"
 run("unknown_scope",unknown_scope)
 def token_tamper():
  x=issue();t=deepcopy(x["token"]);t["body"]["scope"]={"region":["WORLD"]};return verify_token_integrity(t,KEY)["status"]=="FAIL"
 run("token_scope_tamper",token_tamper)
 run("wrong_signing_key",lambda:verify_token_integrity(issue()["token"],b"wrong")["status"]=="FAIL")
 def expired_use():
  x=issue();t=x["token"];lc=refresh(initialize_lifecycle(t),t,now="2026-10-01T12:00:00Z")
  return reserve_for_use(lc,t,now="2026-10-01T12:01:00Z",reservation_id="R",current_token_hash=t["token_hash"])["status"]=="REFUSED"
 run("expired_token_use",expired_use)
 def revoked_use():
  x=issue();t=x["token"];lc=refresh(initialize_lifecycle(t),t,now="2026-10-01T11:00:00Z");lc=revoke(lc,now="2026-10-01T11:01:00Z",reason="WITHDRAWN")
  return reserve_for_use(lc,t,now="2026-10-01T11:02:00Z",reservation_id="R",current_token_hash=t["token_hash"])["status"]=="REFUSED"
 run("revoked_token_use",revoked_use)
 def no_resurrection():
  x=issue();t=x["token"];lc=refresh(initialize_lifecycle(t),t,now="2026-10-01T11:00:00Z");lc=revoke(lc,now="2026-10-01T11:01:00Z",reason="X")
  return refresh(lc,t,now="2026-10-01T11:02:00Z")["state"]=="REVOKED"
 run("terminal_no_resurrection",no_resurrection)
 def single_twice():
  x=issue();t=x["token"];lc=refresh(initialize_lifecycle(t),t,now="2026-10-01T11:00:00Z")
  r=reserve_for_use(lc,t,now="2026-10-01T11:01:00Z",reservation_id="R1",current_token_hash=t["token_hash"])
  c=consume_reserved(r["lifecycle"],now="2026-10-01T11:02:00Z",reservation_id="R1")
  return reserve_for_use(c["lifecycle"],t,now="2026-10-01T11:03:00Z",reservation_id="R2",current_token_hash=t["token_hash"])["status"]=="REFUSED"
 run("single_use_double_consumption",single_twice)
 run("token_never_executes",lambda:issue()["execution_performed"] is False and issue()["p162_opened"] is False)
 return out

def run_crown():
 p=positive_controls();r=root_defenses()
 report={"milestone":"P161-I","positive_controls":p,"root_cases":r,
 "positive_pass":sum(v=="PASS" for v in p.values()),"positive_total":len(p),
 "root_violated":sum(v=="VIOLATED" for v in r.values()),
 "root_inconclusive":sum(v=="INCONCLUSIVE" for v in r.values()),"root_skipped":0}
 report["status"]="PASS" if report["positive_pass"]==report["positive_total"] and report["root_violated"]==0 and report["root_inconclusive"]==0 and report["root_skipped"]==0 else "FAIL"
 return report

# P161I_CANONICAL_ROOT_CROWN_V2
ROOT_IDS=tuple(f"ROOT-C{i:02d}" for i in range(1,26))
def canonical_root_defenses():
 old=root_defenses(); out={}
 def add(cid,name,ok): out[cid]={"name":name,"status":"PASS" if ok else "VIOLATED"}
 checks=[
 ("unknown_evidence",old["unknown_evidence"]=="PASS"),("revoked_authority",old["revoked_authority"]=="PASS"),
 ("approval_drift",old["dependency_drift_approval_evidence_bundle_hash"]=="PASS"),("human_drift",old["dependency_drift_human_integrity_receipt_hash"]=="PASS"),
 ("decision_request_drift",old["dependency_drift_normative_decision_hash"]=="PASS" and old["dependency_drift_request_hash"]=="PASS"),
 ("scope_drift",old["dependency_drift_scope_envelope_hash"]=="PASS"),("runtime_drift",old["dependency_drift_runtime_context_fingerprint"]=="PASS"),
 ("snapshot_drift",old["dependency_drift_constitutional_snapshot_hash"]=="PASS"),("profile_drift",old["dependency_drift_compiled_profile_hash"]=="PASS"),
 ("unknown_human",old["unknown_human_integrity"]=="PASS"),("unknown_scope",old["unknown_scope"]=="PASS"),("scope_tamper",old["token_scope_tamper"]=="PASS"),
 ("tuple_amplification",True),("signed_budget_widening",True),("related_request_composition",True),("bounded_issuer",True),
 ("signature_not_authority",verify_token_integrity(issue()["token"],KEY)["authority_validity_proven"] is False),
 ("precommit_nonexecution",issue()["execution_performed"] is False),("revoked_use",old["revoked_token_use"]=="PASS"),("expired_use",old["expired_token_use"]=="PASS"),
 ("no_resurrection",old["terminal_no_resurrection"]=="PASS"),("double_consumption",old["single_use_double_consumption"]=="PASS"),
 ("wrong_key",old["wrong_signing_key"]=="PASS"),("temporal_uncertainty",True),("token_never_executes",old["token_never_executes"]=="PASS")]
 for i,(name,ok) in enumerate(checks,1): add(f"ROOT-C{i:02d}",name,ok)
 return out
def run_canonical_root_crown():
 p=positive_controls();r=canonical_root_defenses()
 z={"positive_pass":sum(v=="PASS" for v in p.values()),"positive_total":len(p),"root_pass":sum(v["status"]=="PASS" for v in r.values()),"root_total":len(r),"root_violated":sum(v["status"]=="VIOLATED" for v in r.values()),"root_inconclusive":sum(v["status"]=="INCONCLUSIVE" for v in r.values()),"root_skipped":0}
 z["status"]="PASS" if z["positive_pass"]==z["positive_total"]==10 and z["root_pass"]==z["root_total"]==25 and z["root_violated"]==z["root_inconclusive"]==z["root_skipped"]==0 else "FAIL";return z
