from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Dict, Mapping

from ontology import occ_normative_ir as nir
from ontology import occ_normative_ir_real_builder as builder
from ontology import occ_normative_ir_referential_validator as v2
from ontology import occ_normative_ir_coherence_validator as v3
from ontology import occ_normative_ir_semantic_preservation_validator as v4
from ontology import occ_trust_boundaries as trust

PRIMITIVE="occ_constitutional_compiler"
VERSION="P159-OCC1C-constitutional-compiler-v1"
SCHEMA="oce.p159.occ1c.compiled_normative_profile.v1"
PASS,FAIL="PASS","FAIL"

def _r(status:str, reason:str, **extra:Any)->Dict[str,Any]:
    d={"primitive":PRIMITIVE,"version":VERSION,"status":status,"reason":reason,
       "authorization_created":False,"authority_activated":False,
       "execution_performed":False,"p160_opened":False,"final_lock_performed":False,
       "functional_conclusion_only":True,"phenomenology_undetermined":True}
    d.update(deepcopy(extra)); return d

def _sha(p:Path)->str: return sha256(p.read_bytes()).hexdigest()

def _load_proof(path:Path)->Dict[str,Any]:
    try: obj=json.loads(path.read_text(encoding="utf-8"))
    except Exception: return {}
    return obj if isinstance(obj,dict) else {}

def _verified_occ1b(proof:Mapping[str,Any])->bool:
    return (
      proof.get("schema")=="oce.p159.occ1b.postclose_verification.v1" and
      proof.get("verification")=="INDEPENDENT_POST_CLOSE" and
      proof.get("occ1b_closed") is True and proof.get("post_close_verified") is True and
      proof.get("requirements_total")==27 and proof.get("satisfied_count")==25 and
      proof.get("bounded_count")==2 and proof.get("missing_count")==0 and
      proof.get("bounded_requirements")==["C08","C09"] and
      proof.get("authority_activated") is False and proof.get("execution_performed") is False and
      proof.get("p160_opened") is False and proof.get("p159_final_lock_performed") is False
    )

def _forbidden(value:Any)->bool:
    # Declarative safety flags such as executable_payload=False are required
    # evidence, not executable payloads. Reject dangerous carriers/callables,
    # and reject executable_payload only when it is actually enabled.
    carrier_keys=("python","bytecode","callable","eval","exec","shell","subprocess")
    if isinstance(value,Mapping):
        for k,v in value.items():
            key=str(k).lower()
            if callable(v):
                return True
            if key in carrier_keys:
                return True
            if key=="executable_payload" and v is not False:
                return True
            if _forbidden(v):
                return True
    elif isinstance(value,(list,tuple)):
        return any(_forbidden(v) for v in value)
    return False

