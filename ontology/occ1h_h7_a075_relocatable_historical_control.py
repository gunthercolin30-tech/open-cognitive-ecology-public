from pathlib import Path
from ontology.governed_isolated_probe_runner import run_isolated_generated_probe, as_completed_process
from ontology.bounded_filesystem_validation_context import BoundedFilesystemValidationContext
import hashlib, json, shutil, sys, tempfile

SCHEMA="oce.p159.occ1h.a075.relocatable_historical_control.v1"
HISTORICAL_VERIFIER_SHA256="dfd4aa673abb58a08d9970a9d320f5efee7d4409173f985a1f1cce1af87f90f0"
HISTORICAL_BUILDER_SHA256="0ae2b0e5728f1db3b9a07cdef16fd553a5a9e45efaf68fe6dee82e797a1d35b4"
CURRENT_BUILDER_SHA256="b1e0ad044f6c2f59c37e71e6b03519c4d707e2b50d9b7e8ba187437b5d964828"
HISTORICAL_NIR_SHA256="fda1e90e101ca5568a54a70b4f4dcac2b8833c8d8b38474387448eaa957ebde3"

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def canonical_hash(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def result(reason,obs,control=False):
    r={"schema":SCHEMA,"scenario":"A075","classification":"INCONCLUSIVE","reason":reason,
       "relocatable_historical_control_verified":bool(control),"observations":obs,
       "diagnostic_only":True,"attack_phase_executed":False,"a075_verdict_changed":False,
       "historical_evidence_rewritten":False,"occ1f_modified":False,
       "authorization_created":False,"execution_performed":False,
       "occ1h_closed":False,"occ1i_opened":False,"p159_final_lock":False,"p160_opened":False,
       "functional_only":True,"phenomenology_undetermined":True}
    r["evidence_sha256"]=canonical_hash(r)
    return r

def copy(root,sandbox,rel,filesystem_context):
    src=root/rel; dst=sandbox/rel
    if src.is_file():
        filesystem_context.copy2_from(src,dst.relative_to(filesystem_context.root)); return
    if src.is_dir():
        filesystem_context.copytree_from(src,dst.relative_to(filesystem_context.root)); return
    raise RuntimeError("A075_REQUIRED_INPUT_MISSING:"+rel)

def child(sandbox):
    f=sandbox/"a075_relocatable_control_child.py"
    lines=[
      "import hashlib,json,sys",
      "from pathlib import Path",
      "root=Path(sys.argv[1]).resolve()",
      "sys.path.insert(0,str(root))",
      "from ontology import occ_independent_constitutional_verification_report as report",
      "from ontology import occ_independent_constitutional_verifier as verifier",
      "def ch(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()",
      "persisted=json.loads((root/report.COMMON_TCB_REL).read_text(encoding='utf-8'))",
      "rebuilt=report.build_common_tcb_manifest(root)",
      "def normalized(v):",
      " x=json.loads(json.dumps(v))",
      " x.pop('artifact_sha256',None)",
      " for c in x.get('components',[]): c.pop('path',None)",
      " return x",
      "p=normalized(persisted); r=normalized(rebuilt)",
      "diff_keys=sorted(set(p.keys())|set(r.keys()))",
      "different=[k for k in diff_keys if p.get(k)!=r.get(k)]",
      "pc={c['tcb_id']:c for c in persisted.get('components',[])}",
      "rc={c['tcb_id']:c for c in rebuilt.get('components',[])}",
      "component_ids_match=list(pc.keys())==list(rc.keys())",
      "component_nonpath=[]",
      "path_differences=[]",
      "for tid in pc:",
      " a=dict(pc[tid]); b=dict(rc.get(tid,{})); ap=a.pop('path',None); bp=b.pop('path',None)",
      " if a!=b: component_nonpath.append({'tcb_id':tid,'persisted':a,'rebuilt':b})",
      " if ap!=bp: path_differences.append({'tcb_id':tid,'persisted_path':ap,'rebuilt_path':bp})",
      "out={'persisted_self_hash_valid':report._validate_self_hash(persisted),",
      " 'persisted_verifier_identity':persisted.get('verifier_identity'),",
      " 'rebuilt_verifier_identity':rebuilt.get('verifier_identity'),",
      " 'component_ids_match':component_ids_match,'component_nonpath_differences':component_nonpath,",
      " 'path_differences':path_differences,'normalized_top_level_differences':different,",
      " 'normalized_persisted_hash':ch(p),'normalized_rebuilt_hash':ch(r),",
      " 'strict_equal':persisted==rebuilt}",
      "print(json.dumps(out,sort_keys=True))",
    ]
    code=chr(10).join(lines)+chr(10)
    compile(code,str(f),"exec")
    f.write_text(code,encoding="utf-8")
    cp=as_completed_process(run_isolated_generated_probe(script=f, sandbox=sandbox, timeout_seconds=30))
    if cp.returncode!=0:
        return {"child_failed":True,"returncode":cp.returncode,"stdout":cp.stdout[-2000:],"stderr":cp.stderr[-2000:]}
    try: return json.loads(cp.stdout.strip().splitlines()[-1])
    except Exception as e:
        return {"child_failed":True,"parse_error":type(e).__name__+":"+str(e),"stdout":cp.stdout[-2000:],"stderr":cp.stderr[-2000:]}

def run(root):
    root=Path(root); inv=root/"ontology_inventory.txt"
    if not inv.is_file(): raise RuntimeError("ONTOLOGY_INVENTORY_MISSING")
    txt=inv.read_text(encoding="utf-8",errors="replace")
    for n in ("occ_independent_constitutional_verifier","occ_independent_constitutional_verification_report"):
        if n not in txt: raise RuntimeError("ONTOLOGY_INVENTORY_PRIMITIVE_MISSING:"+n)
    verifier=root/"ontology/occ_independent_constitutional_verifier.py"
    builder=root/"ontology/occ_normative_ir_real_builder.py"
    old_builder=root/"ontology/occ_normative_ir_real_builder.py.bak"
    nir=root/"ontology/occ_normative_ir.py"
    pre={"verifier_sha256":sha(verifier),"builder_sha256":sha(builder),
         "historical_builder_sha256":sha(old_builder) if old_builder.is_file() else None,"nir_sha256":sha(nir)}
    if pre["verifier_sha256"]!=HISTORICAL_VERIFIER_SHA256: return result("INCUMBENT_VERIFIER_IDENTITY_DRIFT",{"preflight":pre})
    if pre["builder_sha256"]!=CURRENT_BUILDER_SHA256: return result("CURRENT_BUILDER_IDENTITY_DRIFT",{"preflight":pre})
    if pre["historical_builder_sha256"]!=HISTORICAL_BUILDER_SHA256: return result("HISTORICAL_BUILDER_UNAVAILABLE_OR_DRIFTED",{"preflight":pre})
    if pre["nir_sha256"]!=HISTORICAL_NIR_SHA256: return result("NIR_IDENTITY_DRIFT",{"preflight":pre})
    from ontology import occ_independent_constitutional_verifier as incumbent
    closure=["ontology/dna_adversarial_regression.py","ontology/dna_fitness_suite.py","ontology/dna_fundamental.py",
      "ontology/dna_inheritance.py","ontology/dna_mutation_protocol.py","ontology/dna_registry.py",
      "ontology/dna_rule_contract.py","ontology/dna_severity_model.py","ontology/dna_stack.py",
      "ontology/dna_versioning_lineage.py","ontology/minimal_dna.py","ontology/normative_hierarchy.py",
      "ontology/occ_independent_constitutional_verification_report.py","ontology/occ_independent_constitutional_verifier.py",
      "ontology/occ_normative_ir.py","ontology/occ_normative_ir_real_builder.py",
      "validation_artifacts/p159/occ1f/common_tcb_manifest_v1.json",
      "validation_artifacts/p159/occ1f/verifier_check_registry_v1.json"]
    for q in incumbent.paths(root).values():
        if q.exists(): closure.append(str(q.relative_to(root)))
    filesystem_context = BoundedFilesystemValidationContext(prefix="oce-a075-relocatable-v1-")
    temp = filesystem_context.root; sandbox=temp/"repo"
    try:
        for rel in sorted(set(closure)): copy(root,sandbox,rel,filesystem_context)
        filesystem_context.copy2_from(old_builder,(sandbox/"ontology/occ_normative_ir_real_builder.py").relative_to(filesystem_context.root))
        disk={"verifier":sha(sandbox/"ontology/occ_independent_constitutional_verifier.py"),
              "builder":sha(sandbox/"ontology/occ_normative_ir_real_builder.py"),
              "nir":sha(sandbox/"ontology/occ_normative_ir.py")}
        c=child(sandbox); obs={"preflight":pre,"sandbox_disk":disk,"comparison":c}
        if c.get("child_failed"): return result("RELOCATABLE_CONTROL_CHILD_FAILED",obs)
        if c.get("persisted_self_hash_valid") is not True: return result("PERSISTED_TCB_SELF_HASH_INVALID",obs)
        if c.get("persisted_verifier_identity")!=c.get("rebuilt_verifier_identity"): return result("VERIFIER_IDENTITY_DIFFERS",obs)
        if c.get("component_ids_match") is not True: return result("TCB_COMPONENT_IDS_DIFFER",obs)
        if c.get("component_nonpath_differences"): return result("TCB_NONPATH_COMPONENT_DIFFERENCE",obs)
        if c.get("normalized_top_level_differences"): return result("TCB_NONPATH_TOP_LEVEL_DIFFERENCE",obs)
        if c.get("normalized_persisted_hash")!=c.get("normalized_rebuilt_hash"): return result("NORMALIZED_TCB_HASH_DIFFERENCE",obs)
        if c.get("strict_equal") is True: return result("CONTROL_NOT_RELOCATED_STRICT_EQUAL",obs)
        if not c.get("path_differences"): return result("EXPECTED_RELOCATION_PATH_DIFFERENCE_ABSENT",obs)
        return result("VERIFIED_RELOCATABLE_HISTORICAL_CONTROL_PATH_ONLY_DIFFERENCE",obs,True)
    finally: filesystem_context.remove_tree()
