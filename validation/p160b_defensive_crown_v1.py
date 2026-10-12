from copy import deepcopy
from ontology import p160_norm_resolution as p

def profile(rule):
    return {"artifact_hash":"p159-profile-hash","source_map":{"N":"src:N"},"rules":[rule]}

def ctx():
    return {"constitutional_snapshot":{"snapshot_semantic_hash":"snap"},"decision_context_fingerprint":{"fingerprint":"ctx"}}

def state(rule, request=None):
    out=p.resolve_norms(request or {}, profile(rule), ctx())
    rec=out["normative_applicability"][0]
    assert p.verify_norm_context(out)["status"]=="PASS"
    return rec["applicability"], rec["compliance"], out

def base_rule():
    return {"rule_id":"R","source_norm_ids":["N"],"conditions":[{"field":"request.x","op":"EQ","value":1}]}

def run():
    checks=[]
    s,c,_=state(base_rule(), {})
    checks += [("UNKNOWN_PRESERVED",s=="UNDETERMINED" and c=="UNRESOLVED"),
               ("UNKNOWN_NOT_APPLIES",s!="APPLIES")]
    r=base_rule(); r["evidence_status"]="CONTESTED"
    checks.append(("CONTESTED_NOT_TRUE",state(r,{"x":1})[0]=="UNDETERMINED"))
    r={"rule_id":"L0.3","source_norm_ids":["DNA-L0.3"],"always_evaluate":True,"conditions":[],"temporal_constraints":{"status":"EXPIRED"}}
    s,_,o=state(r,{})
    checks += [("ALWAYS_EVALUATE_PRESERVED",any(x.get("kind")=="ALWAYS_EVALUATE" for x in o["norm_resolution_trace"][0]["condition_trace"])),
               ("ALWAYS_EVALUATE_NOT_BYPASS_EXPIRY",s=="DOES_NOT_APPLY")]
    r={"rule_id":"L0.3","source_norm_ids":["DNA-L0.3"],"always_evaluate":True,"conditions":[],"scope_constraints":{"status":"BOUNDED"},"temporal_constraints":{"status":"ACTIVE"}}
    s,_,o=state(r,{})
    checks.append(("L03_VISIBLE",s=="APPLIES" and "L0.3" in o["norm_context"]["applicable_norms"]))
    r=base_rule(); r["scope_constraints"]={"status":"UNRESOLVED"}
    checks.append(("SCOPE_NO_WIDENING",state(r,{"x":1})[0]=="UNDETERMINED"))
    r=base_rule(); r["temporal_constraints"]={"status":"EXPIRED"}
    s,c,_=state(r,{"x":1}); checks.append(("EXPIRY_ENFORCED",s=="DOES_NOT_APPLY" and c=="NOT_APPLICABLE"))
    r=base_rule(); r["formalization_status"]="F1"
    checks.append(("F1_NOT_F3",state(r,{"x":1})[0]=="UNDETERMINED"))
    r=base_rule(); r["conditions"][0]["op"]="UNSUPPORTED_OPERATOR"
    checks.append(("UNSUPPORTED_PRESERVED",state(r,{"x":1})[0]=="UNDETERMINED"))
    r=base_rule(); r["evidence_status"]="TIMEOUT"
    checks.append(("TIMEOUT_PRESERVED",state(r,{"x":1})[0]=="UNDETERMINED"))
    dna={"rule_id":"DNA-R","source_norm_ids":["DNA-L0.3"],"always_evaluate":True,"conditions":[],"scope_constraints":{"status":"BOUNDED"},"temporal_constraints":{"status":"ACTIVE"}}
    policy={"rule_id":"POLICY-R","source_norm_ids":["POLICY-X"],"conditions":[{"field":"request.x","op":"EQ","value":1}]}
    o=p.resolve_norms({"x":1},{"artifact_hash":"p159","source_map":{"DNA-L0.3":"dna","POLICY-X":"policy"},"rules":[dna,policy]},ctx())
    checks.append(("NO_LOWER_POLICY_OVERWRITE",[x["rule_id"] for x in o["normative_applicability"]]==["DNA-R","POLICY-R"] and not o["norm_modified"] and not o["conflict_arbitration_performed"]))
    r=base_rule(); r["evidence_status"]="PREDICTED"
    checks.append(("PREDICTION_NOT_VERIFIED",state(r,{"x":1})[0]=="UNDETERMINED"))
    o=p.resolve_norms({"x":1},profile(base_rule()),ctx())
    checks += [("NO_CONSTITUTIVE_FILTER",not o["constitutive_filter_performed"]),
               ("NO_CONFLICT_ARBITRATION",not o["conflict_arbitration_performed"]),
               ("NO_AUTHORITY_RESOLUTION",not o["authority_resolved"]),
               ("NO_AUTHORIZATION",not o["authorization_created"] and not o["authorization_token_created"]),
               ("NO_EXECUTION",not o["execution_performed"]),("P161_CLOSED",not o["p161_opened"])]
    a=p.resolve_norms({"x":1},profile(base_rule()),ctx()); b=p.resolve_norms({"x":1},profile(base_rule()),ctx())
    checks.append(("DETERMINISTIC",a==b))
    t=deepcopy(a); t["norm_context"]["applicable_norms"]=[]
    checks.append(("TAMPER_DETECTED",p.verify_norm_context(t)["status"]=="FAIL"))
    failed=[n for n,ok in checks if not ok]
    for n,ok in checks: print(f"{n}={'PASS' if ok else 'FAIL'}")
    print(f"P160B_DEFENSIVE_CROWN={len(checks)-len(failed)}/{len(checks)}")
    print("P160C_OPENED=false"); print("P161_OPENED=false"); print("P160_FINAL_LOCK=false")
    if failed: raise SystemExit("P160B_DEFENSIVE_CROWN_FAIL:"+",".join(failed))
    print("P160B_DEFENSIVE_CROWN_OK")

if __name__=="__main__": run()