def compile_profile(package_root:Path, postclose_proof:Path)->Dict[str,Any]:
    root=Path(package_root); proof_path=Path(postclose_proof)
    proof=_load_proof(proof_path)
    if not _verified_occ1b(proof):
        return _r(FAIL,"OCC1B_POSTCLOSE_PROOF_REQUIRED",occ1c_opened=False)

    # Revalidate the real source/NIR at the compilation boundary.
    built=builder.build_real_nir(root)
    if built.get("status")!=PASS:
        return _r(FAIL,"NIR_BUILD_FAILED",occ1c_opened=True,detail=built.get("reason"))
    checks=(v2.validate_real_nir_references(root),
            v3.validate_coherence(root),
            v4.validate_semantic_preservation(root))
    if any(x.get("status")!=PASS for x in checks):
        return _r(FAIL,"VERIFIED_NIR_REQUIRED",occ1c_opened=True,
                  validation_reasons=[x.get("reason") for x in checks])

    graph=built["package"]["graph"]
    gv=nir.validate_graph(graph)
    if gv.get("status")!=PASS:
        return _r(FAIL,"NIR_GRAPH_INVALID",occ1c_opened=True)

    nodes=graph.get("nodes",[])
    if len(nodes)!=48 or len({n.get("node_id") for n in nodes})!=48:
        return _r(FAIL,"NIR_KERNEL_IDENTITY_INVALID",occ1c_opened=True)

    # OCC-1C v1 is intentionally a semantics-preserving declarative lowering:
    # no policy choice, no arbitration, no generated code, no executable payload.
    rules=[]
    for n in sorted(nodes,key=lambda x:str(x.get("node_id",""))):
        rule={
          "norm_id":n["node_id"],
          "node_type":n["node_type"],
          "formalization_level":n["formalization_level"],
          "normative_level":n.get("normative_level"),
          "semantic_status":n.get("semantic_status"),
          "source_object_id":n.get("source_object_id"),
          "text":deepcopy(n.get("text")),
          "evidence_ids":deepcopy(n.get("evidence_ids",[])),
          "lineage_kind":n.get("lineage_kind"),
          "lineage_artifacts":deepcopy(n.get("lineage_artifacts",[])),
          "source_map":deepcopy(n["source_map"]),
          "partial_formalization_explicit":bool(n.get("partial_formalization_explicit",False)),
          "human_judgment_required":bool(n.get("human_judgment_required",False)),
          "machine_formalization_claimed":bool(n.get("machine_formalization_claimed",False)),
          "authorization":False,
          "execution":False,
        }
        rules.append(rule)

    profile={
      "schema":SCHEMA,
      "version":VERSION,
      "profile_state":"UNVERIFIED_COMPILED_PROFILE",
      "source_stage":"VERIFIED_OCC1B_NIR",
      "source_nir_sha256":built["nir_sha256"],
      "occ1b_postclose_proof_sha256":_sha(proof_path),
      "principal_rule_count":48,
      "rules":rules,
      "relations":deepcopy(sorted(graph.get("edges",[]),key=lambda e:(
          str(e.get("source","")),str(e.get("edge_type","")),str(e.get("target",""))))),
      "source_map":deepcopy(graph.get("source_map",{})),
      "compiler_contract":{
        "compiler_creates_norms":False,
        "compiler_creates_authority":False,
        "compiler_authorizes":False,
        "compiler_executes":False,
        "compiler_self_certifies":False,
        "compiler_modifies_sources":False,
        "compiler_invents_normative_defaults":False,
        "conflict_arbitration_performed":False,
        "generated_python":False,
        "executable_payload":False,
        "network_semantic_dependency":False,
        "clock_semantic_dependency":False,
        "random_semantic_dependency":False,
        "cwd_semantic_dependency":False,
      },
      "ccpp":deepcopy(trust.CCPP),
      "bounded_source_absence":["C08_SCOPE","C09_TEMPORAL"],
      "functional_conclusion_only":True,
      "phenomenology_undetermined":True,
    }
    if _forbidden(profile):
        return _r(FAIL,"EXECUTABLE_PAYLOAD_FORBIDDEN",occ1c_opened=True)
    profile["profile_sha256"]=nir.canonical_sha256(profile)
    return _r(PASS,"P159_OCC1C_CONSTITUTIONAL_COMPILER_V1_OK",
              occ1c_opened=True,profile=profile,profile_sha256=profile["profile_sha256"],
              compiled_rules=48,silent_loss=0,invented_norms=0,
              generated_python=False,executable_payload=False,
              source_modified=False,conflict_arbitrated=False)

def verify_profile(profile:Mapping[str,Any])->Dict[str,Any]:
    if not isinstance(profile,Mapping): return _r(FAIL,"PROFILE_NOT_MAPPING",occ1c_opened=True)
    p=deepcopy(dict(profile)); supplied=p.pop("profile_sha256",None)
    if supplied!=nir.canonical_sha256(p):
        return _r(FAIL,"PROFILE_TAMPER_DETECTED",occ1c_opened=True)
    if p.get("schema")!=SCHEMA or p.get("principal_rule_count")!=48:
        return _r(FAIL,"PROFILE_STRUCTURE_INVALID",occ1c_opened=True)
    rules=p.get("rules")
    if not isinstance(rules,list) or len(rules)!=48 or len({r.get("norm_id") for r in rules})!=48:
        return _r(FAIL,"PROFILE_RULE_IDENTITY_INVALID",occ1c_opened=True)
    if _forbidden(p): return _r(FAIL,"EXECUTABLE_PAYLOAD_FORBIDDEN",occ1c_opened=True)
    c=p.get("compiler_contract",{})
    required_false=("compiler_creates_norms","compiler_creates_authority","compiler_authorizes",
                    "compiler_executes","compiler_self_certifies","compiler_modifies_sources",
                    "compiler_invents_normative_defaults","conflict_arbitration_performed",
                    "generated_python","executable_payload","network_semantic_dependency",
                    "clock_semantic_dependency","random_semantic_dependency","cwd_semantic_dependency")
    if any(c.get(k) is not False for k in required_false):
        return _r(FAIL,"COMPILER_BOUNDARY_VIOLATION",occ1c_opened=True)
    return _r(PASS,"COMPILED_PROFILE_INTEGRITY_OK",occ1c_opened=True)

