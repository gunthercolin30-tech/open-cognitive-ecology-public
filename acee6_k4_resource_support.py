from __future__ import annotations

import gc
import hashlib
import importlib.util
import json
import os
import resource
import statistics
import subprocess
import sys
import tempfile
import time
import tracemalloc
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path.home() / "open-cognitive-ecology"
TARGET = ROOT / "ontology" / "acee_installation_executor.py"
EVIDENCE_DIR = ROOT / "acee6_k_evidence"
SCHEMA_VERSION = "1.0.0"
INVARIANTS = {
    "consciousness_proven": False,
    "subjectivity_proven": False,
    "qualia_proven": False,
    "phenomenology_proven": False,
    "functional_conclusion_only": True,
    "phenomenology_undetermined": True,
}
DEFAULT_THRESHOLDS = {
    "fd_growth_per_cycle_max": 0.0,
    "fd_delta_max": 2,
    "memory_growth_bytes_per_cycle_max": 4096.0,
    "tracemalloc_peak_bytes_max": 33554432,
    "child_process_delta_max": 0,
    "temporary_residue_count_max": 0,
    "unhandled_exception_count_max": 0,
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

def fd_count() -> int | None:
    for candidate in (Path("/dev/fd"), Path("/proc/self/fd")):
        try:
            return len(list(candidate.iterdir()))
        except OSError:
            continue
    return None

def child_pids() -> list[int]:
    try:
        completed = subprocess.run(
            ["ps", "-axo", "pid=,ppid="],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
            shell=False,
        )
    except Exception:
        return []
    own = os.getpid()
    children = []
    for line in completed.stdout.splitlines():
        fields = line.split()
        if len(fields) != 2:
            continue
        try:
            pid, ppid = map(int, fields)
        except ValueError:
            continue
        if ppid == own:
            children.append(pid)
    return sorted(children)

def stable_child_pids() -> list[int]:
    first = set(child_pids())
    time.sleep(0.05)
    second = set(child_pids())
    return sorted(first & second)

def rss_bytes() -> int | None:
    try:
        completed = subprocess.run(
            ["ps", "-o", "rss=", "-p", str(os.getpid())],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
            shell=False,
        )
        return int(completed.stdout.strip()) * 1024
    except Exception:
        return None

def linear_slope(values: Sequence[int | float]) -> float:
    n = len(values)
    if n < 2:
        return 0.0
    x_mean = (n - 1) / 2.0
    y_mean = sum(float(v) for v in values) / n
    numerator = sum((i - x_mean) * (float(v) - y_mean) for i, v in enumerate(values))
    denominator = sum((i - x_mean) ** 2 for i in range(n))
    return numerator / denominator if denominator else 0.0

def load_executor(module_path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("executor_spec_unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(module_name, None)
    return module.AceeInstallationExecutor

def load_thresholds() -> dict[str, Any]:
    thresholds = dict(DEFAULT_THRESHOLDS)
    path = EVIDENCE_DIR / "acee6_k0_baseline_report.json"
    if path.is_file():
        try:
            report = json.loads(path.read_text(encoding="utf-8"))
            supplied = report.get("thresholds")
            if isinstance(supplied, Mapping):
                for key in thresholds:
                    if key in supplied and isinstance(supplied[key], (int, float)):
                        thresholds[key] = supplied[key]
        except Exception:
            pass
    return thresholds

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
    except Exception:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise

def scenario_inputs(index: int) -> Any:
    scenarios = (
        None,
        {},
        {"unexpected": index},
        {"acee5_decision": {}},
        {"acee5_decision": {"result_hash": "0" * 64}},
        {"admission_context": {"requested_stage": "UNKNOWN", "transaction_id": f"k4-{index}"}},
        {"target_path": "../outside.py"},
        {"target_path": "/tmp/outside.py"},
    )
    return scenarios[index % len(scenarios)]
