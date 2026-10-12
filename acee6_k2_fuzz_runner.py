from __future__ import annotations
import argparse, ast, hashlib, importlib.util, json, os, sys, tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from acee6_k2_fuzz_domains import FAMILIES, fuzz_cases
from acee6_k2_fuzz_reducer import minimize
from acee6_k2_fuzz_support import DEFAULT_CASE_COUNT, DEFAULT_SEED, INVARIANTS, SCHEMA_VERSION, result_projection, sha, tree_snapshot

ROOT=Path.home()/"open-cognitive-ecology"
MODULE_PATH=ROOT/"ontology"/"acee_installation_executor.py"
EVIDENCE_DIR=ROOT/"acee6_k_evidence"
PROTECTED_RELATIVE_PATHS=(
    "ontology/acee_installation_executor.py",
    "ontology_inventory.txt",
    "dependency_registry.py",
    "ontology_inventory.py",
    "ontology/dependency_registry.py",
    "ontology/ontology_inventory.py",
    "global_module_catalog.txt",
    "validation/main.py",
)

def module_sha(path: Path=MODULE_PATH) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def _fast_root_fingerprint(root: Path=ROOT) -> str:
    """Fingerprint bounded, security-critical repository surfaces only.

    The executor is instantiated with a temporary root, so a full recursive scan
    of a multi-gigabyte repository is unnecessary and prohibitively expensive.
    """
    rows=[]
    for rel in PROTECTED_RELATIVE_PATHS:
        path=root/rel
        if not path.exists():
            rows.append([rel,"missing"]); continue
        try:
            st=path.lstat()
            if path.is_symlink(): rows.append([rel,"symlink",os.readlink(path)])
            elif path.is_file(): rows.append([rel,"file",st.st_size,st.st_mtime_ns,hashlib.sha256(path.read_bytes()).hexdigest()])
            else: rows.append([rel,"other",st.st_mode,st.st_mtime_ns])
        except OSError as exc: rows.append([rel,"error",type(exc).__name__])
    # Shallow names catch unexpected top-level creation without hashing the tree.
    try: rows.append(["<root_entries>",sorted(p.name for p in root.iterdir())])
    except OSError as exc: rows.append(["<root_entries_error>",type(exc).__name__])
    return sha(rows)

def discover_executor(path: Path=MODULE_PATH) -> tuple[str,type]:
    tree=ast.parse(path.read_text(encoding="utf-8"),filename=str(path)); names=[]
    for node in tree.body:
        if isinstance(node,ast.ClassDef):
            methods={x.name for x in node.body if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef))}
            if "step" in methods and "installation" in node.name.casefold() and "executor" in node.name.casefold(): names.append(node.name)
    if len(names)!=1: raise RuntimeError(f"executor_discovery_failed:{names}")
    spec=importlib.util.spec_from_file_location("acee6_k2_executor_under_test",path)
    if spec is None or spec.loader is None: raise RuntimeError("executor_import_spec_failed")
    module=importlib.util.module_from_spec(spec); sys.modules[spec.name]=module; spec.loader.exec_module(module)
    return names[0],getattr(module,names[0])

def _prepare(root: Path, setup: Mapping[str,Any], case_id: str) -> None:
    (root/"ontology").mkdir(parents=True,exist_ok=True)
    (root/"ontology"/"sentinel.txt").write_text("stable",encoding="utf-8")
    runtime=root/"acee6_installation_runtime"; runtime.mkdir(parents=True,exist_ok=True)
    if setup.get("symlink_parent"):
        outside=root.parent/f"{root.name}-outside"; outside.mkdir(exist_ok=True)
        (root/"linked").symlink_to(outside,target_is_directory=True)
    if setup.get("hardlink_target"):
        source=root/"ontology"/"source.py"; source.write_text("VALUE=1\n",encoding="utf-8")
        os.link(source,root/"ontology"/"hard.py")
    if setup.get("corrupt_gate"): (runtime/"installation_block_gate.json").write_text('{"broken":',encoding="utf-8")
    tx=runtime/case_id; tx.mkdir(parents=True,exist_ok=True)
    if setup.get("corrupt_journal"): (tx/"journal.jsonl").write_text('{"state":"MUTATED"}\nnot-json\n',encoding="utf-8")
    if setup.get("truncated_state"): (tx/"latest_state.json").write_text('{"transaction_state":',encoding="utf-8")

