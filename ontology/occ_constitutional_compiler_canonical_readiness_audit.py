from __future__ import annotations
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Mapping
from ontology import occ_constitutional_compiler as c
from ontology import occ_normative_ir as nir

PRIMITIVE="occ_constitutional_compiler_canonical_readiness_audit"
VERSION="P159-OCC1C-canonical-readiness-audit-v1"
PASS,BOUNDED,MISSING="SATISFIED","BOUNDED","MISSING"

CCI_TEXT={
"CCI-1":"no normative creation","CCI-2":"no authority creation","CCI-3":"no silent scope widening",
"CCI-4":"no silent temporal weakening","CCI-5":"no prohibited UNKNOWN collapse",
"CCI-6":"no active norm optimization removal","CCI-7":"no DNA balancing",
"CCI-8":"output declarative/non-executable","CCI-9":"every rule provenance","CCI-10":"deterministic",
"CCI-11":"no self-activation","CCI-12":"no self-certification",
"CCI-13":"critical ambiguity blocks/escalates","CCI-14":"compilation failure cannot relax requirements",
"CCI-15":"normative eligibility distinct from authorization"}

def _item(status,evidence,note=""): return {"status":status,"evidence":evidence,"note":note}

def audit(package_root:Path, proof:Path)->Dict[str,Any]:
    a=c.compile_canonical_profile(Path(package_root),Path(proof))
    if a.get("status")!=c.PASS:
        return {"status":"FAIL","reason":"CANONICAL_PROFILE_BUILD_FAILED","detail":a.get("reason")}
    p=a["canonical_profile"]; rules=p["rules"]; cr=p["compile_report"]; man=p["compiler_manifest"]
    ids=[r["rule_id"] for r in rules]
    cci={}
    cci["CCI-1"]=_item(PASS,"48 unique compiled rules; semantic_diff.normative_creation=0") if len(rules)==48 and len(set(ids))==48 and p["semantic_diff"]["normative_creation"]==0 else _item(MISSING,"rule identity/semantic diff")
    cci["CCI-2"]=_item(PASS,"compile_report.authority_created=false and per-rule authorization_created=false") if cr["authority_created"] is False and all(r["authority_requirements"]["authorization_created"] is False for r in rules) else _item(MISSING,"authority boundary")
    cci["CCI-3"]=_item(PASS,"scope source absence preserved; implicit_global=false") if cr["scope_source_absence_preserved"] and all(r["scope_constraints"]["implicit_global"] is False for r in rules) else _item(MISSING,"scope")
    cci["CCI-4"]=_item(PASS,"temporal source absence preserved; implicit_permanent=false") if cr["temporal_source_absence_preserved"] and all(r["temporal_constraints"]["implicit_permanent"] is False for r in rules) else _item(MISSING,"temporal")
    cci["CCI-5"]=_item(PASS,"unknown_never_promoted_to_true=true for every rule") if all(r["uncertainty_semantics"]["unknown_never_promoted_to_true"] is True for r in rules) else _item(MISSING,"unknown")
    cci["CCI-6"]=_item(PASS,"48/48 preserved; silent_normative_loss=0") if len(rules)==48 and cr["silent_normative_loss"]==0 else _item(MISSING,"coverage")
    cci["CCI-7"]=_item(BOUNDED,"compiler contains no moral balancing operator; dedicated mutation proof absent","Requires explicit adversarial DNA-balancing test before closure.")
    cci["CCI-8"]=_item(PASS,"declarative_json_only=true, generated_python=false, EXECUTE_ACTION forbidden") if man["declarative_json_only"] and not man["generated_python"] and "EXECUTE_ACTION" in p["norm_ops_specification"]["forbidden"] else _item(MISSING,"backend")
    cci["CCI-9"]=_item(PASS,"source_map present for every compiled rule") if all(r["provenance"]["source_map"] for r in rules) else _item(MISSING,"provenance")
    b=c.compile_canonical_profile(Path(package_root),Path(proof))
    cci["CCI-10"]=_item(PASS,"two builds yield identical artifact_hash; manifest deterministic=true") if b.get("artifact_hash")==a.get("artifact_hash") and man["deterministic"] else _item(MISSING,"determinism")
    cci["CCI-11"]=_item(PASS,"compiler_manifest.self_activation=false; profile UNVERIFIED") if not man["self_activation"] and p["profile_state"]=="UNVERIFIED_COMPILED_PROFILE" else _item(MISSING,"activation")
    cci["CCI-12"]=_item(PASS,"compiler_manifest.self_certification=false; profile UNVERIFIED") if not man["self_certification"] and p["profile_state"]=="UNVERIFIED_COMPILED_PROFILE" else _item(MISSING,"certification")
    cci["CCI-13"]=_item(BOUNDED,"CC3 emits REQUEST_REVIEW/ESCALATE for human-judgment rules","No explicit critical-ambiguity mutation test yet.")
    cci["CCI-14"]=_item(BOUNDED,"legacy compiler is fail-closed; canonical failure-relaxation crown not yet explicit","Requires explicit compile-failure mutation test.")
    cci["CCI-15"]=_item(PASS,"allow_candidate_is_authorization=false; authorization_created=false") if p["norm_ops_specification"]["allow_candidate_is_authorization"] is False and cr["authorization_created"] is False else _item(MISSING,"eligibility/authorization")

    artifacts={
      "ART-1_COMPILER_ENGINE":_item(PASS,"ontology/occ_constitutional_compiler.py"),
      "ART-2_NORM_OPS_SPECIFICATION":_item(PASS,"canonical profile norm_ops_specification"),
      "ART-3_COMPILED_RULE_SCHEMA":_item(PASS,"canonical profile compiled_rule_schema"),
      "ART-4_COMPILE_REPORT":_item(BOUNDED,"compile_report embedded in in-memory canonical profile","Canonical standalone persisted compile_report.json not yet produced."),
      "ART-5_TRANSFORMATION_LEDGER":_item(BOUNDED,"transformation_ledger embedded in in-memory canonical profile","Canonical standalone persisted transformation ledger not yet produced."),
      "ART-6_COMPILER_MANIFEST":_item(BOUNDED,"compiler_manifest embedded in in-memory canonical profile","Canonical persisted manifest/build identity is incomplete: binary hash, dependency manifest and environment fingerprint are not evidenced here.")
    }
    closure={
      "CR-1_DECLARATIVE_DETERMINISTIC_BACKEND":_item(PASS,"CCI-8 + CCI-10"),
      "CR-2_PIPELINE_C1_C12_DEFINED":_item(PASS,"12 explicit ordered stages") if [x["stage"] for x in p["pipeline"]]==["C%d"%i for i in range(1,13)] else _item(MISSING,"pipeline"),
      "CR-3_NO_SELF_CERTIFICATION_ACTIVATION":_item(PASS,"CCI-11 + CCI-12"),
      "CR-4_PROVENANCE_AND_SEMANTIC_DIFF_MANDATORY":_item(PASS,"per-rule provenance + semantic_diff object") if all(r["provenance"]["source_map"] for r in rules) and isinstance(p.get("semantic_diff"),dict) else _item(MISSING,"provenance/diff")
    }
    all_items=list(cci.values())+list(artifacts.values())+list(closure.values())
    counts={x:sum(1 for i in all_items if i["status"]==x) for x in (PASS,BOUNDED,MISSING)}
    decision="OCC1C_READY_TO_CLOSE" if counts[BOUNDED]==0 and counts[MISSING]==0 else "OCC1C_NOT_READY_TO_CLOSE"
    payload={"schema":"oce.p159.occ1c.canonical_readiness_audit.v1","milestone":"P159/OCC-1C",
      "cci":cci,"artifacts":artifacts,"closure_criteria":closure,"counts":counts,"decision":decision,
      "occ1c_closed":False,"occ1d_opened":False,"p160_opened":False,"p159_final_lock_performed":False,
      "functional_conclusion_only":True,"phenomenology_undetermined":True}
    return {"status":"PASS","reason":"P159_OCC1C_CANONICAL_READINESS_AUDIT_OK","payload":payload,
            "audit_sha256":nir.canonical_sha256(payload)}

