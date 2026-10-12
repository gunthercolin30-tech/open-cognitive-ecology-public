from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Mapping, Tuple
PRIMITIVE="constitutional_amendment_protocol"; VERSION="P106-v1"
SCHEMA="oce.p106.constitutional_amendment_protocol.v1"
GOVERNANCE="Governance_Contextual"; CONSTITUTION="Constitution_Operational"; DNA="DNA_Fundamental"
KNOWN=(GOVERNANCE,CONSTITUTION,DNA)

@dataclass(frozen=True)
class AmendmentResult:
    status:str; route:str; next_action:str; missing_evidence:Tuple[str,...]
    authority_granted:bool=False; execution_performed:bool=False
    functional_conclusion_only:bool=True; phenomenology_undetermined:bool=True

def manifest()->Dict[str,Any]:
    return {"primitive":PRIMITIVE,"version":VERSION,"schema":SCHEMA,"routes":list(KNOWN),
    "does_not_execute_real_amendment":True,"does_not_grant_authority":True,
    "acee_may_propose":True,"acee_may_ratify_dna_alone":False,
    "governance_cannot_amend_constitution_or_dna":True,"constitution_cannot_amend_dna":True,
    "unknown_is_not_pass":True,"conflict_requires_abstention_or_escalation":True,
    "functional_conclusion_only":True,"phenomenology_undetermined":True}

def _missing(e:Mapping[str,Any], req:Iterable[str])->Tuple[str,...]:
    return tuple(k for k in req if not e.get(k))

def evaluate_amendment(*,route:str,target_layer:str,proposer:str,evidence:Mapping[str,Any])->AmendmentResult:
    if route not in KNOWN or target_layer not in KNOWN:
        return AmendmentResult("UNDETERMINED",route,"ABSTAIN_AND_ESCALATE",("known_route_and_target",))
    rank={GOVERNANCE:0,CONSTITUTION:1,DNA:2}
    if rank[target_layer]>rank[route]:
        return AmendmentResult("CONFLICT",route,"ABSTAIN_AND_ESCALATE",("authorized_higher_layer_process",))
    if route==GOVERNANCE:
        miss=_missing(evidence,("context_pack","authorized_governance_process","provenance"))
    elif route==CONSTITUTION:
        miss=_missing(evidence,("compatibility_analysis","authorized_constitutional_review","migration_plan","rollback_plan","provenance"))
    else:
        miss=_missing(evidence,("proposal","rationale","incompatibility_analysis","rights_impact",
            "adversarial_review","long_form_human_governance","fork_or_migration_decision","provenance"))
        if proposer.upper()=="ACEE" and evidence.get("acee_solo_ratification"):
            return AmendmentResult("REJECTED",route,"HUMAN_GOVERNANCE_REQUIRED",("independent_authorized_ratification",))
    return AmendmentResult("UNDETERMINED" if miss else "ADMISSIBLE_FOR_DECISION",route,
        "COMPLETE_EVIDENCE" if miss else "DECISION_REQUIRED",miss)

def build_decision_payload(result:AmendmentResult,*,amendment_id:str)->Dict[str,Any]:
    return {"schema":SCHEMA,"milestone":"P106","amendment_id":amendment_id,"route":result.route,
    "status":result.status,"next_action":result.next_action,"missing_evidence":list(result.missing_evidence),
    "authority_granted":False,"execution_performed":False,
    "functional_conclusion_only":True,"phenomenology_undetermined":True}
