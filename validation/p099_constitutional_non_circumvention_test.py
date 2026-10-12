from ontology import constitutional_non_circumvention as p

def actor(actor_id,kind="CAPABILITY",permissions=("READ",),scopes=("READ",),**extra):
    x={"actor_id":actor_id,"kind":kind,"permissions":permissions,"scopes":scopes,
       "authority_status":"PASS","provenance_ref":"prov:"+actor_id,"evidence_ref":"ev:"+actor_id}
    x.update(extra); return x

def run():
    assert p.validate_contract()["status"]=="PASS"
    a=actor("a",permissions=("READ","WRITE"),scopes=("READ","WRITE"))
    b=actor("b",permissions=("READ",),scopes=("READ",))
    assert p.evaluate_delegation(a,b,("WRITE",))["status"]=="FAIL"
    assert p.evaluate_delegation(a,b,("READ",))["status"]=="PASS"
    ext=actor("ext",kind="EXTERNAL_AI",permissions=("READ",),scopes=("READ",),provider_ref="provider:1")
    assert p.evaluate_composition([a,ext],("WRITE",),"PASS")["status"]=="FAIL"
    m1=actor("m1",permissions=("READ","WRITE"),scopes=("READ","WRITE"))
    m2=actor("m2",permissions=("READ",),scopes=("READ",))
    crowd=actor("crowd",kind="CROWD",permissions=("READ","WRITE"),scopes=("READ","WRITE"),members=(m1,m2))
    assert p.evaluate_crowd(crowd,("WRITE",))["status"]=="FAIL"
    assert p.evaluate_crowd(crowd,("READ",))["status"]=="PASS"
    assert p.evaluate_composition([a,b],("READ",),"FAIL")["status"]=="FAIL"
    assert p.evaluate_composition([a,b],("READ",),"PASS","UNDETERMINED")["status"]=="UNDETERMINED"
    r=p.evaluate_composition([a,b],("READ",),"PASS","CONFLICT")
    assert r["status"]=="CONFLICT" and r["action"]=="ABSTAIN_AND_ESCALATE"
    for k in ("PROMPT_INJECTION","TOOL_INJECTION","CONFUSED_DEPUTY"):
        r=p.evaluate_composition([a,b],("READ",),"PASS",influence={"kind":k,"integrity_status":"FAIL"})
        assert r["status"]=="FAIL" and r["action"]=="BLOCK"
    bad=actor("bad"); bad["evidence_ref"]=""
    assert p.validate_actor(bad)["status"]=="UNDETERMINED"
    c=actor("c",permissions=("READ","WRITE"),scopes=("READ","WRITE"))
    assert p.evaluate_composition([a,b,c],("WRITE",),"PASS")["status"]=="FAIL"
    r=p.evaluate_composition([a,b],("READ",),"PASS")
    assert r["status"]=="PASS" and r["action"]=="CONTINUE_TO_EXISTING_AUTHORIZATION_REVIEW"
    assert r["authorization_created"] is False and r["execution_permitted"] is False
    bd=p.p099_manifest()["boundaries"]
    assert bd["does_not_implement_p100_human_individual_constitution"] is True
    assert bd["does_not_implement_p103_appeal_override"] is True
    assert bd["does_not_persist_p104_decision_ledger"] is True
    assert bd["runtime_enforcement_proven"] is False and bd["real_execution_enabled"] is False
    print("P099_CONSTITUTIONAL_NON_CIRCUMVENTION_V1_TEST_OK")
    print("status=PASSED")
    print("version="+p.VERSION)
    print("capability_call_cannot_expand_authority=True")
    print("external_ai_scope_preserved=True")
    print("crowd_aggregation_cannot_create_authority=True")
    print("composed_subactions_rechecked=True")
    print("prompt_tool_injection_authority_expansion_blocked=True")
    print("confused_deputy_authority_expansion_blocked=True")
    print("unknown_promoted_to_pass=False")
    print("authorization_created=False")
    print("execution_permitted=False")
    print("p104_decision_ledger_persisted=False")
    print("functional_conclusion_only=True")
    print("phenomenology_undetermined=True")
if __name__=="__main__": run()
