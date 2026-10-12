from __future__ import annotations
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping

PRIMITIVE="constitutional_decision_ledger"
VERSION="1.0.0-p104"
SCHEMA_VERSION="oce.p104.constitutional_decision_ledger.v1"
PASS,FAIL,CONFLICT,UNDETERMINED="PASS","FAIL","CONFLICT","UNDETERMINED"
REQUIRED_FIELDS=("decision_id","problem_id","decision_type","recommendations_considered","decision_authority","authorization","applicable_DNA","applicable_constitution","applicable_governance","evidence","uncertainty","affected_entities","result","challenge_status","appeal_status")
EXECUTION_DEPENDENCIES=("P103","W1/G1_REUSE","G2_DNA_FUNDAMENTAL")
REUSE_MAP={"stage_separation":"action_status_separation","human_authority":"human_reserved_authority_registry","normative_conflicts":"normative_conflict_resolution","non_circumvention":"constitutional_non_circumvention","recourse_recovery":"constitutional_recourse_recovery","persistence_pattern":"canonical_external_influence_ledger","decision_record_pattern":"external_decision_record_extension"}
BOUNDARIES={"recommendation_decision_authorization_execution_distinct":True,"references_prediction_action_outcome_ledgers_without_required_duplication":True,"lower_norm_cannot_contradict_higher_norm":True,"unresolved_conflict_requires_abstention_or_escalation":True,"intelligence_performance_wealth_reputation_majority_do_not_create_authority":True,"cost_or_performance_cannot_bypass_higher_constraints":True,"does_not_implement_p105_human_interface":True,"does_not_claim_p155_p166_runtime_enforcement":True,"does_not_enable_real_execution":True,"functional_conclusion_only":True,"phenomenology_undetermined":True}

def _present(v:Any)->bool:
 if v is None:return False
 if isinstance(v,str):return bool(v.strip())
 if isinstance(v,(list,tuple,set,dict)):return bool(v)
 return True
def _canonical(v:Any)->str:return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def _hash_payload(v:Mapping[str,Any])->str:return sha256(_canonical(v).encode("utf-8")).hexdigest()

def validate_record(record:Mapping[str,Any])->dict[str,Any]:
 if not isinstance(record,Mapping):return {"status":UNDETERMINED,"valid":False,"action":"ABSTAIN","reason":"record_not_mapping"}
 missing=[k for k in REQUIRED_FIELDS if not _present(record.get(k))]
 if missing:return {"status":UNDETERMINED,"valid":False,"action":"ABSTAIN","reason":"required_fields_missing","missing_fields":missing}
 ns=str(record.get("normative_status",PASS)).upper()
 if ns==CONFLICT:return {"status":CONFLICT,"valid":False,"action":"ABSTAIN_AND_ESCALATE","reason":"unresolved_normative_conflict"}
 if ns!=PASS:return {"status":UNDETERMINED,"valid":False,"action":"ABSTAIN","reason":"normative_status_not_proven"}
 if bool(record.get("authority_expanded",False)):return {"status":FAIL,"valid":False,"action":"REJECT","reason":"authority_expansion_forbidden"}
 if bool(record.get("stage_conflation",False)):return {"status":FAIL,"valid":False,"action":"REJECT","reason":"act_stage_conflation_forbidden"}
 return {"status":PASS,"valid":True,"action":"LEDGER_ELIGIBLE","reason":"p104_contract_satisfied"}

def build_record(payload:Mapping[str,Any])->dict[str,Any]:
 p=deepcopy(dict(payload));check=validate_record(p)
 if check["status"]!=PASS:return {"primitive":PRIMITIVE,"schema_version":SCHEMA_VERSION,**check,"persisted":False,"runtime_enforcement_proven":False,"real_execution_enabled":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
 if not _present(p.get("decision_time")):return {"primitive":PRIMITIVE,"schema_version":SCHEMA_VERSION,"status":UNDETERMINED,"valid":False,"action":"ABSTAIN","reason":"decision_time_missing","persisted":False,"runtime_enforcement_proven":False,"real_execution_enabled":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
 record={k:deepcopy(p[k]) for k in REQUIRED_FIELDS}
 record.update({"decision_time":p["decision_time"],"prediction_ledger_refs":deepcopy(p.get("prediction_ledger_refs",[])),"action_ledger_refs":deepcopy(p.get("action_ledger_refs",[])),"outcome_ledger_refs":deepcopy(p.get("outcome_ledger_refs",[])),"recourse_refs":deepcopy(p.get("recourse_refs",[])),"rollback_refs":deepcopy(p.get("rollback_refs",[])),"provenance":deepcopy(p.get("provenance",{})),"configuration_ref":p.get("configuration_ref"),"dependency_refs":deepcopy(p.get("dependency_refs",[])),"metrics":deepcopy(p.get("metrics",{})),"normative_status":PASS})
 record["record_hash"]=_hash_payload(record)
 return {"primitive":PRIMITIVE,"schema_version":SCHEMA_VERSION,"status":PASS,"valid":True,"action":"LEDGER_RECORD_BUILT","record":record,"persisted":False,"runtime_enforcement_proven":False,"real_execution_enabled":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}

def persist_record(payload:Mapping[str,Any],root:Path|None=None,filesystem_effect_context=None)->dict[str,Any]:
 built=build_record(payload)
 if built.get("status")!=PASS:return built
 root=Path(root) if root is not None else Path.home()/"open-cognitive-ecology"
 path=root/"constitutional_decision_ledger"/"constitutional_decision_ledger.jsonl"
 if not path.parent.exists():
  if filesystem_effect_context is None:raise RuntimeError("governed_filesystem_effect_context_required")
  filesystem_effect_context.begin()
  filesystem_effect_context.execute_path("constitutional_decision_ledger_create_dirs","FS_CREATE_DIRS",path.parent)
 envelope={"record":built["record"],"persisted_at":datetime.now(timezone.utc).isoformat()}
 with path.open("a",encoding="utf-8") as fh:fh.write(_canonical(envelope)+"\n")
 out=deepcopy(built);out["persisted"]=True;out["ledger_path"]=str(path);return out

def manifest()->dict[str,Any]:
 return deepcopy({"primitive":PRIMITIVE,"version":VERSION,"schema_version":SCHEMA_VERSION,"required_fields":REQUIRED_FIELDS,"execution_dependencies":EXECUTION_DEPENDENCIES,"reuse_map":REUSE_MAP,"boundaries":BOUNDARIES,"p105_implemented":False,"runtime_enforcement_proven":False,"real_execution_enabled":False,"functional_conclusion_only":True,"phenomenology_undetermined":True})
