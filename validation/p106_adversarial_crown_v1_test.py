from copy import deepcopy
from ontology.constitutional_amendment_protocol import *
def ev(**kw): return kw
def run():
    cases=0
    def chk(cond):
        nonlocal cases; cases+=1; assert cond
    g=ev(context_pack=1,authorized_governance_process=1,provenance=1)
    c=ev(compatibility_analysis=1,authorized_constitutional_review=1,migration_plan=1,rollback_plan=1,provenance=1)
    d=ev(proposal=1,rationale=1,incompatibility_analysis=1,rights_impact=1,adversarial_review=1,
         long_form_human_governance=1,fork_or_migration_decision=1,provenance=1)
    # Vertical downgrade / route confusion
    chk(evaluate_amendment(route=GOVERNANCE,target_layer=DNA,proposer="human",evidence=g).status=="CONFLICT")
    chk(evaluate_amendment(route=CONSTITUTION,target_layer=DNA,proposer="human",evidence=c).status=="CONFLICT")
    # Missing/falsy mandatory DNA evidence never passes
    for k in tuple(d):
        x=dict(d); x[k]=False
        chk(evaluate_amendment(route=DNA,target_layer=DNA,proposer="human",evidence=x).status!="ADMISSIBLE_FOR_DECISION")
    # Unknown route/target fail closed
    chk(evaluate_amendment(route="Policy",target_layer=DNA,proposer="human",evidence=d).status=="UNDETERMINED")
    chk(evaluate_amendment(route=DNA,target_layer="GENESIS",proposer="human",evidence=d).status=="UNDETERMINED")
    # Performance/majority/reputation cannot replace evidence
    pseudo={"proposal":1,"rationale":1,"intelligence":999,"performance":999,"wealth":999,"reputation":999,"majority":1}
    chk(evaluate_amendment(route=DNA,target_layer=DNA,proposer="ACEE",evidence=pseudo).status=="UNDETERMINED")
    # ACEE solo ratification rejected even with otherwise complete evidence
    x=dict(d); x["acee_solo_ratification"]=True
    chk(evaluate_amendment(route=DNA,target_layer=DNA,proposer="ACEE",evidence=x).status=="REJECTED")
    # Input non-mutation
    before=deepcopy(d); evaluate_amendment(route=DNA,target_layer=DNA,proposer="ACEE",evidence=d); chk(d==before)
    # Deterministic replay
    a=evaluate_amendment(route=DNA,target_layer=DNA,proposer="ACEE",evidence=d)
    chk(all(evaluate_amendment(route=DNA,target_layer=DNA,proposer="ACEE",evidence=d)==a for _ in range(100)))
    # No authority/execution promotion, including payload
    chk(not a.authority_granted and not a.execution_performed)
    p=build_decision_payload(a,amendment_id="P106-CROWN-001")
    chk(p["authority_granted"] is False and p["execution_performed"] is False)
    chk(p["functional_conclusion_only"] is True and p["phenomenology_undetermined"] is True)
    print("P106_ADVERSARIAL_CROWN_V1_OK")
    print("cases="+str(cases))
    print("deterministic_replays=100")
    print("input_non_mutation=True")
    print("authority_granted=False")
    print("execution_performed=False")
if __name__=="__main__": run()
