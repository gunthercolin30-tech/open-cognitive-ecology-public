from pathlib import Path
from ontology.governed_isolated_probe_runner import run_isolated_generated_probe, as_completed_process
from ontology.bounded_filesystem_validation_context import BoundedFilesystemValidationContext
import hashlib, json, shutil, sys, tempfile
SCHEMA="oce.p159.occ1h.a075.common_tcb_resolution_probe.v1"
HISTORICAL_VERIFIER_SHA256="dfd4aa673abb58a08d9970a9d320f5efee7d4409173f985a1f1cce1af87f90f0"
HISTORICAL_BUILDER_SHA256="0ae2b0e5728f1db3b9a07cdef16fd553a5a9e45efaf68fe6dee82e797a1d35b4"
CURRENT_BUILDER_SHA256="b1e0ad044f6c2f59c37e71e6b03519c4d707e2b50d9b7e8ba187437b5d964828"
HISTORICAL_NIR_SHA256="fda1e90e101ca5568a54a70b4f4dcac2b8833c8d8b38474387448eaa957ebde3"
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def _copy(root,sandbox,rel,filesystem_context):
    src=root/rel; dst=sandbox/rel
    if src.is_file():
        filesystem_context.copy2_from(src,dst.relative_to(filesystem_context.root)); return
    if src.is_dir():
        filesystem_context.copytree_from(src,dst.relative_to(filesystem_context.root)); return
    raise RuntimeError("A075_REQUIRED_INPUT_MISSING:"+rel)
