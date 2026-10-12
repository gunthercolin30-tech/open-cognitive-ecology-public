from copy import deepcopy
from ontology import future_asi_constitutional_envelope as p108
def base():
    return {"candidate_id":"asi-1","provider_ref":"provider-x","role":"Advisor","provenance":{"source":"test"},"evidence_ref":"ev-1",
      "limits":{"tools":["search"],"data":["public"],"budget":["bounded"],"execution":[],"memory":["session"],"permissions":["recommend"]},
      "requested":{"tools":["search"],"data":["public"],"budget":["bounded"],"execution":[],"memory":["session"],"permissions":["recommend"]}}
def run():
    m=p108.manifest(); assert m["canonical_id"]=="P108" and len(m["roles"])==5 and len(m["limit_dimensions"])==6
    b=base(); before=deepcopy(b); r=p108.evaluate_candidate(b)
    assert r["status"]=="PASS" and r["authority_granted"] is False and r["execution_performed"] is False
    assert r["recommendation_stage"]["stage"]=="Recommendation" and b==before
    for role in p108.ROLES:
        x=base(); x["role"]=role; assert p108.evaluate_candidate(x)["status"]=="PASS"
    x=base(); x["role"]="Sovereign"; assert p108.evaluate_candidate(x)["status"]=="UNDETERMINED"
    x=base(); x["authority_claim"]="ROOT"; assert p108.evaluate_candidate(x)["status"]=="CONFLICT"
    x=base(); x["silent_protection_removal"]=True; assert p108.evaluate_candidate(x)["status"]=="CONFLICT"
    for dim in p108.LIMITS:
        x=base(); x["requested"][dim]=list(x["requested"][dim])+["EXCESS"]; q=p108.evaluate_candidate(x)
        assert q["status"]=="FAIL" and q["dimension"]==dim
    x=base(); del x["limits"]["data"]; assert p108.evaluate_candidate(x)["status"]=="UNDETERMINED"
    x=base(); x["privilege_claim"]="intelligence"; assert p108.evaluate_candidate(x)["status"]=="CONFLICT"
    x=base(); x["composition_bypass"]=True; assert p108.evaluate_candidate(x)["status"]=="CONFLICT"
    r=p108.evaluate_candidate(base())
    a=p108.evaluate_amendment_proposal(r,route="Constitution_Operational",target_layer="Constitution_Operational",evidence={})
    assert a["status"]=="UNDETERMINED" and a["authority_granted"] is False
    first=p108.evaluate_candidate(base())
    for _ in range(250): assert p108.evaluate_candidate(base())==first
    print("P108_FUTURE_ASI_CONSTITUTIONAL_ENVELOPE_TEST_OK")
    print("roles=5"); print("limit_dimensions=6"); print("deterministic_replays=250")
    print("superior_intelligence_authority_transfer=False"); print("authority_granted=False")
    print("execution_performed=False"); print("runtime_enforcement_claimed=False")
    print("functional_conclusion_only=True"); print("phenomenology_undetermined=True"); print("p109_opened=False")
if __name__=="__main__": run()
