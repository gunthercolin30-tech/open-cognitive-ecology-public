from pathlib import Path
from ontology.governed_isolated_probe_runner import run_isolated_generated_probe, as_completed_process
from ontology.bounded_filesystem_validation_context import BoundedFilesystemValidationContext
import hashlib, json, shutil, sys, tempfile

SCHEMA="oce.p159.occ1h.a075.defensive_identity_drift_discrimination.v1"
HISTORICAL_VERIFIER_SHA256="dfd4aa673abb58a08d9970a9d320f5efee7d4409173f985a1f1cce1af87f90f0"
HISTORICAL_BUILDER_SHA256="0ae2b0e5728f1db3b9a07cdef16fd553a5a9e45efaf68fe6dee82e797a1d35b4"
CURRENT_BUILDER_SHA256="b1e0ad044f6c2f59c37e71e6b03519c4d707e2b50d9b7e8ba187437b5d964828"
HISTORICAL_NIR_SHA256="fda1e90e101ca5568a54a70b4f4dcac2b8833c8d8b38474387448eaa957ebde3"

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ch(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def result(classification,reason,obs):
    r={"schema":SCHEMA,"scenario":"A075","classification":classification,"reason":reason,
       "observations":obs,"defensive_validation_only":True,"temporary_fixture_only":True,
       "real_runtime_identity_modified":False,"historical_evidence_rewritten":False,
       "authorization_created":False,"execution_performed":False,
       "functional_only":True,"phenomenology_undetermined":True,
       "occ1h_closed":False,"occ1i_opened":False,"p159_final_lock":False,"p160_opened":False}
    r["evidence_sha256"]=ch(r); return r

def cp(root,sandbox,rel,filesystem_context):
    s=root/rel; d=sandbox/rel
    if s.is_file():
        filesystem_context.copy2_from(s,d.relative_to(filesystem_context.root)); return
    if s.is_dir():
        filesystem_context.copytree_from(s,d.relative_to(filesystem_context.root)); return
    raise RuntimeError("A075_REQUIRED_INPUT_MISSING:"+rel)

def run_child(sandbox,mode):
    f=sandbox/("a075_defensive_"+mode+".py")
    lines=[
      "import hashlib,json,sys",
      "from pathlib import Path",
      "root=Path(sys.argv[1]).resolve(); sys.path.insert(0,str(root))",
      "from ontology import occ_independent_constitutional_verification_report as r",
      "from ontology import occ_independent_constitutional_verifier as v",
      "def fh(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()",
      "tcb=root/r.COMMON_TCB_REL; reg=root/r.CHECK_REGISTRY_REL",
      "out={'loaded_verifier_sha256':fh(Path(v.__file__).resolve()),'pre':r.verify_preclose_evidence(root)}",
      "if sys.argv[2]=='measure':",
      " out['old_tcb_sha256']=fh(tcb); out['old_registry_sha256']=fh(reg)",
      " try:",
      "  r.materialize_preclose_evidence(root); out['rebind_attempt']='SUCCEEDED'",
      " except Exception as e:",
      "  out['rebind_attempt']='REJECTED'; out['rebind_error']=type(e).__name__+':'+str(e)",
      " out['post']=r.verify_preclose_evidence(root)",
      " out['new_tcb_sha256']=fh(tcb); out['new_registry_sha256']=fh(reg)",
      " td=json.loads(tcb.read_text()); rd=json.loads(reg.read_text())",
      " out['tcb_bound_verifier_sha256']=td.get('verifier_identity',{}).get('file_sha256')",
      " out['registry_bound_verifier_sha256']=rd.get('verifier_identity',{}).get('file_sha256')",
      "print(json.dumps(out,sort_keys=True))",
    ]
    code=chr(10).join(lines)+chr(10); compile(code,str(f),"exec"); f.write_text(code,encoding="utf-8")
    p=as_completed_process(run_isolated_generated_probe(script=f, sandbox=sandbox, args=(mode,), timeout_seconds=30))
    if p.returncode: return {"child_failed":True,"stderr":p.stderr[-2000:],"stdout":p.stdout[-2000:]}
    return json.loads(p.stdout.strip().splitlines()[-1])

def relocalize_tcb(sandbox):
    sys.path.insert(0,str(sandbox))
    # Done in isolated child to avoid module cache contamination.
    f=sandbox/"a075_relocalize.py"
    lines=[
      "import json,sys","from pathlib import Path","root=Path(sys.argv[1]).resolve(); sys.path.insert(0,str(root))",
      "from ontology import occ_independent_constitutional_verification_report as r",
      "p=root/r.COMMON_TCB_REL; x=json.loads(p.read_text()); y=r.build_common_tcb_manifest(root)",
      "m={c['tcb_id']:c for c in y['components']}",
      "for c in x['components']:",
      " c['path']=m[c['tcb_id']]['path']",
      "x.pop('artifact_sha256',None); x['artifact_sha256']=r._canonical_hash(x)",
      "p.write_text(json.dumps(x,indent=2,sort_keys=True,ensure_ascii=False)+'\\n')",
      "print(json.dumps(r.verify_preclose_evidence(root),sort_keys=True))"]
    code=chr(10).join(lines)+chr(10); compile(code,str(f),"exec"); f.write_text(code)
    p=as_completed_process(run_isolated_generated_probe(script=f, sandbox=sandbox, timeout_seconds=30))
    if p.returncode: return {"status":"ERROR","detail":p.stderr[-2000:]}
    return json.loads(p.stdout.strip().splitlines()[-1])

def run(root):
    root=Path(root)
    inv=root/"ontology_inventory.txt"
    if not inv.is_file(): raise RuntimeError("ONTOLOGY_INVENTORY_MISSING")
    it=inv.read_text(encoding="utf-8",errors="replace")
    for n in ("occ_independent_constitutional_verifier","occ_independent_constitutional_verification_report"):
        if n not in it: raise RuntimeError("ONTOLOGY_INVENTORY_PRIMITIVE_MISSING:"+n)

    vp=root/"ontology/occ_independent_constitutional_verifier.py"
    bp=root/"ontology/occ_normative_ir_real_builder.py"; hb=root/"ontology/occ_normative_ir_real_builder.py.bak"
    np=root/"ontology/occ_normative_ir.py"
    pre={"verifier":sha(vp),"builder":sha(bp),"historical_builder":sha(hb) if hb.is_file() else None,"nir":sha(np)}
    if pre["verifier"]!=HISTORICAL_VERIFIER_SHA256: return result("INCONCLUSIVE","INCUMBENT_VERIFIER_IDENTITY_DRIFT",{"preflight":pre})
    if pre["builder"]!=CURRENT_BUILDER_SHA256: return result("INCONCLUSIVE","CURRENT_BUILDER_IDENTITY_DRIFT",{"preflight":pre})
    if pre["historical_builder"]!=HISTORICAL_BUILDER_SHA256: return result("INCONCLUSIVE","HISTORICAL_BUILDER_UNAVAILABLE",{"preflight":pre})
    if pre["nir"]!=HISTORICAL_NIR_SHA256: return result("INCONCLUSIVE","NIR_IDENTITY_DRIFT",{"preflight":pre})

    from ontology import occ_independent_constitutional_verifier as inc
    closure=["ontology/dna_adversarial_regression.py","ontology/dna_fitness_suite.py","ontology/dna_fundamental.py",
      "ontology/dna_inheritance.py","ontology/dna_mutation_protocol.py","ontology/dna_registry.py",
      "ontology/dna_rule_contract.py","ontology/dna_severity_model.py","ontology/dna_stack.py",
      "ontology/dna_versioning_lineage.py","ontology/minimal_dna.py","ontology/normative_hierarchy.py",
      "ontology/occ_independent_constitutional_verification_report.py","ontology/occ_independent_constitutional_verifier.py",
      "ontology/occ_normative_ir.py","ontology/occ_normative_ir_real_builder.py",
      "validation_artifacts/p159/occ1f/common_tcb_manifest_v1.json","validation_artifacts/p159/occ1f/verifier_check_registry_v1.json",
      "validation_artifacts/p159/occ1f/verifier_identity_authorization_anchor_v1.json",
      "oif_review/campaigns/P159-OCC1A/occ1a_initial_development_authority_materialization.json"]
    for q in inc.paths(root).values():
        if q.exists(): closure.append(str(q.relative_to(root)))

    filesystem_context = BoundedFilesystemValidationContext(prefix="oce-a075-defensive-v1-")
    temp = filesystem_context.root; sandbox=temp/"repo"
    try:
        for rel in sorted(set(closure)): cp(root,sandbox,rel,filesystem_context)
        filesystem_context.copy2_from(hb,(sandbox/"ontology/occ_normative_ir_real_builder.py").relative_to(filesystem_context.root))
        baseline=relocalize_tcb(sandbox)
        if baseline.get("status")!="VERIFIED_PRECLOSE_BINDING":
            return result("INCONCLUSIVE","BASELINE_NOT_VERIFIED",{"preflight":pre,"baseline":baseline})

        # Controlled identity drift, temporary fixture only.
        sv=sandbox/"ontology/occ_independent_constitutional_verifier.py"
        original=sv.read_text(encoding="utf-8")
        marker='lm.get("self_activation") is False'
        if marker not in original:
            return result("INCONCLUSIVE","DEFENSIVE_DRIFT_MARKER_MISSING",{"preflight":pre,"baseline":baseline})
        sv.write_text(original.replace(marker,"True",1),encoding="utf-8")
        drift_sha=sha(sv)
        measured=run_child(sandbox,"measure")
        obs={"preflight":pre,"baseline":baseline,"drifted_verifier_sha256":drift_sha,"measurement":measured}
        if measured.get("child_failed"): return result("INCONCLUSIVE","DEFENSIVE_MEASUREMENT_FAILED",obs)

        loaded=measured.get("loaded_verifier_sha256")==drift_sha
        pre_rejected=measured.get("pre",{}).get("status")=="REJECTED"
        rebound=(measured.get("tcb_bound_verifier_sha256")==drift_sha and measured.get("registry_bound_verifier_sha256")==drift_sha)
        post_verified=measured.get("post",{}).get("status")=="VERIFIED_PRECLOSE_BINDING"
        changed=(measured.get("old_tcb_sha256")!=measured.get("new_tcb_sha256") or measured.get("old_registry_sha256")!=measured.get("new_registry_sha256"))

        if loaded and pre_rejected and measured.get("rebind_attempt")=="SUCCEEDED" and changed and rebound and post_verified:
            return result("ASSURANCE_GAP","PRECLOSE_TRUST_CAN_BE_REBOUND_TO_DRIFTED_VERIFIER_WITHIN_EXISTING_TRUST_CHAIN",obs)
        if loaded and pre_rejected and measured.get("rebind_attempt")=="REJECTED" and not post_verified:
            return result("RESISTED","DRIFTED_VERIFIER_IDENTITY_REJECTED_AFTER_VERIFIED_BASELINE",obs)
        return result("INCONCLUSIVE","DEFENSIVE_EXPERIMENT_DID_NOT_DISCRIMINATE",obs)
    finally:
        filesystem_context.remove_tree()
