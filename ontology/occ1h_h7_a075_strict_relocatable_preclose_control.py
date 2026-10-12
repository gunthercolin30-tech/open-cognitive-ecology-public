from pathlib import Path
from ontology.governed_isolated_probe_runner import run_isolated_generated_probe, as_completed_process
from ontology.bounded_filesystem_validation_context import BoundedFilesystemValidationContext
import hashlib, json, shutil, sys, tempfile

SCHEMA="oce.p159.occ1h.a075.strict_relocatable_preclose_control.v1"
HISTORICAL_VERIFIER_SHA256="dfd4aa673abb58a08d9970a9d320f5efee7d4409173f985a1f1cce1af87f90f0"
HISTORICAL_BUILDER_SHA256="0ae2b0e5728f1db3b9a07cdef16fd553a5a9e45efaf68fe6dee82e797a1d35b4"
CURRENT_BUILDER_SHA256="b1e0ad044f6c2f59c37e71e6b03519c4d707e2b50d9b7e8ba187437b5d964828"
HISTORICAL_NIR_SHA256="fda1e90e101ca5568a54a70b4f4dcac2b8833c8d8b38474387448eaa957ebde3"

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def canonical_hash(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def result(reason,obs,verified=False):
    r={"schema":SCHEMA,"scenario":"A075","classification":"INCONCLUSIVE","reason":reason,
       "strict_relocatable_preclose_verified":bool(verified),"observations":obs,
       "diagnostic_only":True,"identity_drift_simulation_executed":False,
       "a075_verdict_changed":False,"historical_evidence_rewritten":False,"occ1f_modified":False,
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
    f=sandbox/"a075_strict_relocatable_preclose_child.py"
    lines=[
      "import hashlib,json,sys",
      "from pathlib import Path",
      "root=Path(sys.argv[1]).resolve()",
      "sys.path.insert(0,str(root))",
      "from ontology import occ_independent_constitutional_verification_report as report",
      "from ontology import occ_independent_constitutional_verifier as verifier",
      "def fh(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()",
      "tcb_path=root/report.COMMON_TCB_REL",
      "persisted=json.loads(tcb_path.read_text(encoding='utf-8'))",
      "before=json.loads(json.dumps(persisted))",
      "rebuilt=report.build_common_tcb_manifest(root)",
      "rebuilt_by_id={c['tcb_id']:c for c in rebuilt.get('components',[])}",
      "changed=[]",
      "for c in persisted.get('components',[]):",
      " tid=c.get('tcb_id'); rc=rebuilt_by_id.get(tid,{})",
      " if c.get('path')!=rc.get('path'):",
      "  changed.append({'tcb_id':tid,'old_path':c.get('path'),'new_path':rc.get('path')})",
      "  c['path']=rc.get('path')",
      "persisted.pop('artifact_sha256',None)",
      "persisted['artifact_sha256']=report._canonical_hash(persisted)",
      "tcb_path.write_text(json.dumps(persisted,indent=2,sort_keys=True,ensure_ascii=False)+'\\n',encoding='utf-8')",
      "status=report.verify_preclose_evidence(root)",
      "after=json.loads(tcb_path.read_text(encoding='utf-8'))",
      "out={'loaded_verifier_path':str(Path(verifier.__file__).resolve()),",
      " 'loaded_verifier_sha256':fh(Path(verifier.__file__).resolve()),",
      " 'path_changes':changed,'path_change_count':len(changed),",
      " 'only_component_paths_relocalized':all(set(x.keys())=={'tcb_id','old_path','new_path'} for x in changed),",
      " 'persisted_self_hash_valid_after':report._validate_self_hash(after),",
      " 'strict_equal_to_rebuilt_after':after==report.build_common_tcb_manifest(root),",
      " 'verify_preclose':status}",
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
    root=Path(root)
    inv=root/"ontology_inventory.txt"
    if not inv.is_file(): raise RuntimeError("ONTOLOGY_INVENTORY_MISSING")
    txt=inv.read_text(encoding="utf-8",errors="replace")
    for n in ("occ_independent_constitutional_verifier","occ_independent_constitutional_verification_report"):
        if n not in txt: raise RuntimeError("ONTOLOGY_INVENTORY_PRIMITIVE_MISSING:"+n)

    verifier=root/"ontology/occ_independent_constitutional_verifier.py"
    builder=root/"ontology/occ_normative_ir_real_builder.py"
    old_builder=root/"ontology/occ_normative_ir_real_builder.py.bak"
    nir=root/"ontology/occ_normative_ir.py"
    pre={"verifier_sha256":sha(verifier),"builder_sha256":sha(builder),
         "historical_builder_sha256":sha(old_builder) if old_builder.is_file() else None,
         "nir_sha256":sha(nir)}
    if pre["verifier_sha256"]!=HISTORICAL_VERIFIER_SHA256: return result("INCUMBENT_VERIFIER_IDENTITY_DRIFT",{"preflight":pre})
    if pre["builder_sha256"]!=CURRENT_BUILDER_SHA256: return result("CURRENT_BUILDER_IDENTITY_DRIFT",{"preflight":pre})
    if pre["historical_builder_sha256"]!=HISTORICAL_BUILDER_SHA256: return result("HISTORICAL_BUILDER_UNAVAILABLE_OR_DRIFTED",{"preflight":pre})
    if pre["nir_sha256"]!=HISTORICAL_NIR_SHA256: return result("NIR_IDENTITY_DRIFT",{"preflight":pre})

    from ontology import occ_independent_constitutional_verifier as incumbent
    closure=[
      "ontology/dna_adversarial_regression.py","ontology/dna_fitness_suite.py","ontology/dna_fundamental.py",
      "ontology/dna_inheritance.py","ontology/dna_mutation_protocol.py","ontology/dna_registry.py",
      "ontology/dna_rule_contract.py","ontology/dna_severity_model.py","ontology/dna_stack.py",
      "ontology/dna_versioning_lineage.py","ontology/minimal_dna.py","ontology/normative_hierarchy.py",
      "ontology/occ_independent_constitutional_verification_report.py","ontology/occ_independent_constitutional_verifier.py",
      "ontology/occ_normative_ir.py","ontology/occ_normative_ir_real_builder.py",
      "validation_artifacts/p159/occ1f/common_tcb_manifest_v1.json",
      "validation_artifacts/p159/occ1f/verifier_check_registry_v1.json"]
    for q in incumbent.paths(root).values():
        if q.exists(): closure.append(str(q.relative_to(root)))

    filesystem_context = BoundedFilesystemValidationContext(prefix="oce-a075-strict-control-v1-")
    temp = filesystem_context.root; sandbox=temp/"repo"
    try:
        for rel in sorted(set(closure)): copy(root,sandbox,rel,filesystem_context)
        filesystem_context.copy2_from(old_builder,(sandbox/"ontology/occ_normative_ir_real_builder.py").relative_to(filesystem_context.root))
        disk={"verifier":sha(sandbox/"ontology/occ_independent_constitutional_verifier.py"),
              "builder":sha(sandbox/"ontology/occ_normative_ir_real_builder.py"),
              "nir":sha(sandbox/"ontology/occ_normative_ir.py")}
        c=child(sandbox)
        obs={"preflight":pre,"sandbox_disk":disk,"strict_control":c}
        if c.get("child_failed"): return result("STRICT_RELOCATABLE_CONTROL_CHILD_FAILED",obs)
        if c.get("loaded_verifier_sha256")!=HISTORICAL_VERIFIER_SHA256: return result("STRICT_CONTROL_VERIFIER_IDENTITY_MISMATCH",obs)
        if c.get("path_change_count")!=2: return result("UNEXPECTED_RELOCATION_PATH_CHANGE_COUNT",obs)
        if c.get("only_component_paths_relocalized") is not True: return result("RELOCATION_CHANGED_NONPATH_FIELDS",obs)
        if c.get("persisted_self_hash_valid_after") is not True: return result("RELOCALIZED_TCB_SELF_HASH_INVALID",obs)
        if c.get("strict_equal_to_rebuilt_after") is not True: return result("RELOCALIZED_TCB_NOT_STRICTLY_EQUAL_TO_REBUILD",obs)
        if c.get("verify_preclose",{}).get("status")!="VERIFIED_PRECLOSE_BINDING":
            return result("STRICT_RELOCATABLE_PRECLOSE_NOT_VERIFIED",obs)
        return result("STRICT_RELOCATABLE_HISTORICAL_PRECLOSE_VERIFIED",obs,True)
    finally:
        filesystem_context.remove_tree()