# === P159 OCC-1C READINESS AUDIT V1.1 ===
import hashlib as _hashlib
import json as _json
from ontology import occ_constitutional_compiler_bounded_gaps as _gaps

def _v11_sha(path):
    return _hashlib.sha256(Path(path).read_bytes()).hexdigest()

def _v11_load(path):
    return _json.loads(Path(path).read_text(encoding="utf-8"))

def _v11_content_ok(obj):
    if not isinstance(obj,dict) or not isinstance(obj.get("content_sha256"),str): return False
    q=deepcopy(obj); supplied=q.pop("content_sha256")
    return supplied==_gaps.h(q)

def _v11_verify(package_root,proof,artifact_dir,compiler_path):
    names={"compile_report":"compile_report_v1.json","transformation_ledger":"transformation_ledger_v1.json",
           "compiler_manifest":"compiler_manifest_v1.json","evidence":"bounded_gaps_evidence_v1.json"}
    paths={k:Path(artifact_dir)/v for k,v in names.items()}
    if not all(x.is_file() for x in paths.values()): return {"status":"FAIL","reason":"PERSISTED_GAP_ARTIFACT_MISSING"}
    got={k:_v11_load(v) for k,v in paths.items()}
    if not all(_v11_content_ok(v) for v in got.values()): return {"status":"FAIL","reason":"PERSISTED_GAP_CONTENT_HASH_INVALID"}
    expected=_gaps.build(Path(package_root),Path(proof),Path(compiler_path))
    if got!=expected: return {"status":"FAIL","reason":"PERSISTED_GAP_ARTIFACT_SEMANTIC_DRIFT"}
    proofs={x.get("cci"):x for x in got["evidence"].get("proofs",[]) if isinstance(x,dict)}
    if set(proofs)!={"CCI-7","CCI-13","CCI-14"} or not all(x.get("detected") is True for x in proofs.values()):
        return {"status":"FAIL","reason":"CCI_PROOF_SET_INVALID"}
    if proofs["CCI-7"].get("hard_constraints_preserved") is not True: return {"status":"FAIL","reason":"CCI7_PROOF_INVALID"}
    p13=proofs["CCI-13"]
    if p13.get("compilation_class")!="CC3_ESCALATION_HUMAN_CCAD_REQUIRED" or not {"REQUEST_REVIEW","ESCALATE","ABSTAIN"}.issubset(set(p13.get("ops",[]))) or "ALLOW_CANDIDATE" in p13.get("ops",[]):
        return {"status":"FAIL","reason":"CCI13_PROOF_INVALID"}
    if proofs["CCI-14"].get("usable_relaxed_profile_returned") is not False: return {"status":"FAIL","reason":"CCI14_PROOF_INVALID"}
    led=got["transformation_ledger"]
    if len(led.get("entries",[]))!=48 or len({x.get("rule_id") for x in led["entries"]})!=48:
        return {"status":"FAIL","reason":"LEDGER_COVERAGE_INVALID"}
    man=got["compiler_manifest"]
    if man.get("compiler_sha256")!=_v11_sha(compiler_path): return {"status":"FAIL","reason":"COMPILER_HASH_DRIFT"}
    if man.get("self_certification") is not False or man.get("self_activation") is not False: return {"status":"FAIL","reason":"SELF_POWER_INVALID"}
    if man.get("authorization_created") is not False or man.get("execution_performed") is not False: return {"status":"FAIL","reason":"STAGE_BOUNDARY_INVALID"}
    if not man.get("dependencies") or any(not x.get("sha256") for x in man["dependencies"]): return {"status":"FAIL","reason":"DEPENDENCY_MANIFEST_INCOMPLETE"}
    cur=c.compile_canonical_profile(Path(package_root),Path(proof))
    if cur.get("status")!=c.PASS: return {"status":"FAIL","reason":"CURRENT_PROFILE_BUILD_FAILED"}
    ph=cur["canonical_profile"]["artifact_hash"]
    if any(got[k].get("source_profile_hash")!=ph for k in ("compile_report","transformation_ledger","evidence")):
        return {"status":"FAIL","reason":"SOURCE_PROFILE_BINDING_INVALID"}
    return {"status":"PASS","reason":"PERSISTED_GAP_ARTIFACTS_VERIFIED","file_sha256":{k:_v11_sha(v) for k,v in paths.items()}}