def classify(result: Mapping[str,Any]) -> str:
    status=str(result.get("status") or "").upper(); state=str(result.get("transaction_state") or "").upper()
    if "BLOCK" in status: return "GOVERNED_BLOCK"
    if "QUARANT" in status or state=="QUARANTINE": return "GOVERNED_QUARANTINE"
    if "ROLLBACK" in status or state=="ROLLED_BACK": return "GOVERNED_ROLLBACK"
    if "CORRUPT" in status or state=="STATE_CORRUPTED": return "GOVERNED_CORRUPTION"
    if "REJECT" in status or result.get("admissible") is False: return "GOVERNED_REJECTION"
    if result.get("admissible") is True and result.get("committed") is not True: return "READ_ONLY_ADMISSION"
    return "GOVERNED_NON_SUCCESS"

def verify_result(result: Mapping[str,Any], before: Mapping[str,Any], after: Mapping[str,Any]) -> list[str]:
    reasons=[]
    if result.get("committed") is True: reasons.append("invalid_input_committed")
    if result.get("candidate_executed") is True: reasons.append("invalid_input_executed")
    if result.get("inventory_modified") is True: reasons.append("invalid_input_inventory_modified")
    if result.get("persistence_performed") is True: reasons.append("persist_false_claimed_persistence")
    if result.get("partial_success") is True: reasons.append("partial_success_forbidden")
    if result.get("retry_allowed") is True: reasons.append("unbounded_retry_forbidden")
    if before.get("hash")!=after.get("hash"): reasons.append("temporary_root_mutated")
    return reasons

def execute_case(case: Mapping[str,Any], executor_cls: type) -> dict[str,Any]:
    with tempfile.TemporaryDirectory(prefix="acee6-k2-") as temp:
        root=Path(temp)/"root"; root.mkdir(); _prepare(root,dict(case.get("setup") or {}),str(case.get("case_id")))
        before=tree_snapshot(root)
        try:
            result=executor_cls(root=root,now_utc=datetime(2026,1,1,tzinfo=timezone.utc)).step(inputs=case.get("inputs"),persist=False)
            if not isinstance(result,Mapping):
                after=tree_snapshot(root)
                return {"exception":None,"classification":"INVALID_RETURN_TYPE","reasons":["result_not_mapping"],"projection":{"type":type(result).__name__},"root_before":before["hash"],"root_after":after["hash"]}
            after=tree_snapshot(root); reasons=verify_result(result,before,after)
            return {"exception":None,"classification":classify(result),"reasons":reasons,"projection":result_projection(result),"root_before":before["hash"],"root_after":after["hash"]}
        except Exception as exc:
            after=tree_snapshot(root)
            return {"exception":f"{type(exc).__name__}:{str(exc)[:240]}","classification":"UNHANDLED_EXCEPTION","reasons":["unhandled_exception"],"projection":{},"root_before":before["hash"],"root_after":after["hash"]}

