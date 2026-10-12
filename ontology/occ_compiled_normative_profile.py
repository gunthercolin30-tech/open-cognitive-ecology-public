from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping
PRIMITIVE="occ_compiled_normative_profile"
VERSION="P159-OCC1E-CNP-v1"
SCHEMA="oce.p159.occ1e.compiled_normative_profile.v1"
LIFECYCLE=("DRAFT","COMPILED","VERIFIED","SEALED","CERTIFIED","ACTIVE","SUPERSEDED","REVOKED","NON_ACTIVATABLE")
RULE_RESULTS=("CONSTRAINT_SATISFIED","CONSTRAINT_VIOLATED","UNRESOLVED","NOT_APPLICABLE","ALLOW_CANDIDATE")
CONSUMERS=("NormResolver","CCAD","AuthorizationEngine","CapabilityGate","RecoveryEngine","AssuranceEngine")
def canonical_sha256(v): return sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def file_sha256(p): return sha256(Path(p).read_bytes()).hexdigest()
def _result(status,reason,**kw):
 d={"status":status,"reason":reason,"primitive":PRIMITIVE,"authorization_created":False,"authority_activated":False,"execution_performed":False,"p160_opened":False,"p159_final_lock":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}; d.update(kw); return d
def _rule(r):
 rid=str(r.get("rule_id") or r.get("norm_id") or "")
 if not rid: raise ValueError("RULE_ID_REQUIRED")
 sids=deepcopy(r.get("source_norm_ids") or ([r.get("source_object_id") or r.get("norm_id")] if (r.get("source_object_id") or r.get("norm_id")) else []))
 nids=deepcopy(r.get("nir_node_ids") or ([r.get("norm_id")] if r.get("norm_id") else []))
 prov=deepcopy(r.get("provenance") or {"source_object_id":r.get("source_object_id"),"source_map":r.get("source_map",{}),"lineage_kind":r.get("lineage_kind"),"lineage_artifacts":r.get("lineage_artifacts",[]),"evidence_ids":r.get("evidence_ids",[])})
 out={"rule_id":rid,"source_norm_ids":sids,"nir_node_ids":nids,"evaluation_phase":r.get("evaluation_phase","RUNTIME"),"inputs":deepcopy(r.get("inputs",[])),"conditions":deepcopy(r.get("conditions",[])),"normative_effect":{"source_semantics_preserved":True,"result_domain":list(RULE_RESULTS),"allow_candidate_is_authorization":False,"authorization_created":False,"execution_performed":False},"enforcement_class":r.get("enforcement_class","UNRESOLVED"),"authority_requirements":deepcopy(r.get("authority_requirements",{"binding_kind":"AUTHORITY_TYPE_ONLY","current_holder_resolved":False,"authorization_created":False})),"scope_constraints":deepcopy(r.get("scope_constraints",{"status":"SOURCE_ABSENT_BOUNDED","implicit_global":False})),"temporal_constraints":deepcopy(r.get("temporal_constraints",{"status":"SOURCE_ABSENT_BOUNDED","implicit_permanent":False})),"uncertainty_semantics":deepcopy(r.get("uncertainty_semantics",{"semantic_status":r.get("semantic_status"),"unknown_never_promoted_to_true":True})),"provenance":prov}
 out["authority_requirements"]["authorization_created"]=False; out["uncertainty_semantics"]["unknown_never_promoted_to_true"]=True; out["semantic_fingerprint"]=canonical_sha256(out); return out
