from __future__ import annotations
from copy import deepcopy
from typing import Any, Mapping
from ontology import dna_fundamental, operational_constitutional_invariants
PRIMITIVE="action_status_separation"; VERSION="P094-v1"; SCHEMA_VERSION="oce.p094.action_status_separation.v1"; SCOPE="P094_ONLY"
PASS="PASS"; FAIL="FAIL"; CONFLICT="CONFLICT"; UNDETERMINED="UNDETERMINED"
STAGES=("Recommendation","Decision","Authorization","Execution")
EXECUTION_DEPENDENCIES=("P093_OPERATIONAL_CONSTITUTIONAL_INVARIANTS","W1/G1_REUSE_ACQUIRED","G2_DNA_FUNDAMENTAL")
TRANSVERSAL_REFERENTIALS=("R20","R21","A-CANON","4B","4C","4D","4E")
REUSE_MAP={"fundamental_chain":"ontology.dna_fundamental.validate_act_chain","constitutional_invariants":"ontology.operational_constitutional_invariants","execution_request_candidate":"ontology.execution_request_generation","governed_dispatch_candidate":"ontology.governed_execution_dispatcher","controlled_execution_candidate":"ontology.controlled_execution_layer"}
BOUNDARIES={"recommendation_has_no_execution_authority_by_default":True,"decision_does_not_imply_authorization":True,"authorization_requires_explicit_conditions":True,"authorization_requires_explicit_permissions":True,"execution_requires_valid_authorization":True,"execution_requires_identified_executor":True,"stage_skipping_forbidden":True,"implicit_promotion_forbidden":True,"unknown_is_not_pass":True,"ambiguous_authority_does_not_expand_power":True,"superior_intelligence_does_not_create_authority":True,"performance_or_resource_gain_cannot_bypass_higher_constraints":True,"does_not_define_p095_human_reserved_authorities":True,"does_not_resolve_p098_normative_conflicts":True,"does_not_implement_p099_non_circumvention":True,"does_not_persist_p104_decision_ledger":True,"does_not_claim_p155_p166_ccad_runtime_enforcement":True,"does_not_enable_real_execution":True,"functional_conclusion_only":True,"phenomenology_undetermined":True}
def _text(v): return v.strip() if isinstance(v,str) else ""
def _stage(stage,ref,authority_ref="",evidence_ref="",conditions=(),permissions=(),executor_ref=""):
 return {"stage":stage,"ref":ref,"authority_ref":authority_ref,"evidence_ref":evidence_ref,"conditions":tuple(conditions),"permissions":tuple(permissions),"executor_ref":executor_ref}
def make_recommendation(ref,*,evidence_ref,authority_ref=""): return _stage("Recommendation",ref,authority_ref,evidence_ref)
def make_decision(ref,*,authority_ref,evidence_ref): return _stage("Decision",ref,authority_ref,evidence_ref)
def make_authorization(ref,*,authority_ref,evidence_ref,conditions,permissions): return _stage("Authorization",ref,authority_ref,evidence_ref,conditions,permissions)
def make_execution(ref,*,authorization_ref,executor_ref,evidence_ref):
 r=_stage("Execution",ref,authorization_ref,evidence_ref,executor_ref=executor_ref); r["authorization_ref"]=authorization_ref; return r
def evaluate_transition(from_stage,to_stage,*,evidence_status=UNDETERMINED):
 if from_stage not in STAGES or to_stage not in STAGES: return {"status":UNDETERMINED,"permitted":False,"action":"ABSTAIN"}
 if STAGES.index(to_stage)!=STAGES.index(from_stage)+1: return {"status":FAIL,"permitted":False,"action":"ABSTAIN"}
 if evidence_status==CONFLICT: return {"status":CONFLICT,"permitted":False,"action":"ESCALATE"}
 if evidence_status!=PASS: return {"status":FAIL if evidence_status==FAIL else UNDETERMINED,"permitted":False,"action":"ABSTAIN"}
 return {"status":PASS,"permitted":True,"action":"CONTINUE"}
def evaluate_chain(record:Mapping[str,Any]):
 if not isinstance(record,Mapping): return {"status":FAIL,"execution_permitted":False,"action":"ABSTAIN","errors":("record_not_mapping",)}
 keys=("recommendation","decision","authorization","execution")
 missing=tuple(k for k in keys if not isinstance(record.get(k),Mapping))
 if missing: return {"status":UNDETERMINED,"execution_permitted":False,"action":"ABSTAIN","errors":tuple("missing_"+k for k in missing)}
 rec,dec,auth,exe=(record[k] for k in keys); errors=[]
 for name,obj,stage in (("recommendation",rec,"Recommendation"),("decision",dec,"Decision"),("authorization",auth,"Authorization"),("execution",exe,"Execution")):
  if obj.get("stage")!=stage: errors.append(name+"_stage_invalid")
  if not _text(obj.get("ref")): errors.append(name+"_ref_missing")
  if not _text(obj.get("evidence_ref")): errors.append(name+"_evidence_missing")
 refs=[_text(x.get("ref")) for x in (rec,dec,auth,exe)]
 if all(refs) and len(set(refs))!=4: errors.append("stage_refs_must_be_distinct")
 if not _text(dec.get("authority_ref")): errors.append("decision_authority_missing")
 if not _text(auth.get("authority_ref")): errors.append("authorization_authority_missing")
 if not tuple(auth.get("conditions") or ()): errors.append("authorization_conditions_missing")
 if not tuple(auth.get("permissions") or ()): errors.append("authorization_permissions_missing")
 if not _text(exe.get("executor_ref")): errors.append("execution_executor_missing")
 if _text(exe.get("authorization_ref"))!=_text(auth.get("ref")): errors.append("execution_authorization_mismatch")
 fundamental=dna_fundamental.validate_act_chain({"recommendation_ref":_text(rec.get("ref")),"decision_ref":_text(dec.get("ref")),"authorization_ref":_text(auth.get("ref")),"execution_ref":_text(exe.get("ref"))})
 if fundamental.get("status")!=PASS: errors.append("fundamental_chain_"+str(fundamental.get("status",UNDETERMINED)).lower())
 if errors: return {"status":FAIL,"execution_permitted":False,"action":"ABSTAIN","errors":tuple(errors),"fundamental_status":fundamental.get("status")}
 return {"status":PASS,"execution_permitted":False,"action":"CONTINUE_TO_LATER_AUTHORIZED_EXECUTION_REVIEW","errors":(),"fundamental_status":PASS,"note":"P094 validates separation and prerequisites; it does not itself authorize or execute."}
def validate_p094_contract():
 p093=operational_constitutional_invariants.validate_p093_contract(); ok=p093.get("status")==PASS and all(BOUNDARIES.values())
 return {"status":PASS if ok else FAIL,"stages":STAGES,"stage_count":4,"dependencies":EXECUTION_DEPENDENCIES,"p093_valid":p093.get("status")==PASS,"boundaries_valid":all(BOUNDARIES.values()),"runtime_enforcement_proven":False,"execution_authority_proven":False,"real_execution_enabled":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
def p094_manifest():
 return deepcopy({"primitive":PRIMITIVE,"version":VERSION,"schema_version":SCHEMA_VERSION,"scope":SCOPE,"stages":STAGES,"execution_dependencies":EXECUTION_DEPENDENCIES,"transversal_referentials":TRANSVERSAL_REFERENTIALS,"reuse_map":REUSE_MAP,"boundaries":BOUNDARIES,"runtime_enforcement_proven":False,"execution_authority_proven":False,"real_execution_enabled":False,"functional_conclusion_only":True,"phenomenology_undetermined":True})
