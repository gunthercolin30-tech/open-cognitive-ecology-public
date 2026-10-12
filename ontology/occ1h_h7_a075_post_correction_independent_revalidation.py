from __future__ import annotations
from pathlib import Path
from typing import Any, Dict
import hashlib, importlib.util, json, shutil, sys, tempfile

SCHEMA="oce.p159.occ1h.a075.post_correction_independent_revalidation.v1"
AUTHORIZED_VERIFIER_SHA="dfd4aa673abb58a08d9970a9d320f5efee7d4409173f985a1f1cce1af87f90f0"
HISTORICAL_BUILDER_SHA="0ae2b0e5728f1db3b9a07cdef16fd553a5a9e45efaf68fe6dee82e797a1d35b4"
ANCHOR_REL=Path("validation_artifacts/p159/occ1f/verifier_identity_authorization_anchor_v1.json")
AUTHORITY_REL=Path("oif_review/campaigns/P159-OCC1A/occ1a_initial_development_authority_materialization.json")
HIST_REL=Path("validation_artifacts/p159/occ1h/a075_defensive_assurance_gap_historization_v1.json")

def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def _canonical_hash(v: Dict[str,Any]) -> str:
    x=dict(v); x.pop("evidence_sha256",None)
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def _copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)

def _local_ontology_closure(root: Path) -> list[Path]:
    """Resolve local ontology imports statically; never execute repository modules."""
    import ast
    seeds=[
        root/"ontology/occ_independent_constitutional_verification_report.py",
        root/"ontology/occ_independent_constitutional_verifier.py",
        root/"ontology/occ_normative_ir.py",
        root/"ontology/occ_normative_ir_real_builder.py",
    ]
    init=root/"ontology/__init__.py"
    queue=seeds+([init] if init.is_file() else [])
    selected=set()

    def candidates(name: str):
        if not name or not name.startswith("ontology"):
            return []
        parts=name.split(".")
        if parts[0]!="ontology":
            return []
        base=root.joinpath(*parts)
        return [base.with_suffix(".py"),base/"__init__.py"]

    def package_for(path: Path) -> str:
        rel=path.relative_to(root).with_suffix("")
        parts=list(rel.parts)
        if parts and parts[-1]=="__init__":
            parts=parts[:-1]
        else:
            parts=parts[:-1]
        return ".".join(parts)

    while queue:
        p=queue.pop(0).resolve()
        try: rel=p.relative_to(root)
        except ValueError: continue
        if rel.as_posix() in selected or not p.is_file():
            continue
        selected.add(rel.as_posix())
        tree=ast.parse(p.read_text(encoding="utf-8"),filename=str(p))
        pkg=package_for(p)
        for node in ast.walk(tree):
            names=[]
            if isinstance(node,ast.Import):
                names=[a.name for a in node.names]
            elif isinstance(node,ast.ImportFrom):
                if node.level:
                    base=pkg.split(".") if pkg else []
                    keep=max(0,len(base)-node.level+1)
                    prefix=base[:keep]
                    if node.module: prefix+=node.module.split(".")
                    base_name=".".join(prefix)
                else:
                    base_name=node.module or ""
                if base_name:
                    names.append(base_name)
                    names.extend(base_name+"."+a.name for a in node.names)
            for name in names:
                for cand in candidates(name):
                    if cand.is_file(): queue.append(cand)
    result=[root/r for r in sorted(selected)]
    if not any(p.name=="normative_hierarchy.py" for p in result):
        raise RuntimeError("STATIC_IMPORT_CLOSURE_MISSING_NORMATIVE_HIERARCHY")
    if len(result)>80:
        raise RuntimeError("STATIC_IMPORT_CLOSURE_UNEXPECTEDLY_BROAD")
    return result