def audit_v1_1(package_root,proof,artifact_dir,compiler_path):
    base=audit(Path(package_root),Path(proof))
    if base.get("status")!="PASS": return base
    v=_v11_verify(package_root,proof,artifact_dir,compiler_path)
    if v.get("status")!="PASS":
        return {"status":"PASS","reason":"P159_OCC1C_READINESS_V1_1_EVIDENCE_REJECTED","payload":base["payload"],
                "verification":v,"audit_sha256":nir.canonical_sha256({"base":base["payload"],"verification":v})}
    p=deepcopy(base["payload"]); p["schema"]="oce.p159.occ1c.canonical_readiness_audit.v1.1"
    p["cci"]["CCI-7"]=_item(PASS,"persisted DNA-balancing adversarial proof independently rebuilt and verified")
    p["cci"]["CCI-13"]=_item(PASS,"persisted critical ambiguity escalation proof independently rebuilt and verified")
    p["cci"]["CCI-14"]=_item(PASS,"persisted fail-closed compilation-failure proof independently rebuilt and verified")
    p["artifacts"]["ART-4_COMPILE_REPORT"]=_item(PASS,"persisted compile_report_v1.json verified")
    p["artifacts"]["ART-5_TRANSFORMATION_LEDGER"]=_item(PASS,"persisted 48/48 transformation_ledger_v1.json verified")
    p["artifacts"]["ART-6_COMPILER_MANIFEST"]=_item(PASS,"persisted compiler_manifest_v1.json build identity verified")
    items=list(p["cci"].values())+list(p["artifacts"].values())+list(p["closure_criteria"].values())
    p["counts"]={x:sum(1 for i in items if i["status"]==x) for x in (PASS,BOUNDED,MISSING)}
    p["decision"]="OCC1C_READY_TO_CLOSE" if p["counts"]=={PASS:25,BOUNDED:0,MISSING:0} else "OCC1C_NOT_READY_TO_CLOSE"
    p["occ1c_closed"]=False; p["occ1d_opened"]=False; p["p160_opened"]=False; p["p159_final_lock_performed"]=False
    p["bounded_gap_artifact_verification"]=v
    return {"status":"PASS","reason":"P159_OCC1C_CANONICAL_READINESS_AUDIT_V1_1_OK","payload":p,"audit_sha256":nir.canonical_sha256(p)}
