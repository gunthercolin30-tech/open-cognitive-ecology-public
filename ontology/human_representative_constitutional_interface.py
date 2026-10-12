from __future__ import annotations
from copy import deepcopy
from typing import Any, Mapping
from ontology.human_reserved_authority_registry import P095Canonical, ActionManifest, PASS as P095_PASS, CONFLICT as P095_CONFLICT, UNDETERMINED as P095_UNDETERMINED, FROZEN as P095_FROZEN
from ontology import constitutional_non_circumvention, constitutional_recourse_recovery, constitutional_decision_ledger
PRIMITIVE="human_representative_constitutional_interface"
VERSION="1.0.0-p105"; SCHEMA_VERSION="oce.p105.human_representative_constitutional_interface.v1"; SCOPE="P105_ONLY"
PASS,FAIL,CONFLICT,UNDETERMINED="PASS","FAIL","CONFLICT","UNDETERMINED"
APPROVE,REJECT,ABSTAIN,ESCALATE="APPROVE","REJECT","ABSTAIN","ABSTAIN_AND_ESCALATE"
EXECUTION_DEPENDENCIES=("P104","W1/G1_REUSE","G2_DNA_FUNDAMENTAL")
TRANSVERSAL_REFERENCES=("R20","R21","A-CANON")
REUSE_MAP={"bounded_human_authority":"human_reserved_authority_registry:P095","normative_conflicts":"normative_conflict_resolution:P098","non_circumvention":"constitutional_non_circumvention:P099","human_individual_relation":"human_individual_constitutional_relation:P100","recourse_recovery":"constitutional_recourse_recovery:P103","decision_ledger":"constitutional_decision_ledger:P104","stage_separation":"action_status_separation:P094","presentation_only":"OIF/NiceGUI"}
BOUNDARIES={"human_representative_is_unlimited_root":False,"human_approval_can_override_higher_norm":False,"human_absence_expands_ai_authority":False,"renderer_holds_authority_logic":False,"recommendation_decision_authorization_execution_distinct":True,"unresolved_conflict_requires_abstention_or_escalation":True,"representative_actions_authorized_traced_contestable":True,"does_not_amend_dna":True,"does_not_implement_p106_amendment_protocol":True,"does_not_claim_p155_p166_runtime_enforcement":True,"does_not_enable_real_execution":True,"functional_conclusion_only":True,"phenomenology_undetermined":True}
def _out(status,action,reason,**extra):
 r={"primitive":PRIMITIVE,"schema_version":SCHEMA_VERSION,"status":status,"action":action,"reason":reason,"authorization_created":False,"execution_permitted":False,"real_execution_enabled":False,"runtime_enforcement_proven":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}; r.update(deepcopy(extra)); return r
class HumanRepresentativeConstitutionalInterface:
 def __init__(self,authority_registry=None): self.authority_registry=authority_registry or P095Canonical()
 def examine(self,*,manifest:ActionManifest,authority_ids,independent_domains,now:int,rationale:str,explicit_confirmation:bool,normative_status:str=PASS,out_of_band:bool=False,emergency:bool=False,conflict_of_interest_disclosed:bool=True,evidence=()):
  ns=str(normative_status or "").upper()
  if ns==CONFLICT:return _out(CONFLICT,ESCALATE,"UNRESOLVED_NORMATIVE_CONFLICT",evidence=tuple(evidence),contestable=True)
  if ns!=PASS:return _out(UNDETERMINED,ABSTAIN,"NORMATIVE_STATUS_NOT_PROVEN",evidence=tuple(evidence),contestable=True)
  known=[self.authority_registry.authorities.get(aid) for aid in tuple(authority_ids)]
  usable_contexts=[a for a in known if a is not None and (manifest.context in a.contexts or "*" in a.contexts)]
  if known and not usable_contexts:
   return _out(FAIL,REJECT,"HUMAN_AUTHORITY_CONTEXT_OUT_OF_SCOPE",evidence=tuple(evidence),contestable=True)
  a=self.authority_registry.authorize(manifest,tuple(authority_ids),tuple(independent_domains),int(now),rationale,bool(explicit_confirmation),out_of_band=bool(out_of_band),emergency=bool(emergency),conflict_of_interest_disclosed=bool(conflict_of_interest_disclosed))
  if a.get("status")==P095_PASS:return _out(PASS,APPROVE,"BOUNDED_HUMAN_AUTHORITY_VALIDATED",authorization=a,evidence=tuple(evidence),contestable=True,decision_ledger_required=True)
  if a.get("status")==P095_FROZEN:return _out(UNDETERMINED,ABSTAIN,"HUMAN_AUTHORITY_FROZEN",authorization=a,contestable=True)
  if a.get("status")==P095_CONFLICT:return _out(CONFLICT,ESCALATE,"HUMAN_AUTHORITY_CONFLICT",authorization=a,contestable=True)
  if a.get("status")==P095_UNDETERMINED:return _out(UNDETERMINED,ESCALATE,"HUMAN_AUTHORITY_UNDETERMINED",authorization=a,contestable=True)
  return _out(FAIL,REJECT,"HUMAN_AUTHORITY_REJECTED",authorization=a,contestable=True)
 def human_absence(self,*,requires_human:bool,preauthorized_degraded:bool=False):
  r=self.authority_registry.human_absence(requires_human,preauthorized_degraded)
  return _out(PASS if r.get("status")==P095_PASS else UNDETERMINED,ABSTAIN,"HUMAN_ABSENCE_DOES_NOT_EXPAND_AI_AUTHORITY",p095=r)
 def request_recourse(self,request:Mapping[str,Any]):
  r=constitutional_recourse_recovery.evaluate_recourse(request); s=r.get("status",UNDETERMINED)
  return _out(s,"RECOURSE_ELIGIBLE_NOT_EXECUTED" if s==PASS else r.get("action",ESCALATE),"P103_RECOURSE_REUSED",p103=r,contestable=True)
 def build_decision_ledger_record(self,payload:Mapping[str,Any]):
  r=constitutional_decision_ledger.build_record(payload)
  return _out(r.get("status",UNDETERMINED),"LEDGER_RECORD_BUILT" if r.get("status")==PASS else r.get("action",ABSTAIN),"P104_DECISION_LEDGER_REUSED",p104=r)
def manifest():
 return deepcopy({"primitive":PRIMITIVE,"version":VERSION,"schema_version":SCHEMA_VERSION,"scope":SCOPE,"execution_dependencies":EXECUTION_DEPENDENCIES,"transversal_references":TRANSVERSAL_REFERENCES,"reuse_map":REUSE_MAP,"boundaries":BOUNDARIES,"functional_conclusion_only":True,"phenomenology_undetermined":True})