def _preclose_data_closure(root: Path) -> list[Path]:
    """Resolve verifier paths(root) statically; execute no OCE module."""
    import ast
    verifier_src=root/"ontology/occ_independent_constitutional_verifier.py"
    tree=ast.parse(verifier_src.read_text(encoding="utf-8"),filename=str(verifier_src))
    fn=next((n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="paths"),None)
    if fn is None: raise RuntimeError("VERIFIER_PATHS_FUNCTION_MISSING")
    env={"root":root}

    def ev(n):
        if isinstance(n,ast.Name):
            if n.id not in env: raise RuntimeError("VERIFIER_PATHS_UNKNOWN_NAME:"+n.id)
            return env[n.id]
        if isinstance(n,ast.Constant) and isinstance(n.value,str): return n.value
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=="Path" and len(n.args)==1:
            return Path(ev(n.args[0]))
        if isinstance(n,ast.BinOp) and isinstance(n.op,ast.Div):
            left,right=ev(n.left),ev(n.right)
            if isinstance(left,Path) and isinstance(right,str): return left/right
        if isinstance(n,ast.Dict): return {ev(k):ev(v) for k,v in zip(n.keys,n.values)}
        raise RuntimeError("VERIFIER_PATHS_UNSUPPORTED_AST:"+type(n).__name__)

    resolved=None
    for st in fn.body:
        if isinstance(st,ast.Assign) and len(st.targets)==1 and isinstance(st.targets[0],ast.Name):
            env[st.targets[0].id]=ev(st.value)
        elif isinstance(st,ast.Return): resolved=ev(st.value)
    if not isinstance(resolved,dict): raise RuntimeError("VERIFIER_PATHS_STATIC_RESOLUTION_FAILED")
    files=set()
    for key,p in resolved.items():
        if not isinstance(p,Path): raise RuntimeError("VERIFIER_PATH_NOT_PATH:"+str(key))
        try: p.resolve().relative_to(root.resolve())
        except ValueError: raise RuntimeError("VERIFIER_PATH_ESCAPES_ROOT:"+str(key))
        if p.is_file(): files.add(p.resolve())
        elif p.is_dir():
            for q in p.rglob("*"):
                if q.is_file() and "__pycache__" not in q.parts and q.name!=".DS_Store" and q.suffix!=".pyc":
                    files.add(q.resolve())
        else: raise RuntimeError("VERIFIER_DECLARED_INPUT_MISSING:"+str(key))
    if len(files)<9: raise RuntimeError("PRECLOSE_DATA_CLOSURE_UNEXPECTEDLY_SMALL")
    if len(files)>180: raise RuntimeError("PRECLOSE_DATA_CLOSURE_UNEXPECTEDLY_BROAD")
    return sorted(files,key=lambda p:p.relative_to(root).as_posix())

def _historical_builder(root: Path) -> Path:
    for p in (root/"ontology/occ_normative_ir_real_builder.py.bak",
              root/"ontology/occ_normative_ir_real_builder.py.bak8",
              root/"ontology/occ_normative_ir_real_builder.py.bak10"):
        if p.is_file() and _sha(p)==HISTORICAL_BUILDER_SHA:
            return p
    raise RuntimeError("HISTORICAL_BUILDER_FIXTURE_MISSING")

def _load_report(sandbox: Path):
    # Isolate imports so the report resolves ontology modules from the sandbox.
    old_path=list(sys.path)
    saved={k:v for k,v in sys.modules.items() if k=="ontology" or k.startswith("ontology.")}
    try:
        for k in list(saved): sys.modules.pop(k,None)
        sys.path.insert(0,str(sandbox))
        spec=importlib.util.spec_from_file_location(
            "ontology.occ_independent_constitutional_verification_report",
            sandbox/"ontology/occ_independent_constitutional_verification_report.py")
        if spec is None or spec.loader is None: raise RuntimeError("REPORT_IMPORT_SPEC_FAILED")
        mod=importlib.util.module_from_spec(spec)
        sys.modules[spec.name]=mod
        spec.loader.exec_module(mod)
        return mod
    finally:
        sys.path[:]=old_path
        for k in [k for k in list(sys.modules) if k=="ontology" or k.startswith("ontology.")]:
            sys.modules.pop(k,None)
        sys.modules.update(saved)

