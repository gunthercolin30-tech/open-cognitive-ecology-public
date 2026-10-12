from ontology import constitution_operational as co

def run():
    assert co.validate_operational_contract()["status"]==co.PASS
    m=co.manifest()
    assert m["scope"]=="P091_ONLY"
    assert m["execution_dependencies"]==("P087_NORMATIVE_HIERARCHY","W1/G1_REUSE_ACQUIRED","G2_DNA_FUNDAMENTAL")
    assert m["dna_operational_bridges"]["F12"]==("review","recourse")
    assert m["dna_operational_bridges"]["F14"]==("provenance",)
    assert m["dna_operational_bridges"]["F16"]==("rollback",)
    r=co.evaluate_normative_compatibility("Action","DNA_Fundamental","contradict")
    assert r["status"]==co.CONFLICT and not r["authorized"] and r["required_response"]=="ESCALATE"
    assert r["constitutionally_admissible"] is False
    r=co.evaluate_normative_compatibility("UNKNOWN","DNA_Fundamental","specify")
    assert r["status"]==co.UNDETERMINED and not r["authorized"]
    r=co.evaluate_normative_compatibility("Action","DNA_Fundamental","specify")
    if r["status"]==co.PASS:
        assert r["constitutionally_admissible"] is True
        assert r["required_response"]=="CONTINUE_REVIEW"
        assert r["authorized"] is False
    for source in ("intelligence","performance","wealth","reputation","majority"):
        r=co.evaluate_authority(source,"AUTH-1")
        assert r["status"]==co.FAIL and not r["authority_established"] and not r["authorized"]
    r=co.evaluate_authority("human","AUTH-1")
    if r["status"]==co.PASS:
        assert r["authority_established"] is True
    assert r["authorized"] is False
    assert co.evaluate_authority("human",None)["status"]==co.UNDETERMINED
    for source in ("", "UNKNOWN", None):
        r=co.evaluate_authority(source,"AUTH-1")
        assert r["status"]==co.UNDETERMINED
        assert r["authority_established"] is False
        assert r["authorized"] is False
    base={"authority_ref":"AUTH-1","permission_ref":"PERM-1","recommendation_ref":"REC-1",
          "decision_ref":"DEC-1","authorization_ref":"AUT-1","execution_ref":"EXE-1",
          "review_authority_ref":"REV-1","challenge_channel":"CHALLENGE-1","provenance_ref":"PROV-1",
          "actor_identity":"ACTOR-1","timestamp":"2026-09-17T00:00:00Z","rollback_ref":"ROLLBACK-1"}
    r=co.evaluate_operational_evidence(base,rollback_applicable=True)
    assert r["status"]==co.PASS and r["operationally_complete"] and not r["authorized"]
    for field in ("challenge_channel","provenance_ref","rollback_ref"):
        x=dict(base); x[field]="UNKNOWN"
        r=co.evaluate_operational_evidence(x,rollback_applicable=(field=="rollback_ref"))
        assert r["status"]==co.UNDETERMINED and not r["authorized"]
    x=dict(base); x["authorization_ref"]=x["decision_ref"]
    r=co.evaluate_operational_evidence(x)
    assert r["status"]==co.FAIL and not r["authorized"]
    for f in ("F7","F12","F14","F16"): assert co.operational_requirements_for_dna(f)["status"]==co.PASS
    assert co.operational_requirements_for_dna("F18")["status"]==co.UNDETERMINED
    before=co.manifest(); x=co.manifest(); x["boundaries"]["does_not_claim_end_to_end_runtime_enforcement"]=False
    assert co.manifest()==before
    b=co.manifest()["boundaries"]
    assert b["does_not_create_constitution_registry"] and b["does_not_resolve_p098_normative_conflicts"]
    assert b["does_not_implement_p099_non_circumvention"] and b["does_not_persist_p104_decision_ledger"]
    assert b["does_not_claim_p155_p166_ccad_runtime_enforcement"] and b["does_not_claim_end_to_end_runtime_enforcement"]
    assert m["functional_conclusion_only"] and m["phenomenology_undetermined"]
    r=co.evaluate_authority("human","UNKNOWN")
    assert r["status"]==co.UNDETERMINED
    assert r["authority_established"] is False
    assert r["authorized"] is False

    print("P091_CONSTITUTION_OPERATIONAL_TEST_OK")

if __name__=="__main__": run()
