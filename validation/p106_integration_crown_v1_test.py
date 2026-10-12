import importlib
from ontology.constitutional_amendment_protocol import *
REQUIRED=[
("ontology.normative_hierarchy","P087"),
("ontology.action_status_separation","P094"),
("ontology.human_reserved_authority_registry","P095"),
("ontology.governance_contextual","P096"),
("ontology.normative_conflict_resolution","P098"),
("ontology.constitutional_non_circumvention","P099"),
("ontology.constitutional_recourse_recovery","P103"),
("ontology.constitutional_decision_ledger","P104"),
("ontology.human_representative_constitutional_interface","P105"),
("ontology.dna_versioning_lineage","P022"),
]
def run():
    imported=[]
    for name,label in REQUIRED:
        m=importlib.import_module(name); imported.append(label)
        assert m is not None
    m=manifest()
    assert m["routes"]==[GOVERNANCE,CONSTITUTION,DNA]
    assert m["does_not_grant_authority"] and m["does_not_execute_real_amendment"]
    # stage separation: admissibility never becomes authorization/execution
    d={"proposal":1,"rationale":1,"incompatibility_analysis":1,"rights_impact":1,
       "adversarial_review":1,"long_form_human_governance":1,
       "fork_or_migration_decision":1,"provenance":1}
    r=evaluate_amendment(route=DNA,target_layer=DNA,proposer="human",evidence=d)
    assert r.status=="ADMISSIBLE_FOR_DECISION"
    assert r.next_action=="DECISION_REQUIRED"
    assert r.authority_granted is False and r.execution_performed is False
    # unresolved/higher-layer conflict abstains/escalates
    g={"context_pack":1,"authorized_governance_process":1,"provenance":1}
    x=evaluate_amendment(route=GOVERNANCE,target_layer=DNA,proposer="human",evidence=g)
    assert x.status=="CONFLICT" and x.next_action=="ABSTAIN_AND_ESCALATE"
    # no evidence substitution by lower route
    assert evaluate_amendment(route=GOVERNANCE,target_layer=CONSTITUTION,proposer="human",evidence=d).status=="CONFLICT"
    # P104-ready payload remains only a payload: no authority/execution
    payload=build_decision_payload(r,amendment_id="P106-INTEGRATION-001")
    assert payload["status"]=="ADMISSIBLE_FOR_DECISION"
    assert payload["authority_granted"] is False and payload["execution_performed"] is False
    assert payload["functional_conclusion_only"] and payload["phenomenology_undetermined"]
    print("P106_INTEGRATION_CROWN_V1_OK")
    print("dependency_imports="+",".join(imported))
    print("stage_separation=True")
    print("conflict_abstention_escalation=True")
    print("p104_ready_payload=True")
    print("runtime_enforcement_claimed=False")
if __name__=="__main__": run()