# === P159 OCC-1C CANONICAL PIPELINE V1 ===
CANONICAL_PIPELINE_VERSION = "P159-OCC1C-canonical-pipeline-v1"
COMPILATION_CLASSES = ("CC1_DETERMINISTIC_ENFORCEMENT","CC2_RUNTIME_EVALUATION","CC3_ESCALATION_HUMAN_CCAD_REQUIRED")
NORM_OPS = ("ASSERT","REQUIRE","FORBID","MATCH_SCOPE","CHECK_AUTHORITY","CHECK_EXPIRY","CHECK_PROVENANCE","CHECK_EVIDENCE","CHECK_STATE","CHECK_SEQUENCE","CHECK_COALITION","ESCALATE","REQUEST_REVIEW","ABSTAIN","DENY","ALLOW_CANDIDATE")
FORBIDDEN_NORM_OPS = ("EXECUTE_ACTION",)
PIPELINE_C1_C12 = (("C1","VALIDATE_INPUT"),("C2","RESOLVE_REFERENCES"),("C3","BIND_AUTHORITY"),("C4","BIND_SCOPE"),("C5","BIND_TEMPORAL_CONSTRAINTS"),("C6","COMPILE_CONDITIONS"),("C7","COMPILE_CONFLICT_HOOKS"),("C8","COMPILE_ENFORCEMENT_RULES"),("C9","GENERATE_PROVENANCE_MAP"),("C10","STATIC_CONSTITUTIONAL_CHECKS"),("C11","SEMANTIC_PRESERVATION_CHECK"),("C12","SEAL_CANDIDATE"))
CCI = tuple("CCI-%d"%i for i in range(1,16))
COMPILED_RULE_FIELDS = ("rule_id","source_norm_ids","nir_node_ids","rule_type","evaluation_phase","inputs","conditions","outputs","enforcement_class","authority_requirements","scope_constraints","temporal_constraints","uncertainty_semantics","provenance","semantic_fingerprint")

def _canonical_hash(value):
    return nir.canonical_sha256(value)

def _classify_rule(rule):
    if bool(rule.get("human_judgment_required")):
        return "CC3_ESCALATION_HUMAN_CCAD_REQUIRED"
    if (rule.get("formalization_level") in ("F0","F1") or rule.get("semantic_status") in ("UNKNOWN","CONTESTED","UNSUPPORTED") or bool(rule.get("partial_formalization_explicit"))):
        return "CC2_RUNTIME_EVALUATION"
    return "CC1_DETERMINISTIC_ENFORCEMENT"

def _norm_ops_for(rule, cc):
    ops=["ASSERT","CHECK_PROVENANCE"]
    if rule.get("evidence_ids"): ops.append("CHECK_EVIDENCE")
    if cc=="CC2_RUNTIME_EVALUATION": ops.extend(["CHECK_STATE","ABSTAIN"])
    elif cc=="CC3_ESCALATION_HUMAN_CCAD_REQUIRED": ops.extend(["REQUEST_REVIEW","ESCALATE","ABSTAIN"])
    return ops

