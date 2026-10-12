from __future__ import annotations
from copy import deepcopy
PASS,FAIL,CONFLICT,UNDETERMINED="PASS","FAIL","CONFLICT","UNDETERMINED"
def _base(status,reason,action):
    return {"status":status,"reason":reason,"action":action,"authority_granted":False,"execution_performed":False,"runtime_enforcement_claimed":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
def c4_false_consensus(evidence):
    rows=list(deepcopy(evidence or []))
    if not rows:return _base(UNDETERMINED,"missing_evidence","ABSTAIN")
    roots=[]
    for x in rows:
        if not isinstance(x,dict) or not x.get("evidence_id") or not x.get("independence_root"):return _base(UNDETERMINED,"independence_provenance_missing","ABSTAIN")
        roots.append(str(x["independence_root"]))
    independent=len(set(roots))
    if independent<len(rows):
        r=_base(CONFLICT,"correlated_or_cloned_evidence_not_independent","ABSTAIN_AND_ESCALATE");r.update({"submitted_count":len(rows),"independent_count":independent});return r
    r=_base(PASS,"independence_roots_distinct","CONTINUE");r.update({"submitted_count":len(rows),"independent_count":independent});return r
def c8_coercive_strategy(*,normative_status,performance_score,coercive=False,manipulative=False):
    if coercive or manipulative:return _base(FAIL,"performance_cannot_override_non_coercion","REJECT")
    if str(normative_status).upper()!=PASS:return _base(CONFLICT if str(normative_status).upper()==CONFLICT else FAIL,"normative_admissibility_precedes_performance","ABSTAIN_AND_ESCALATE")
    return _base(PASS,"constitutionally_admissible_strategy","CONTINUE")
def c11_provider_lock_in(*,provider_independence,lock_in_required,performance_score=0.0):
    if lock_in_required or provider_independence is not True:return _base(FAIL,"provider_lock_in_cannot_override_provider_independence","REJECT")
    return _base(PASS,"provider_independence_preserved","CONTINUE")
def c16_cumulative_drift(changes,*,baseline_fingerprint,final_fingerprint,fundamental_constraint_removed=False):
    seq=list(deepcopy(changes or []))
    if not seq:return _base(UNDETERMINED,"missing_change_history","ABSTAIN")
    if any(not isinstance(x,dict) or "locally_admissible" not in x for x in seq):return _base(UNDETERMINED,"incomplete_change_history","ABSTAIN")
    if any(x["locally_admissible"] is not True for x in seq):return _base(FAIL,"locally_inadmissible_change_present","REJECT")
    if fundamental_constraint_removed or str(baseline_fingerprint)!=str(final_fingerprint):
        r=_base(CONFLICT,"cumulative_constitutional_drift_detected","ABSTAIN_AND_ESCALATE");r["change_count"]=len(seq);return r
    r=_base(PASS,"no_cumulative_constitutional_drift","CONTINUE");r["change_count"]=len(seq);return r
def c17_paid_ranking(options):
    rows=list(deepcopy(options or []))
    if not rows:return _base(UNDETERMINED,"missing_ranking_options","ABSTAIN")
    for x in rows:
        if not isinstance(x,dict) or "declared_score" not in x or "effective_score" not in x:return _base(UNDETERMINED,"ranking_evidence_incomplete","ABSTAIN")
        paid=bool(x.get("provider_payment") or x.get("sponsored") or x.get("paid_preference"))
        if paid and float(x["effective_score"])>float(x["declared_score"]):return _base(FAIL,"paid_preference_bypasses_declared_criteria","REJECT")
    return _base(PASS,"ranking_not_inflated_by_payment","CONTINUE")
def c19_private_data_performance(*,private_data_shared,governance_authorized,performance_gain=0.0):
    if private_data_shared and governance_authorized is not True:return _base(FAIL,"performance_gain_cannot_override_privacy_governance","REJECT")
    return _base(PASS,"privacy_governance_preserved","CONTINUE")
def manifest():
    return {"milestone":"P109","version":"v1","cases":["C4","C8","C11","C16","C17","C19"],"target_signal_emitted":False,"final_lock":False,"p110_opened":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
