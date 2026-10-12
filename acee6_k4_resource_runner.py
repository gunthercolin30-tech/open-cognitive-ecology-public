from __future__ import annotations

import argparse
import gc
import json
import resource
import tempfile
import time
import tracemalloc
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from acee6_k4_resource_support import (
    EVIDENCE_DIR, INVARIANTS, ROOT, SCHEMA_VERSION, TARGET,
    atomic_json_write, child_pids, stable_child_pids, fd_count, file_sha, linear_slope,
    load_executor, load_thresholds, rss_bytes, scenario_inputs, sha,
)

def run_campaign(*, warmup: int = 5, cycles: int = 64, persist: bool = False) -> dict[str, Any]:
    if warmup < 0 or cycles < 2 or cycles > 500:
        raise ValueError("invalid_campaign_size")
    source_before = file_sha(TARGET)
    thresholds = load_thresholds()
    fd_before = fd_count()
    children_before = stable_child_pids()
    rss_before = rss_bytes()
    ru_before = resource.getrusage(resource.RUSAGE_SELF)
    exceptions = []
    durations = []
    memory_samples = []
    fd_samples = []
    rss_samples = []
    statuses: dict[str, int] = {}

    with tempfile.TemporaryDirectory(prefix="acee6_k4_") as temp_name:
        campaign_parent = Path(temp_name)
        root = campaign_parent / "sandbox"
        (root / "ontology").mkdir(parents=True, exist_ok=True)
        executor_cls = load_executor(TARGET, "_acee6_k4_executor")
        executor = executor_cls(root=root, now_utc=datetime(2026, 1, 1, tzinfo=timezone.utc))

        for index in range(warmup):
            try:
                executor.step(inputs=scenario_inputs(index), persist=False)
            except Exception as exc:
                exceptions.append(f"warmup:{type(exc).__name__}:{exc}")
        gc.collect()
        tracemalloc.start()
        for index in range(cycles):
            started = time.perf_counter_ns()
            try:
                result = executor.step(inputs=scenario_inputs(index + warmup), persist=False)
                status = str(result.get("status") or result.get("transaction_state") or "UNCLASSIFIED") if isinstance(result, Mapping) else type(result).__name__
                statuses[status] = statuses.get(status, 0) + 1
            except Exception as exc:
                exceptions.append(f"cycle:{index}:{type(exc).__name__}:{exc}")
            durations.append(time.perf_counter_ns() - started)
            gc.collect()
            current, _peak = tracemalloc.get_traced_memory()
            memory_samples.append(current)
            fd_value = fd_count()
            if fd_value is not None:
                fd_samples.append(fd_value)
            rss_value = rss_bytes()
            if rss_value is not None:
                rss_samples.append(rss_value)
        current_memory, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        gc.collect()
        residues = sorted(
            str(path.relative_to(campaign_parent))
            for path in campaign_parent.rglob("*")
            if path != root and path.exists()
        )
        # The sandbox directory itself is expected; contents are not.
        sandbox_residues = sorted(str(path.relative_to(root)) for path in root.rglob("*") if path.is_file() or path.is_symlink())

    fd_after = fd_count()
    children_after = stable_child_pids()
    rss_after = rss_bytes()
    ru_after = resource.getrusage(resource.RUSAGE_SELF)
    source_after = file_sha(TARGET)
    fd_delta = None if fd_before is None or fd_after is None else fd_after - fd_before
    child_delta = len(set(children_after) - set(children_before))
    memory_slope = linear_slope(memory_samples)
    fd_slope = linear_slope(fd_samples)
    rss_slope = linear_slope(rss_samples)
    median_ns = int(sorted(durations)[len(durations) // 2]) if durations else 0
    p95_ns = int(sorted(durations)[min(len(durations)-1, int(len(durations)*0.95))]) if durations else 0
    checks = {
        "target_immutable": source_before == source_after,
        "memory_slope_within_limit": memory_slope <= float(thresholds["memory_growth_bytes_per_cycle_max"]),
        "tracemalloc_peak_within_limit": peak_memory <= int(thresholds["tracemalloc_peak_bytes_max"]),
        "fd_delta_within_limit": fd_delta is None or fd_delta <= int(thresholds["fd_delta_max"]),
        "fd_slope_within_limit": not fd_samples or fd_slope <= float(thresholds["fd_growth_per_cycle_max"]),
        "no_child_process_leak": child_delta <= int(thresholds["child_process_delta_max"]),
        "no_temporary_residue": len(sandbox_residues) <= int(thresholds["temporary_residue_count_max"]),
        "no_unhandled_exception": len(exceptions) <= int(thresholds["unhandled_exception_count_max"]),
    }
    payload = {
        "primitive": "ACEE6_K_RESOURCE_METROLOGY",
        "stage": "ACEE6-K4",
        "public_schema_version": SCHEMA_VERSION,
        "status": "ACEE6_K4_RESOURCE_CAMPAIGN_COMPLETE",
        "warmup_cycles": warmup,
        "measured_cycles": cycles,
        "target_sha256": source_before,
        "thresholds": thresholds,
        "metrics": {
            "duration_median_ns": median_ns,
            "duration_p95_ns": p95_ns,
            "duration_total_ns": sum(durations),
            "memory_growth_bytes_per_cycle": memory_slope,
            "tracemalloc_current_bytes": current_memory,
            "tracemalloc_peak_bytes": peak_memory,
            "fd_before": fd_before,
            "fd_after": fd_after,
            "fd_delta": fd_delta,
            "fd_growth_per_cycle": fd_slope,
            "rss_before_bytes": rss_before,
            "rss_after_bytes": rss_after,
            "rss_growth_bytes_per_cycle_diagnostic": rss_slope,
            "ru_utime_delta": ru_after.ru_utime - ru_before.ru_utime,
            "ru_stime_delta": ru_after.ru_stime - ru_before.ru_stime,
            "child_process_delta": child_delta,
            "temporary_residue_count": len(sandbox_residues),
            "temporary_residues": sandbox_residues,
            "unhandled_exception_count": len(exceptions),
            "status_counts": dict(sorted(statuses.items())),
        },
        "checks": checks,
        "exceptions": exceptions,
        "real_root_mutation_count": 0 if source_before == source_after else 1,
        "invariants": dict(INVARIANTS),
        "limitations": [
            "rss_is_diagnostic_only_on_macos",
            "tracemalloc_slope_is_primary_memory_leak_indicator",
            "resource_campaign_uses_persist_false_and_temporary_root",
        ],
    }
    campaign_payload = dict(payload)
    campaign_payload.pop("metrics", None)
    campaign_payload["metric_projection"] = {
        "memory_growth_bytes_per_cycle": round(memory_slope, 6),
        "fd_delta": fd_delta,
        "fd_growth_per_cycle": round(fd_slope, 6),
        "child_process_delta": child_delta,
        "temporary_residue_count": len(sandbox_residues),
        "unhandled_exception_count": len(exceptions),
    }
    payload["campaign_hash"] = sha(campaign_payload)
    payload["report_hash"] = sha(payload)
    verification = verify_report(payload)
    report_path = None
    if persist:
        report_path = EVIDENCE_DIR / "acee6_k4_resource_report.json"
        atomic_json_write(report_path, payload)
    return {"report": payload, "verification": verification, "report_path": str(report_path) if report_path else None}

def verify_report(report: Mapping[str, Any]) -> dict[str, Any]:
    reasons = []
    payload = dict(report)
    expected = payload.pop("report_hash", None)
    if expected != sha(payload): reasons.append("report_hash_invalid")
    if report.get("invariants") != INVARIANTS: reasons.append("epistemic_invariants_invalid")
    checks = report.get("checks")
    if not isinstance(checks, Mapping) or not all(value is True for value in checks.values()): reasons.append("resource_checks_failed")
    if report.get("real_root_mutation_count") != 0: reasons.append("real_root_mutated")
    metrics = report.get("metrics")
    if not isinstance(metrics, Mapping): reasons.append("metrics_missing")
    return {"valid": not reasons, "reasons": reasons}

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--warmup", type=int, default=5)
    parser.add_argument("--cycles", type=int, default=64)
    parser.add_argument("--persist", action="store_true")
    args = parser.parse_args()
    result = run_campaign(warmup=args.warmup, cycles=args.cycles, persist=args.persist)
    print(json.dumps(result, indent=2, sort_keys=True))
    print("ACEE6_K4_RESOURCE_RUNNER_READY")
    raise SystemExit(0 if result["verification"]["valid"] else 1)
if __name__ == "__main__": main()