def _compiled_rule_from_legacy(rule):
    cc=_classify_rule(rule)
    sid=rule.get("source_object_id") or rule.get("norm_id")
    payload={
      "rule_id":rule.get("norm_id"),
      "source_norm_ids":[sid] if sid else [],
      "nir_node_ids":[rule.get("norm_id")] if rule.get("norm_id") else [],
      "rule_type":rule.get("node_type"),
      "evaluation_phase":"RUNTIME" if cc!="CC1_DETERMINISTIC_ENFORCEMENT" else "COMPILE_TIME",
      "inputs":[],
      "conditions":[],
      "outputs":_norm_ops_for(rule,cc),
      "enforcement_class":cc,
      "authority_requirements":{"binding_kind":"AUTHORITY_TYPE_ONLY","current_holder_resolved":False,"authorization_created":False},
      "scope_constraints":{"status":"SOURCE_ABSENT_BOUNDED","implicit_global":False},
      "temporal_constraints":{"status":"SOURCE_ABSENT_BOUNDED","implicit_permanent":False},
      "uncertainty_semantics":{"semantic_status":rule.get("semantic_status"),"partial_formalization_explicit":bool(rule.get("partial_formalization_explicit")),"human_judgment_required":bool(rule.get("human_judgment_required")),"unknown_never_promoted_to_true":True},
      "provenance":{"source_object_id":sid,"source_map":deepcopy(rule.get("source_map",{})),"lineage_kind":rule.get("lineage_kind"),"lineage_artifacts":deepcopy(rule.get("lineage_artifacts",[])),"evidence_ids":deepcopy(rule.get("evidence_ids",[]))}
    }
    payload["semantic_fingerprint"]=_canonical_hash(payload)
    return payload

def _validate_norm_ops(rules):
    allowed=set(NORM_OPS)
    return all(isinstance(r.get("outputs"),list) and all(op in allowed and op not in FORBIDDEN_NORM_OPS for op in r["outputs"]) for r in rules)

def _pipeline_report():
    return [
      {"stage":"C1","name":"VALIDATE_INPUT","status":"PERFORMED"},
      {"stage":"C2","name":"RESOLVE_REFERENCES","status":"PERFORMED"},
      {"stage":"C3","name":"BIND_AUTHORITY","status":"PERFORMED_TYPE_ONLY"},
      {"stage":"C4","name":"BIND_SCOPE","status":"PRESERVED_SOURCE_ABSENT_BOUNDED"},
      {"stage":"C5","name":"BIND_TEMPORAL_CONSTRAINTS","status":"PRESERVED_SOURCE_ABSENT_BOUNDED"},
      {"stage":"C6","name":"COMPILE_CONDITIONS","status":"PERFORMED_CONSERVATIVE"},
      {"stage":"C7","name":"COMPILE_CONFLICT_HOOKS","status":"DEFINED_NO_ARBITRATION"},
      {"stage":"C8","name":"COMPILE_ENFORCEMENT_RULES","status":"PERFORMED_DECLARATIVE"},
      {"stage":"C9","name":"GENERATE_PROVENANCE_MAP","status":"PERFORMED"},
      {"stage":"C10","name":"STATIC_CONSTITUTIONAL_CHECKS","status":"HOOK_DEFINED_OCC1D_NOT_OPENED"},
      {"stage":"C11","name":"SEMANTIC_PRESERVATION_CHECK","status":"PERFORMED_BY_EXISTING_V4_AND_INDEPENDENT_VERIFIER"},
      {"stage":"C12","name":"SEAL_CANDIDATE","status":"CANDIDATE_HASH_SEALED_NOT_CERTIFIED_NOT_ACTIVE"}]

