from __future__ import annotations

import ast
import hashlib
import importlib
import json
import os
import platform
import resource
import sys
import tempfile
import time
import tracemalloc
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

ROOT = Path.home() / "open-cognitive-ecology"
MODULE_PATH = ROOT / "ontology" / "acee_installation_executor.py"
EVIDENCE_DIR = ROOT / "acee6_k_evidence"
SCHEMA_VERSION = "1.0.0"

CAMPAIGNS = (
    {"id": "K0", "name": "contract_and_baseline", "heavy": False},
    {"id": "K1", "name": "property_testing", "heavy": True},
    {"id": "K2", "name": "deterministic_fuzzing", "heavy": True},
    {"id": "K3", "name": "quantified_mutation_testing", "heavy": True},
    {"id": "K4", "name": "performance_memory_fd", "heavy": True},
    {"id": "K5", "name": "100_transactions", "heavy": True},
    {"id": "K6", "name": "1000_transactions", "heavy": True},
    {"id": "K7", "name": "longitudinal_drift", "heavy": True},
    {"id": "K8", "name": "global_certification", "heavy": True},
)

INVARIANTS = {
    "consciousness_proven": False,
    "subjectivity_proven": False,
    "qualia_proven": False,
    "phenomenology_proven": False,
    "functional_conclusion_only": True,
    "phenomenology_undetermined": True,
}


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def sha(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def discover_executor_class(module_path: Path = MODULE_PATH) -> str:
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    candidates = []
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        methods = {item.name for item in node.body if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))}
        if "step" in methods and "installation" in node.name.casefold() and "executor" in node.name.casefold():
            candidates.append(node.name)
    if len(candidates) != 1:
        raise RuntimeError(f"executor_class_discovery_failed:{candidates}")
    return candidates[0]


def fd_count() -> int | None:
    for candidate in (Path("/dev/fd"), Path("/proc/self/fd")):
        try:
            return len(list(candidate.iterdir()))
        except OSError:
            continue
    return None


def corrected_runtime_baseline(root: Path = ROOT) -> dict[str, Any]:
    module_path = root / "ontology" / "acee_installation_executor.py"
    class_name = discover_executor_class(module_path)
    before_fd = fd_count()
    before_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    tracemalloc.start()
    started = time.perf_counter()
    module = importlib.import_module("ontology.acee_installation_executor")
    elapsed = time.perf_counter() - started
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    cls = getattr(module, class_name)
    instance = cls(root=root)
    result = {
        "executor_class": class_name,
        "instance_type": type(instance).__name__,
        "module_file": str(Path(module.__file__).resolve()),
        "module_sha256": file_sha(module_path),
        "import_seconds": elapsed,
        "tracemalloc_current_bytes": current,
        "tracemalloc_peak_bytes": peak,
        "rss_before_ru_maxrss": before_rss,
        "rss_after_ru_maxrss": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "fd_before": before_fd,
        "fd_after": fd_count(),
        "python_version": sys.version,
        "platform": platform.platform(),
    }
    return result


def thresholds_from_baseline(baseline: Mapping[str, Any]) -> dict[str, Any]:
    import_seconds = max(float(baseline.get("import_seconds") or 0.001), 0.001)
    peak = max(int(baseline.get("tracemalloc_peak_bytes") or 1), 1)
    fd_before = baseline.get("fd_before")
    fd_after = baseline.get("fd_after")
    fd_delta = 0 if fd_before is None or fd_after is None else max(0, int(fd_after) - int(fd_before))
    return {
        "import_seconds_max": max(1.0, import_seconds * 5.0),
        "tracemalloc_peak_bytes_max": max(32 * 1024 * 1024, peak * 4),
        "fd_delta_max": max(2, fd_delta + 1),
        "mutation_score_min": 0.95,
        "transaction_success_rate_min": 1.0,
        "hash_drift_allowed": 0,
        "decision_drift_allowed": 0,
        "memory_growth_bytes_per_cycle_max": 4096,
        "fd_growth_per_cycle_max": 0,
    }


