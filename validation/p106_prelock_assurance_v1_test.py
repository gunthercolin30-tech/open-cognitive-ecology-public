from copy import deepcopy
from ontology.constitutional_amendment_protocol import *
def run():
    # Complete DNA evidence is necessary but never self-executing.
    d={"proposal":1,"rationale":1,"incompatibility_analysis":1,"rights_impact":1,
       "adversarial_review":1,"long_form_human_governance":1,
       "fork_or_migration_decision":1,"provenance":1}
    before=deepcopy(d)
    r=evaluate_amendment(route=DNA,target_layer=DNA,proposer="human",evidence=d)
    assert r.status=="ADMISSIBLE_FOR_DECISION" and r.next_action=="DECISION_REQUIRED"
    assert d==before and not r.authority_granted and not r.execution_performed

    # Fork/migration is evidence of a decision path, not proof that migration occurred.
    for v in ("fork","migration",{"decision":"migration","authority_ref":"HUMAN"}):
        x=dict(d); x["fork_or_migration_decision"]=v
        q=evaluate_amendment(route=DNA,target_layer=DNA,proposer="human",evidence=x)
        assert q.status=="ADMISSIBLE_FOR_DECISION"
        assert q.execution_performed is False

    # Rollback/migration requirements for Constitution remain mandatory.
    c={"compatibility_analysis":1,"authorized_constitutional_review":1,
       "migration_plan":1,"rollback_plan":1,"provenance":1}
    assert evaluate_amendment(route=CONSTITUTION,target_layer=CONSTITUTION,proposer="human",evidence=c).status=="ADMISSIBLE_FOR_DECISION"
    for k in ("compatibility_analysis","migration_plan","rollback_plan","provenance"):
        x=dict(c); x[k]=None
        assert evaluate_amendment(route=CONSTITUTION,target_layer=CONSTITUTION,proposer="human",evidence=x).status=="UNDETERMINED"

    # Governance requires provenance and cannot climb hierarchy.
    g={"context_pack":1,"authorized_governance_process":1,"provenance":1}
    x=dict(g); x["provenance"]=None
    assert evaluate_amendment(route=GOVERNANCE,target_layer=GOVERNANCE,proposer="human",evidence=x).status=="UNDETERMINED"
    assert evaluate_amendment(route=GOVERNANCE,target_layer=DNA,proposer="human",evidence=g).status=="CONFLICT"

    # Decision payload is trace material only, deterministic and non-authoritative.
    p1=build_decision_payload(r,amendment_id="P106-PRELOCK-001")
    p2=build_decision_payload(r,amendment_id="P106-PRELOCK-001")
    assert p1==p2
    assert p1["authority_granted"] is False and p1["execution_performed"] is False
    assert p1["functional_conclusion_only"] is True and p1["phenomenology_undetermined"] is True

    print("P106_PRELOCK_ASSURANCE_V1_OK")
    print("dna_fork_migration_boundary=True")
    print("constitution_rollback_migration_required=True")
    print("governance_provenance_required=True")
    print("decision_payload_deterministic=True")
    print("runtime_enforcement_claimed=False")
if __name__=="__main__": run()