def build_profile(base,source_package_hash,compiler_hash,schema_hash,static_validation_report_hash):
 if not isinstance(base,Mapping) or not isinstance(base.get("rules"),list) or not base["rules"]: raise ValueError("OCC1C_PROFILE_REQUIRED")
 rules=[_rule(r) for r in base["rules"]]
 if len({r["rule_id"] for r in rules})!=len(rules): raise ValueError("RULE_IDENTITY_NOT_UNIQUE")
 snap={"source_package_hash":source_package_hash,"nir_package_hash":str(base.get("source_nir_sha256","")),"occ1c_profile_hash":canonical_sha256(base),"compiler_hash":compiler_hash,"schema_hash":schema_hash,"static_validation_report_hash":static_validation_report_hash}; snap["snapshot_hash"]=canonical_sha256(snap)
 p={"schema":SCHEMA,"profile_id":"P159-OCC1E-CNP","profile_version":VERSION,"profile_state":"COMPILED","lifecycle_model":{"states":list(LIFECYCLE),"self_activation":False,"ordinary_activation_from_non_activatable":False,"sealed_mutation_allowed":False,"status_changes_require_governed_transition":True},"source_package_hash":source_package_hash,"nir_package_hash":str(base.get("source_nir_sha256","")),"compiler_version":str(base.get("version") or base.get("pipeline_version") or "OCC1C"),"compiler_hash":compiler_hash,"schema_version":"v1","schema_hash":schema_hash,"rules":rules,"authority_model":{"resolution_phase":"RUNTIME","current_holder_resolved_at_compile_time":False,"compiler_creates_authority":False,"compiler_authorizes":False},"scope_model":{"bounded_source_absence":deepcopy(base.get("bounded_source_absence",[])),"implicit_global_scope":False},"temporal_model":{"bounded_source_absence":deepcopy(base.get("bounded_source_absence",[])),"implicit_permanence":False},"uncertainty_model":{"unknown_never_promoted_to_true":True,"unresolved_is_authorization":False},"conflict_hooks":{"arbitration_performed_by_cnp":False,"ccad_may_be_required":True,"predetermined_resolution":False},"enforcement_map":{"status":"UNRESOLVED","required_consumer_types":list(CONSUMERS),"rule_bindings":{r["rule_id"]:{"consumer_status":"UNRESOLVED","consumers":[],"runtime_reachability_proven":False} for r in rules},"runtime_consumer_graph_proven":False},"runtime_interfaces":{"contract_only":True,"execution_capability":False,"authorization_capability":False,"consumers":list(CONSUMERS),"allow_candidate_is_permission_to_execute":False},"source_map":deepcopy(base.get("source_map",{})),"validation_report_hash":static_validation_report_hash,"constitutional_snapshot":snap,"compiler_contract":{"source_is_compiler":False,"compiler_is_verifier":False,"compiler_is_authority":False,"compiler_is_execution":False,"compilation_manufactures_legitimacy":False,"authorization_created":False,"execution_performed":False,"self_activation":False,"executable_payload":False},"explainability_contract":{"source_and_effect_per_rule_required":True,"opaque_bytecode_as_sole_authority_representation":False},"portability_contract":{"content_addressed":True,"reconstructible_from_declared_inputs":True},"functional_conclusion_only":True,"phenomenology_undetermined":True}
 p["artifact_hash"]=canonical_sha256(p); return p
def verify_profile(profile):
 if not isinstance(profile,Mapping): return _result("FAIL","PROFILE_NOT_MAPPING")
 p=deepcopy(dict(profile)); supplied=p.pop("artifact_hash",None)
 if not supplied or supplied!=canonical_sha256(p): return _result("FAIL","ARTIFACT_HASH_MISMATCH")
 if p.get("schema")!=SCHEMA or p.get("profile_state") not in LIFECYCLE: return _result("FAIL","PROFILE_STRUCTURE_INVALID")
 if p.get("profile_state")=="ACTIVE": return _result("FAIL","OCC1E_MUST_NOT_SELF_ACTIVATE")
 lc=p.get("lifecycle_model",{}); cc=p.get("compiler_contract",{}); ri=p.get("runtime_interfaces",{})
 if lc.get("self_activation") is not False or lc.get("sealed_mutation_allowed") is not False or lc.get("ordinary_activation_from_non_activatable") is not False: return _result("FAIL","LIFECYCLE_BOUNDARY_VIOLATION")
 if any(cc.get(k) is not False for k in ("source_is_compiler","compiler_is_verifier","compiler_is_authority","compiler_is_execution","compilation_manufactures_legitimacy","authorization_created","execution_performed","self_activation","executable_payload")): return _result("FAIL","TRUST_BOUNDARY_VIOLATION")
 if ri.get("execution_capability") is not False or ri.get("authorization_capability") is not False or ri.get("allow_candidate_is_permission_to_execute") is not False: return _result("FAIL","RUNTIME_INTERFACE_CAPABILITY_VIOLATION")
 snap=p.get("constitutional_snapshot");
 if not isinstance(snap,Mapping): return _result("FAIL","CONSTITUTIONAL_SNAPSHOT_REQUIRED")
 s=deepcopy(dict(snap)); sh=s.pop("snapshot_hash",None)
 if not sh or sh!=canonical_sha256(s): return _result("FAIL","SNAPSHOT_HASH_MISMATCH")
 rules=p.get("rules"); bindings=p.get("enforcement_map",{}).get("rule_bindings",{})
 if not isinstance(rules,list) or not rules or len({r.get("rule_id") for r in rules})!=len(rules): return _result("FAIL","RULE_IDENTITY_INVALID")
 for r in rules:
  rid=r.get("rule_id"); eff=r.get("normative_effect",{}); prov=r.get("provenance")
  if not r.get("source_norm_ids") or not r.get("nir_node_ids"): return _result("FAIL","RULE_SOURCE_MAPPING_REQUIRED",rule_id=rid)
  if not isinstance(prov,Mapping) or "source_map" not in prov: return _result("FAIL","RULE_PROVENANCE_REQUIRED",rule_id=rid)
  if eff.get("allow_candidate_is_authorization") is not False or eff.get("authorization_created") is not False or eff.get("execution_performed") is not False: return _result("FAIL","RULE_CAPABILITY_VIOLATION",rule_id=rid)
  if rid not in bindings: return _result("FAIL","ENFORCEMENT_BINDING_REQUIRED",rule_id=rid)
 return _result("PASS","P159_OCC1E_CNP_CONTRACT_OK",rule_count=len(rules),lifecycle_state=p.get("profile_state"),enforcement_status=p.get("enforcement_map",{}).get("status"),runtime_consumer_graph_proven=p.get("enforcement_map",{}).get("runtime_consumer_graph_proven") is True)