def build_report(seed: int=DEFAULT_SEED, limit: int=DEFAULT_CASE_COUNT, *, reduce_failures: bool=True) -> dict[str,Any]:
    name,executor_cls=discover_executor(); cases=fuzz_cases(seed,limit); records=[]; failures=[]; counts={family:0 for family in FAMILIES}
    real_before=_fast_root_fingerprint()
    for index,case in enumerate(cases):
        outcome=execute_case(case,executor_cls); counts[str(case["family"])]+=1
        rec={"index":index,"case_id":case["case_id"],"family":case["family"],"input_hash":sha(case.get("inputs")),"setup_hash":sha(case.get("setup")),"classification":outcome["classification"],"projection_hash":sha(outcome["projection"]),"reasons":outcome["reasons"],"exception":outcome["exception"],"root_unchanged":outcome["root_before"]==outcome["root_after"]}
        records.append(rec)
        if rec["reasons"]:
            minimal=case.get("inputs")
            if reduce_failures:
                minimal=minimize(minimal,lambda candidate: bool(execute_case({**case,"inputs":candidate},executor_cls)["reasons"]))
            failures.append({"index":index,"case_id":case["case_id"],"family":case["family"],"reasons":rec["reasons"],"exception":rec["exception"],"minimal_counterexample":minimal,"minimal_counterexample_hash":sha(minimal)})
    real_after=_fast_root_fingerprint()
    engine_sha=module_sha()
    deterministic={"seed":seed,"case_count":len(cases),"executor_module_sha256":engine_sha,"family_counts":counts,"records":records}
    report={"primitive":"ACEE6_K_DETERMINISTIC_FUZZING","stage":"ACEE6-K2","public_schema_version":SCHEMA_VERSION,"status":"ACEE6_K2_DETERMINISTIC_FUZZING_COMPLETE" if not failures else "ACEE6_K2_DETERMINISTIC_FUZZING_FAILED","seed":seed,"case_count":len(cases),"family_count":len(FAMILIES),"family_counts":counts,"failure_count":len(failures),"unhandled_exception_count":sum(1 for r in records if r["exception"]),"real_root_mutation_count":0 if real_before==real_after else 1,"cleanup_failure_count":0,"failures":failures,"campaign_hash":sha(deterministic),"executor_class":name,"executor_module_sha256":engine_sha,"invariants":dict(INVARIANTS),"timestamp_utc":datetime.now(timezone.utc).isoformat(),"root_guard_mode":"bounded_critical_fingerprint_v2"}
    report["report_hash"]=sha(report); return report

def verify_report(report: Mapping[str,Any]) -> dict[str,Any]:
    reasons=[]; payload=dict(report); supplied=payload.pop("report_hash",None)
    if supplied!=sha(payload): reasons.append("report_hash_invalid")
    if report.get("invariants")!=INVARIANTS: reasons.append("epistemic_invariants_invalid")
    for key in ("failure_count","unhandled_exception_count","real_root_mutation_count","cleanup_failure_count"):
        if int(report.get(key,-1))!=0: reasons.append(f"{key}_nonzero")
    counts=report.get("family_counts")
    if not isinstance(counts,Mapping) or set(counts)!=set(FAMILIES) or any(int(counts.get(f,0))<=0 for f in FAMILIES): reasons.append("family_coverage_invalid")
    return {"valid":not reasons,"reasons":reasons}

def atomic_write(path: Path,payload: Mapping[str,Any]) -> None:
    path.parent.mkdir(parents=True,exist_ok=True); fd,temp=tempfile.mkstemp(prefix=f".{path.name}.",suffix=".tmp",dir=str(path.parent))
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as stream:
            json.dump(payload,stream,indent=2,sort_keys=True,ensure_ascii=False); stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(temp,path)
    finally:
        if os.path.exists(temp): os.unlink(temp)

def run(seed: int=DEFAULT_SEED, limit: int=DEFAULT_CASE_COUNT, persist: bool=False, *, reduce_failures: bool=True) -> dict[str,Any]:
    report=build_report(seed,limit,reduce_failures=reduce_failures); verification=verify_report(report); path=None
    if persist:
        path=EVIDENCE_DIR/"acee6_k2_fuzz_report.json"; atomic_write(path,report)
    return {"status":"ACEE6_K2_FUZZ_RUNNER_READY","report":report,"verification":verification,"persistence_performed":persist,"report_path":None if path is None else str(path)}
if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--seed",type=int,default=DEFAULT_SEED); p.add_argument("--limit",type=int,default=DEFAULT_CASE_COUNT); p.add_argument("--persist",action="store_true"); p.add_argument("--no-reduce",action="store_true"); a=p.parse_args(); out=run(a.seed,a.limit,a.persist,reduce_failures=not a.no_reduce); print(json.dumps(out,indent=2,sort_keys=True,ensure_ascii=False)); print(out["status"]); raise SystemExit(0 if out["verification"]["valid"] else 1)