def build_contract(root: Path = ROOT) -> dict[str, Any]:
    module_path = root / "ontology" / "acee_installation_executor.py"
    class_name = discover_executor_class(module_path)
    payload = {
        "primitive": "ACEE6_K_CERTIFICATION_FRAMEWORK",
        "stage": "ACEE6-K0",
        "public_schema_version": SCHEMA_VERSION,
        "status": "ACEE6_K0_CONTRACT_READY",
        "executor_class": class_name,
        "executor_module_sha256": file_sha(module_path),
        "campaigns": list(CAMPAIGNS),
        "failure_policy": {
            "before_mutation": "REJECT",
            "after_mutation": "ROLLBACK",
            "rollback_failed": "QUARANTINE",
            "impossible_state": "STATE_CORRUPTED_THEN_QUARANTINE",
            "partial_success_allowed": False,
        },
        "retry_policy": {
            "unlimited_retry_allowed": False,
            "semantic_failure_retry_allowed": False,
            "constitutional_veto_retry_allowed": False,
            "automatic_repair_retry_allowed": False,
            "allowed_families": ["transient_infrastructure", "external_proof_revalidation"],
            "strict_budget_required": True,
        },
        "invariants": dict(INVARIANTS),
        "heavy_campaigns_default_enabled": False,
    }
    payload["contract_hash"] = sha(payload)
    return payload


def build_k0_report(root: Path = ROOT) -> dict[str, Any]:
    baseline = corrected_runtime_baseline(root)
    contract = build_contract(root)
    payload = {
        "primitive": "ACEE6_K_CERTIFICATION_FRAMEWORK",
        "stage": "ACEE6-K0",
        "public_schema_version": SCHEMA_VERSION,
        "status": "ACEE6_K0_BASELINE_READY",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "contract": contract,
        "baseline": baseline,
        "thresholds": thresholds_from_baseline(baseline),
        "campaign_status": {item["id"]: ("READY" if item["id"] == "K0" else "NOT_RUN") for item in CAMPAIGNS},
        "heavy_campaigns_executed": False,
        "invariants": dict(INVARIANTS),
    }
    payload["report_hash"] = sha(payload)
    return payload


def verify_report(report: Mapping[str, Any]) -> dict[str, Any]:
    reasons = []
    payload = dict(report)
    expected = payload.pop("report_hash", None)
    if expected != sha(payload):
        reasons.append("report_hash_invalid")
    contract = report.get("contract")
    if not isinstance(contract, Mapping):
        reasons.append("contract_missing")
    else:
        cp = dict(contract)
        ch = cp.pop("contract_hash", None)
        if ch != sha(cp):
            reasons.append("contract_hash_invalid")
    if report.get("invariants") != INVARIANTS:
        reasons.append("epistemic_invariants_invalid")
    if report.get("heavy_campaigns_executed") is not False:
        reasons.append("heavy_campaign_execution_unexpected")
    return {"valid": not reasons, "reasons": reasons}


def atomic_json_write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
        directory_fd = os.open(str(path.parent), os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass


def run_orchestrator(*, root: Path = ROOT, persist: bool = False, run_heavy: bool = False) -> dict[str, Any]:
    if run_heavy:
        raise ValueError("heavy_campaigns_require_explicit_future_campaign_scripts")
    report = build_k0_report(root)
    verification = verify_report(report)
    result = {
        "status": "ACEE6_K0_ORCHESTRATOR_READY",
        "dry_run": not persist,
        "persistence_performed": False,
        "report": report,
        "verification": verification,
        "report_path": None,
    }
    if persist:
        path = root / "acee6_k_evidence" / "acee6_k0_baseline_report.json"
        atomic_json_write(path, report)
        result["persistence_performed"] = True
        result["report_path"] = str(path)
    return result