def run(root: Path) -> Dict[str,Any]:
    root=Path(root).resolve()
    hist_before=_sha(root/HIST_REL)
    anchor_before=_sha(root/ANCHOR_REL)
    verifier_before=_sha(root/"ontology/occ_independent_constitutional_verifier.py")
    result: Dict[str,Any]={
        "schema":SCHEMA,"scenario":"A075","functional_only":True,
        "phenomenology_undetermined":True,"defensive_validation_only":True,
        "temporary_fixture_only":True,"real_runtime_identity_modified":False,
        "historical_evidence_rewritten":False,"authorization_created":False,
        "execution_performed":False,"occ1h_closed":False,"occ1i_opened":False,
        "p159_final_lock":False,"p160_opened":False,
        "classification":"INCONCLUSIVE","reason":"EXPERIMENT_NOT_COMPLETED",
        "observations":{}
    }
    with tempfile.TemporaryDirectory(prefix="oce_a075_postcorr_") as td:
        sb=Path(td)
        closure=_local_ontology_closure(root)
        for src in closure:
            rel=src.relative_to(root)
            _copy(src,sb/rel)
        data_closure=_preclose_data_closure(root)
        for src in data_closure:
            rel=src.relative_to(root)
            _copy(src,sb/rel)
        _copy(root/ANCHOR_REL,sb/ANCHOR_REL)
        _copy(root/AUTHORITY_REL,sb/AUTHORITY_REL)
        # Deliberately substitute only the exact historical builder after
        # copying the current static import closure.
        _copy(_historical_builder(root),sb/"ontology/occ_normative_ir_real_builder.py")
        result["observations"]["sandbox_import_closure"]={
            "file_count":len(closure),
            "contains_normative_hierarchy":any(p.name=="normative_hierarchy.py" for p in closure),
            "module_execution_during_resolution":False,
        }
        result["observations"]["sandbox_preclose_data_closure"]={
            "file_count":len(data_closure),
            "contains_normative_occ1a":any("normative/occ1a/" in p.relative_to(root).as_posix() for p in data_closure),
            "module_execution_during_resolution":False,
        }

        r=_load_report(sb)
        anchor0=r._verify_verifier_identity_anchor(sb)
        if anchor0.get("status")!="VERIFIED_IDENTITY_ANCHOR":
            result["reason"]="BASELINE_IDENTITY_ANCHOR_NOT_VERIFIED"
        else:
            try:
                baseline=r.materialize_preclose_evidence(sb)
                baseline_check=r.verify_preclose_evidence(sb)
            except Exception as exc:
                result["reason"]="BASELINE_PRECLOSE_NOT_MATERIALIZABLE"
                result["observations"]["baseline_error"]=type(exc).__name__+":"+str(exc)
            else:
                result["observations"]["baseline"]={
                    "anchor":anchor0,"materialized_status":baseline.get("status"),
                    "verified_status":baseline_check.get("status")}
                if baseline_check.get("status")!="VERIFIED_PRECLOSE_BINDING":
                    result["reason"]="BASELINE_PRECLOSE_NOT_VERIFIED"
                else:
                    vp=sb/"ontology/occ_independent_constitutional_verifier.py"
                    original=vp.read_bytes()
                    vp.write_bytes(original+b"\n# controlled A075 post-correction identity drift fixture\n")
                    drift_sha=_sha(vp)
                    anchor_after_drift=r._verify_verifier_identity_anchor(sb)
                    pre=r.verify_preclose_evidence(sb)
                    rebind="NOT_ATTEMPTED"
                    rebind_error=None
                    try:
                        r.materialize_preclose_evidence(sb)
                        rebind="SUCCEEDED"
                    except Exception as exc:
                        rebind="REJECTED"
                        rebind_error=type(exc).__name__+":"+str(exc)
                    post=r.verify_preclose_evidence(sb)
                    anchor_file_unchanged=(_sha(sb/ANCHOR_REL)==anchor_before)
                    result["observations"]["measurement"]={
                        "authorized_verifier_sha256":AUTHORIZED_VERIFIER_SHA,
                        "drifted_verifier_sha256":drift_sha,
                        "anchor_after_drift":anchor_after_drift,
                        "pre":pre,"rebind_attempt":rebind,
                        "rebind_error":rebind_error,"post":post,
                        "anchor_file_unchanged":anchor_file_unchanged}
                    accepted_identity_rejection_reasons={
                        "VERIFIER_IDENTITY_ANCHOR_MISMATCH",
                        "VERIFIER_IDENTITY_NOT_INDEPENDENTLY_AUTHORIZED",
                    }
                    anchor_reason=anchor_after_drift.get("reason")
                    pre_reason=pre.get("reason")
                    post_reason=post.get("reason")
                    causal=(
                        anchor_after_drift.get("status")=="REJECTED"
                        and anchor_reason in accepted_identity_rejection_reasons
                        and pre.get("status")=="REJECTED"
                        and pre_reason==anchor_reason
                        and rebind=="REJECTED"
                        and rebind_error is not None
                        and ("OCC1F_VERIFIER_IDENTITY_NOT_AUTHORIZED:"+anchor_reason) in rebind_error
                        and post.get("status")=="REJECTED"
                        and post_reason==anchor_reason
                        and anchor_file_unchanged
                    )
                    if causal:
                        result["classification"]="RESISTED"
                        result["reason"]="UNAUTHORIZED_VERIFIER_IDENTITY_DRIFT_CANNOT_REBIND_PRECLOSE_TRUST"
                    elif rebind=="SUCCEEDED" and post.get("status")=="VERIFIED_PRECLOSE_BINDING":
                        result["classification"]="ASSURANCE_GAP"
                        result["reason"]="PRECLOSE_TRUST_STILL_REBINDABLE_AFTER_IDENTITY_DRIFT"
                    else:
                        result["reason"]="POST_CORRECTION_RESULT_NOT_CAUSALLY_DISCRIMINATED"

    if _sha(root/HIST_REL)!=hist_before:
        raise RuntimeError("HISTORICAL_EVIDENCE_CHANGED")
    if _sha(root/ANCHOR_REL)!=anchor_before:
        raise RuntimeError("REAL_ANCHOR_CHANGED")
    if _sha(root/"ontology/occ_independent_constitutional_verifier.py")!=verifier_before:
        raise RuntimeError("REAL_VERIFIER_CHANGED")
    result["evidence_sha256"]=_canonical_hash(result)
    return result