def transition(profile,target,governed=False):
 current=str(profile.get("profile_state",""))
 if target not in LIFECYCLE: return _result("FAIL","UNKNOWN_TARGET_STATE")
 if not governed: return _result("FAIL","GOVERNED_TRANSITION_REQUIRED",current=current,target=target)
 if target=="ACTIVE": return _result("FAIL","ACTIVATION_OUTSIDE_OCC1E_SCOPE",current=current,target=target)
 allowed={"DRAFT":{"COMPILED","NON_ACTIVATABLE"},"COMPILED":{"VERIFIED","NON_ACTIVATABLE"},"VERIFIED":{"SEALED","NON_ACTIVATABLE"},"SEALED":{"CERTIFIED","SUPERSEDED","REVOKED"},"CERTIFIED":{"SUPERSEDED","REVOKED"},"SUPERSEDED":set(),"REVOKED":set(),"NON_ACTIVATABLE":set()}
 if target not in allowed.get(current,set()): return _result("FAIL","ILLEGAL_LIFECYCLE_TRANSITION",current=current,target=target)
 out=deepcopy(dict(profile)); out["profile_state"]=target; out.pop("artifact_hash",None); out["artifact_hash"]=canonical_sha256(out); return _result("PASS","GOVERNED_NON_ACTIVE_TRANSITION_OK",profile=out,current=current,target=target)
def manifest(profile):
 v=verify_profile(profile)
 if v["status"]!="PASS": raise ValueError(v["reason"])
 return {"schema":"oce.p159.occ1e.cnp_manifest.v1","profile_id":profile["profile_id"],"profile_version":profile["profile_version"],"profile_state":profile["profile_state"],"artifact_hash":profile["artifact_hash"],"constitutional_snapshot_hash":profile["constitutional_snapshot"]["snapshot_hash"],"rule_count":len(profile["rules"]),"authorization_created":False,"execution_performed":False,"self_activation":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
def human_explanation(profile):
 v=verify_profile(profile)
 if v["status"]!="PASS": raise ValueError(v["reason"])
 lines=["P159 OCC-1E CompiledNormativeProfile","State: "+profile["profile_state"],"Artifact hash: "+profile["artifact_hash"],"This artifact is derivative and non-executing.","It creates neither authority nor authorization and cannot self-activate.","ALLOW_CANDIDATE is not permission to execute.","Runtime enforcement bindings remain explicit and may remain UNRESOLVED until proven.","","Rules:"]
 for r in profile["rules"]: lines.append("- %s | sources=%s | effect=constraint-only; no authorization/execution"%(r["rule_id"],",".join(map(str,r["source_norm_ids"]))))
 return "\n".join(lines)+"\n"