def _result(reason,obs):
    r={"schema":SCHEMA,"scenario":"A075","classification":"INCONCLUSIVE","reason":reason,"observations":obs,
       "diagnostic_only":True,"a075_verdict_changed":False,"historical_evidence_rewritten":False,
       "occ1f_modified":False,"authorization_created":False,"execution_performed":False,
       "occ1h_closed":False,"occ1i_opened":False,"p159_final_lock":False,"p160_opened":False,
       "functional_only":True,"phenomenology_undetermined":True}
    r["evidence_sha256"]=hashlib.sha256(json.dumps(r,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
    return r
def _child(sandbox):
    child=sandbox/"a075_common_tcb_resolution_child.py"
    lines=[
      "import hashlib,json,sys",
      "from pathlib import Path",
      "root=Path(sys.argv[1]).resolve()",
      "sys.path.insert(0,str(root))",
      "from ontology import occ_independent_constitutional_verifier as v",
      "from ontology import occ_independent_constitutional_verification_report as report",
      "from ontology import occ_normative_ir as nir",
      "builder=v.builder",
      "def sh(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()",
      "def ident(mod):",
      "    p=Path(mod.__file__).resolve()",
      "    return {'path':str(p),'sha256':sh(p),'inside_sandbox':root in p.parents}",
      "out={'sys_path_0':sys.path[0],'verifier':ident(v),'builder_via_verifier':ident(builder),'nir':ident(nir),'verifier_builder_module_name':getattr(builder,'__name__',None),'verify_preclose':report.verify_preclose_evidence(root)}",
      "print(json.dumps(out,sort_keys=True))",
    ]
    code=chr(10).join(lines)+chr(10)
    compile(code,str(child),"exec")
    child.write_text(code,encoding="utf-8")
    cp=as_completed_process(run_isolated_generated_probe(script=child, sandbox=sandbox, timeout_seconds=30))
    if cp.returncode!=0:
        return {"child_failed":True,"returncode":cp.returncode,"stdout":cp.stdout[-2000:],"stderr":cp.stderr[-2000:]}
    try: return json.loads(cp.stdout.strip().splitlines()[-1])
    except Exception as e:
        return {"child_failed":True,"returncode":cp.returncode,"parse_error":type(e).__name__+":"+str(e),
                "stdout":cp.stdout[-2000:],"stderr":cp.stderr[-2000:]}
def run(root):
    root=Path(root); inv=root/"ontology_inventory.txt"
    if not inv.is_file(): raise RuntimeError("ONTOLOGY_INVENTORY_MISSING")
    txt=inv.read_text(encoding="utf-8",errors="replace")
    for primitive in ("occ_independent_constitutional_verifier","occ_independent_constitutional_verification_report"):
        if primitive not in txt: raise RuntimeError("ONTOLOGY_INVENTORY_PRIMITIVE_MISSING:"+primitive)
    verifier=root/"ontology/occ_independent_constitutional_verifier.py"
    builder=root/"ontology/occ_normative_ir_real_builder.py"
    old_builder=root/"ontology/occ_normative_ir_real_builder.py.bak"
    nir=root/"ontology/occ_normative_ir.py"
    pre={"verifier_sha256":sha(verifier) if verifier.is_file() else None,
         "builder_sha256":sha(builder) if builder.is_file() else None,
         "historical_builder_available":old_builder.is_file(),
         "historical_builder_sha256":sha(old_builder) if old_builder.is_file() else None,
         "nir_sha256":sha(nir) if nir.is_file() else None}
    if pre["verifier_sha256"]!=HISTORICAL_VERIFIER_SHA256: return _result("INCUMBENT_VERIFIER_IDENTITY_DRIFT_BEFORE_DIAGNOSTIC",{"preflight":pre})
    if pre["builder_sha256"]!=CURRENT_BUILDER_SHA256: return _result("CURRENT_BUILDER_IDENTITY_DRIFT_BEFORE_DIAGNOSTIC",{"preflight":pre})
    if pre["historical_builder_sha256"]!=HISTORICAL_BUILDER_SHA256: return _result("HISTORICAL_BUILDER_FIXTURE_UNAVAILABLE_OR_DRIFTED",{"preflight":pre})
    if pre["nir_sha256"]!=HISTORICAL_NIR_SHA256: return _result("NIR_IDENTITY_DRIFT_BEFORE_DIAGNOSTIC",{"preflight":pre})
    from ontology import occ_independent_constitutional_verifier as incumbent
    closure=["ontology/dna_adversarial_regression.py","ontology/dna_fitness_suite.py","ontology/dna_fundamental.py",
      "ontology/dna_inheritance.py","ontology/dna_mutation_protocol.py","ontology/dna_registry.py",
      "ontology/dna_rule_contract.py","ontology/dna_severity_model.py","ontology/dna_stack.py",
      "ontology/dna_versioning_lineage.py","ontology/minimal_dna.py","ontology/normative_hierarchy.py",
      "ontology/occ_independent_constitutional_verification_report.py","ontology/occ_independent_constitutional_verifier.py",
      "ontology/occ_normative_ir.py","ontology/occ_normative_ir_real_builder.py",
      "validation_artifacts/p159/occ1f/common_tcb_manifest_v1.json",
      "validation_artifacts/p159/occ1f/verifier_check_registry_v1.json"]
    for path in incumbent.paths(root).values():
        if path.exists(): closure.append(str(path.relative_to(root)))
    filesystem_context = BoundedFilesystemValidationContext(prefix="oce-a075-tcb-resolution-v1-")
    temp = filesystem_context.root; sandbox=temp/"repo"
    try:
        for rel in sorted(set(closure)): _copy(root,sandbox,rel,filesystem_context)
        sb_builder=sandbox/"ontology/occ_normative_ir_real_builder.py"; filesystem_context.copy2_from(old_builder,sb_builder.relative_to(filesystem_context.root))
        disk={"sandbox_verifier_sha256":sha(sandbox/"ontology/occ_independent_constitutional_verifier.py"),
              "sandbox_builder_sha256":sha(sb_builder),"sandbox_nir_sha256":sha(sandbox/"ontology/occ_normative_ir.py")}
        child=_child(sandbox)
        obs={"preflight":pre,"sandbox_disk":disk,"child":child,
             "expected":{"verifier_sha256":HISTORICAL_VERIFIER_SHA256,"builder_sha256":HISTORICAL_BUILDER_SHA256,"nir_sha256":HISTORICAL_NIR_SHA256}}
        if child.get("child_failed"): return _result("DIAGNOSTIC_CHILD_FAILED",obs)
        vi=child.get("verifier",{}); bi=child.get("builder_via_verifier",{}); ni=child.get("nir",{})
        if not (vi.get("inside_sandbox") and bi.get("inside_sandbox") and ni.get("inside_sandbox")): return _result("COMMON_TCB_MODULE_RESOLUTION_ESCAPED_SANDBOX",obs)
        if vi.get("sha256")!=HISTORICAL_VERIFIER_SHA256: return _result("LOADED_VERIFIER_IDENTITY_MISMATCH",obs)
        if bi.get("sha256")!=HISTORICAL_BUILDER_SHA256: return _result("LOADED_BUILDER_IDENTITY_MISMATCH",obs)
        if ni.get("sha256")!=HISTORICAL_NIR_SHA256: return _result("LOADED_NIR_IDENTITY_MISMATCH",obs)
        status=child.get("verify_preclose",{}).get("status"); reason=child.get("verify_preclose",{}).get("reason")
        if status=="VERIFIED_PRECLOSE_BINDING": return _result("HISTORICAL_COMMON_TCB_RESOLUTION_CONFIRMED",obs)
        return _result("COMMON_TCB_IDENTITIES_MATCH_BUT_PRECLOSE_BINDING_REJECTED:"+str(reason),obs)
    finally: filesystem_context.remove_tree()
