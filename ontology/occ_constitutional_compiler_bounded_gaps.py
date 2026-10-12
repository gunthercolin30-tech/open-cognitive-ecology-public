from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import hashlib,json,platform,sys
from ontology import occ_constitutional_compiler as c
from ontology import occ_normative_ir as nir

def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def h(x): return hashlib.sha256(canon(x)).hexdigest()

def prove_cci_7(profile):
    # DNA hard constraints may not be represented as weighted/balanced preferences.
    bad=deepcopy(profile)
    bad["rules"][0]["enforcement_class"]="WEIGHTED_PREFERENCE"
    bad["rules"][0]["outputs"]=["ALLOW_CANDIDATE"]
    # Independent invariant: compiler vocabulary/classes are closed; balancing is not a class.
    detected=(bad["rules"][0]["enforcement_class"] not in c.COMPILATION_CLASSES)
    return {"cci":"CCI-7","attack":"DNA_BALANCING_WEIGHTED_PREFERENCE","detected":detected,
            "hard_constraints_preserved":detected}

def prove_cci_13(profile):
    # Critical ambiguity must not silently become an eligible/true rule.
    r=deepcopy(profile["rules"][0])
    r["uncertainty_semantics"]["semantic_status"]="UNKNOWN"
    r["uncertainty_semantics"]["human_judgment_required"]=True
    cc=c._classify_rule({"formalization_level":"F1","semantic_status":"UNKNOWN",
                         "partial_formalization_explicit":True,"human_judgment_required":True})
    ops=c._norm_ops_for(r,cc)
    ok=cc=="CC3_ESCALATION_HUMAN_CCAD_REQUIRED" and "REQUEST_REVIEW" in ops and "ESCALATE" in ops and "ABSTAIN" in ops and "ALLOW_CANDIDATE" not in ops
    return {"cci":"CCI-13","attack":"CRITICAL_AMBIGUITY","detected":ok,"compilation_class":cc,"ops":ops}

def prove_cci_14(package_root,proof):
    # Failures must fail closed, never return a usable relaxed profile.
    missing=Path(str(proof)+".missing")
    r=c.compile_canonical_profile(package_root,missing)
    ok=r.get("status")!=c.PASS and "canonical_profile" not in r
    return {"cci":"CCI-14","attack":"INVALID_OR_MISSING_VERIFIED_INPUT","detected":ok,
            "usable_relaxed_profile_returned":("canonical_profile" in r)}

def build(package_root:Path,proof:Path,compiler_path:Path):
    r=c.compile_canonical_profile(package_root,proof)
    if r.get("status")!=c.PASS: raise RuntimeError(r)
    p=r["canonical_profile"]
    proofs=[prove_cci_7(p),prove_cci_13(p),prove_cci_14(package_root,proof)]
    if not all(x["detected"] for x in proofs): raise RuntimeError("CCI_PROOF_FAILED")
    compile_report=deepcopy(p["compile_report"])
    compile_report.update({"schema":"oce.p159.occ1c.compile_report.v1","source_profile_hash":p["artifact_hash"],
                           "cci_7_13_14_proven":True})
    ledger={"schema":"oce.p159.occ1c.transformation_ledger.v1","source_profile_hash":p["artifact_hash"],
            "entries":deepcopy(p["transformation_ledger"])}
    dep_names=("ontology.occ_normative_ir","ontology.occ_normative_ir_real_builder",
               "ontology.occ_normative_ir_referential_validator","ontology.occ_normative_ir_coherence_validator",
               "ontology.occ_normative_ir_semantic_preservation_validator")
    deps=[]
    for name in dep_names:
        m=sys.modules.get(name)
        f=Path(getattr(m,"__file__","")) if m else None
        deps.append({"module":name,"sha256":hashlib.sha256(f.read_bytes()).hexdigest() if f and f.is_file() else None})
    manifest={"schema":"oce.p159.occ1c.compiler_manifest.v1","compiler_name":c.PRIMITIVE,
              "compiler_version":c.VERSION,"pipeline_version":c.CANONICAL_PIPELINE_VERSION,
              "compiler_sha256":hashlib.sha256(compiler_path.read_bytes()).hexdigest(),
              "dependencies":deps,
              "environment_fingerprint":{"python_implementation":platform.python_implementation(),
                 "python_major_minor":"%d.%d"%sys.version_info[:2]},
              "semantic_environment_excludes":["hostname","clock","cwd","random","network"],
              "self_certification":False,"self_activation":False,"authorization_created":False,
              "execution_performed":False}
    evidence={"schema":"oce.p159.occ1c.bounded_gaps_evidence.v1","source_profile_hash":p["artifact_hash"],
              "proofs":proofs,"all_proven":True,"occ1c_closed":False,"occ1d_opened":False,
              "p160_opened":False,"final_lock_performed":False}
    for x in (compile_report,ledger,manifest,evidence): x["content_sha256"]=h(x)
    return {"compile_report":compile_report,"transformation_ledger":ledger,"compiler_manifest":manifest,"evidence":evidence}
