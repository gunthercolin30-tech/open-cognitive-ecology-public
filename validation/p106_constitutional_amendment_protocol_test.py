from ontology.constitutional_amendment_protocol import *
def run():
    m=manifest()
    assert m["does_not_execute_real_amendment"] and m["does_not_grant_authority"]
    assert m["acee_may_propose"] and not m["acee_may_ratify_dna_alone"]
    g={"context_pack":1,"authorized_governance_process":1,"provenance":1}
    assert evaluate_amendment(route=GOVERNANCE,target_layer=GOVERNANCE,proposer="human",evidence=g).status=="ADMISSIBLE_FOR_DECISION"
    assert evaluate_amendment(route=GOVERNANCE,target_layer=CONSTITUTION,proposer="human",evidence=g).status=="CONFLICT"
    c={"compatibility_analysis":1,"authorized_constitutional_review":1,"migration_plan":1,"rollback_plan":1,"provenance":1}
    assert evaluate_amendment(route=CONSTITUTION,target_layer=CONSTITUTION,proposer="human",evidence=c).status=="ADMISSIBLE_FOR_DECISION"
    assert evaluate_amendment(route=CONSTITUTION,target_layer=DNA,proposer="human",evidence=c).status=="CONFLICT"
    d={"proposal":1,"rationale":1,"incompatibility_analysis":1,"rights_impact":1,"adversarial_review":1,
       "long_form_human_governance":1,"fork_or_migration_decision":1,"provenance":1}
    a=evaluate_amendment(route=DNA,target_layer=DNA,proposer="ACEE",evidence=d)
    assert a.status=="ADMISSIBLE_FOR_DECISION" and not a.authority_granted and not a.execution_performed
    bad=dict(d); bad["acee_solo_ratification"]=True
    assert evaluate_amendment(route=DNA,target_layer=DNA,proposer="ACEE",evidence=bad).status=="REJECTED"
    missing=dict(d); missing["rights_impact"]=False
    assert evaluate_amendment(route=DNA,target_layer=DNA,proposer="human",evidence=missing).status=="UNDETERMINED"
    assert evaluate_amendment(route="UNKNOWN",target_layer=DNA,proposer="human",evidence=d).status=="UNDETERMINED"
    for _ in range(50):
        assert evaluate_amendment(route=DNA,target_layer=DNA,proposer="ACEE",evidence=d)==a
    payload=build_decision_payload(a,amendment_id="P106-TEST-001")
    assert payload["authority_granted"] is False and payload["execution_performed"] is False
    assert payload["functional_conclusion_only"] and payload["phenomenology_undetermined"]
    print("P106_CONSTITUTIONAL_AMENDMENT_PROTOCOL_TEST_OK")
    print("deterministic_replays=50")
    print("functional_conclusion_only=True")
    print("phenomenology_undetermined=True")
if __name__=="__main__": run()
