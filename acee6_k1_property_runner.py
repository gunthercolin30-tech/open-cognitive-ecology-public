from __future__ import annotations
import argparse, ast, json, os, tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from acee6_k1_property_domains import DEFAULT_SEED, SCHEMA_VERSION, structured_cases
from acee6_k1_property_oracles import INVARIANTS, evaluate_case, sha, verify_case

ROOT = Path.home() / "open-cognitive-ecology"
EVIDENCE_DIR = ROOT / "acee6_k_evidence"
MODULE_PATH = ROOT / "ontology" / "acee_installation_executor.py"


def module_sha(path: Path = MODULE_PATH) -> str:
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


def discover_executor(path: Path = MODULE_PATH) -> str:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found=[]
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            methods={x.name for x in node.body if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef))}
            if "step" in methods and "installation" in node.name.casefold() and "executor" in node.name.casefold():
                found.append(node.name)
    if len(found)!=1:
        raise RuntimeError(f"executor_discovery_failed:{found}")
    return found[0]


def minimize_counterexample(case: Mapping[str, Any], failing) -> dict[str, Any]:
    current=dict(case)
    for key in sorted(list(current)):
        trial=dict(current); trial.pop(key, None)
        try:
            still=bool(failing(trial))
        except Exception:
            still=True
        if still:
            current=trial
    return current


def build_report(seed: int = DEFAULT_SEED, limit: int = 256) -> dict[str, Any]:
    cases=structured_cases(seed=seed, limit=limit)
    records=[]; failures=[]
    for index, case in enumerate(cases):
        result=evaluate_case(case)
        reasons=verify_case(case,result)
        record={"index":index,"case_hash":sha(case),"result_hash":sha(result),"reasons":reasons}
        records.append(record)
        if reasons:
            failures.append({"case":case,"reasons":reasons})
    deterministic_payload={"seed":seed,"limit":limit,"records":records}
    report={
        "primitive":"ACEE6_K_PROPERTY_TESTING",
        "stage":"ACEE6-K1",
        "public_schema_version":SCHEMA_VERSION,
        "status":"ACEE6_K1_PROPERTY_TESTING_COMPLETE" if not failures else "ACEE6_K1_PROPERTY_TESTING_FAILED",
        "seed":seed,
        "case_count":len(cases),
        "property_count":4,
        "failure_count":len(failures),
        "failures":failures,
        "campaign_hash":sha(deterministic_payload),
        "executor_class":discover_executor(),
        "executor_module_sha256":module_sha(),
        "invariants":dict(INVARIANTS),
        "timestamp_utc":datetime.now(timezone.utc).isoformat(),
    }
    report["report_hash"]=sha(report)
    return report


def verify_report(report: Mapping[str, Any]) -> dict[str, Any]:
    reasons=[]; payload=dict(report); expected=payload.pop("report_hash",None)
    if expected!=sha(payload): reasons.append("report_hash_invalid")
    if report.get("invariants")!=INVARIANTS: reasons.append("epistemic_invariants_invalid")
    if int(report.get("failure_count",-1))!=0: reasons.append("property_failures_present")
    return {"valid":not reasons,"reasons":reasons}


def atomic_write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,temp=tempfile.mkstemp(prefix=f".{path.name}.",suffix=".tmp",dir=str(path.parent))
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as stream:
            json.dump(payload,stream,indent=2,sort_keys=True,ensure_ascii=False); stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(temp,path)
    finally:
        if os.path.exists(temp): os.unlink(temp)


def run(seed: int = DEFAULT_SEED, limit: int = 256, persist: bool = False) -> dict[str, Any]:
    report=build_report(seed,limit); verification=verify_report(report); path=None
    if persist:
        path=EVIDENCE_DIR / "acee6_k1_property_report.json"; atomic_write(path,report)
    return {"status":"ACEE6_K1_RUNNER_READY","report":report,"verification":verification,"persistence_performed":persist,"report_path":None if path is None else str(path)}

if __name__=="__main__":
    parser=argparse.ArgumentParser(); parser.add_argument("--seed",type=int,default=DEFAULT_SEED); parser.add_argument("--limit",type=int,default=256); parser.add_argument("--persist",action="store_true")
    args=parser.parse_args(); result=run(args.seed,args.limit,args.persist); print(json.dumps(result,indent=2,sort_keys=True)); print(result["status"])