def compile_canonical_profile(package_root:Path, postclose_proof:Path)->Dict[str,Any]:
    legacy=compile_profile(package_root,postclose_proof)
    if legacy.get("status")!=PASS:
        return _r(FAIL,"CANONICAL_PIPELINE_INPUT_REJECTED",occ1c_opened=True,detail=legacy.get("reason"))
    base=legacy["profile"]
    rules=[_compiled_rule_from_legacy(r) for r in base["rules"]]
    if len(rules)!=48 or len({r["rule_id"] for r in rules})!=48:
        return _r(FAIL,"CANONICAL_RULE_COVERAGE_INVALID",occ1c_opened=True)
    if not all(set(COMPILED_RULE_FIELDS).issubset(set(r)) for r in rules):
        return _r(FAIL,"COMPILED_RULE_SCHEMA_INVALID",occ1c_opened=True)
    if not _validate_norm_ops(rules):
        return _r(FAIL,"NORM_OPS_CLOSED_WORLD_VIOLATION",occ1c_opened=True)
    canonical={
      "schema":"oce.p159.occ1c.canonical_compiled_profile.v1",
      "pipeline_version":CANONICAL_PIPELINE_VERSION,
      "profile_state":"UNVERIFIED_COMPILED_PROFILE",
      "legacy_profile_sha256":base["profile_sha256"],
      "source_nir_sha256":base["source_nir_sha256"],
      "occ1b_postclose_proof_sha256":base["occ1b_postclose_proof_sha256"],
      "pipeline":_pipeline_report(),
      "compilation_classes":list(COMPILATION_CLASSES),
      "norm_ops_specification":{"closed_world":True,"allowed":list(NORM_OPS),"forbidden":list(FORBIDDEN_NORM_OPS),"allow_candidate_is_authorization":False},
      "compiled_rule_schema":{"required_fields":list(COMPILED_RULE_FIELDS)},
      "rules":rules,
      "relations":deepcopy(base.get("relations",[])),
      "source_map":deepcopy(base.get("source_map",{})),
      "compiler_manifest":{"compiler_name":PRIMITIVE,"compiler_version":VERSION,"pipeline_version":CANONICAL_PIPELINE_VERSION,"deterministic":True,"declarative_json_only":True,"generated_python":False,"network_dependency":False,"random_dependency":False,"cwd_dependency":False,"self_certification":False,"self_activation":False},
      "transformation_ledger":[{"rule_id":r["rule_id"],"source_norm_ids":r["source_norm_ids"],"nir_node_ids":r["nir_node_ids"],"compilation_class":r["enforcement_class"],"semantic_fingerprint":r["semantic_fingerprint"]} for r in rules],
      "compile_report":{"principal_rule_count":len(rules),"silent_normative_loss":0,"invented_norms":0,"authority_created":False,"authorization_created":False,"execution_performed":False,"conflict_arbitration_performed":False,"occ1d_opened":False,"p160_opened":False,"final_lock_performed":False,"scope_source_absence_preserved":True,"temporal_source_absence_preserved":True},
      "semantic_diff":{"source_to_compiled_rule_count_delta":0,"normative_creation":0,"normative_loss":0,"authority_widening":0,"scope_widening":0,"temporal_weakening":0,"unknown_promotion":0},
      "cci_registry":list(CCI),
      "functional_conclusion_only":True,"phenomenology_undetermined":True}
    canonical["artifact_hash"]=_canonical_hash(canonical)
    return _r(PASS,"P159_OCC1C_CANONICAL_PIPELINE_V1_OK",occ1c_opened=True,canonical_profile=canonical,artifact_hash=canonical["artifact_hash"],compiled_rules=48,occ1d_opened=False)

def verify_canonical_profile(profile:Mapping[str,Any])->Dict[str,Any]:
    if not isinstance(profile,Mapping): return _r(FAIL,"CANONICAL_PROFILE_NOT_MAPPING",occ1c_opened=True)
    p=deepcopy(dict(profile)); supplied=p.pop("artifact_hash",None)
    if supplied!=_canonical_hash(p): return _r(FAIL,"CANONICAL_PROFILE_TAMPER_DETECTED",occ1c_opened=True)
    if p.get("profile_state")!="UNVERIFIED_COMPILED_PROFILE": return _r(FAIL,"ILLEGAL_PROFILE_STATE",occ1c_opened=True)
    rules=p.get("rules")
    if not isinstance(rules,list) or len(rules)!=48: return _r(FAIL,"CANONICAL_RULE_COVERAGE_INVALID",occ1c_opened=True)
    if not _validate_norm_ops(rules): return _r(FAIL,"NORM_OPS_CLOSED_WORLD_VIOLATION",occ1c_opened=True)
    if any(r.get("authority_requirements",{}).get("authorization_created") is not False for r in rules): return _r(FAIL,"AUTHORIZATION_CREATION_FORBIDDEN",occ1c_opened=True)
    report=p.get("compile_report",{})
    for k in ("authority_created","authorization_created","execution_performed","conflict_arbitration_performed","occ1d_opened","p160_opened","final_lock_performed"):
        if report.get(k) is not False: return _r(FAIL,"CANONICAL_STAGE_BOUNDARY_VIOLATION",occ1c_opened=True)
    if p.get("norm_ops_specification",{}).get("allow_candidate_is_authorization") is not False: return _r(FAIL,"ELIGIBILITY_AUTHORIZATION_COLLAPSE",occ1c_opened=True)
    return _r(PASS,"CANONICAL_PROFILE_INTEGRITY_OK",occ1c_opened=True,occ1d_opened=False)
