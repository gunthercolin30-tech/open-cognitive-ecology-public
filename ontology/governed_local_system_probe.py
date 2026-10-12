from __future__ import annotations
import os
import shutil
from pathlib import Path
from types import SimpleNamespace
from ontology.governed_process_effector import GovernedProcessEffector, ProcessEffectRequest

ADAPTER_ID = "p162g65c10a.local-system-probe"
_ALLOWED = {
    "pagesize": [()],
    "vm_stat": [()],
    "pmset": [("-g", "therm"), ("-g", "batt")],
    "sysctl": [("-n", "kern.boottime")],
    "system_profiler": [("SPCameraDataType",), ("SPAudioDataType",), ("SPUSBDataType",)],
    "lsusb": [()],
    "launchctl": [("list",)],
}
_TIMEOUTS = {
    "pagesize": 2.0, "vm_stat": 2.0, "pmset": 2.0, "sysctl": 2.0,
    "system_profiler": 4.0, "lsusb": 2.0, "launchctl": 10.0,
}

def _minimal_env():
    return {k: v for k in ("PATH", "HOME", "TMPDIR", "LANG", "LC_ALL")
            if (v := os.environ.get(k)) is not None}

def run_local_system_probe(command, *args, timeout_seconds=None):
    if command not in _ALLOWED or tuple(args) not in _ALLOWED[command]:
        raise PermissionError("unregistered local system probe")
    resolved = shutil.which(command)
    if not resolved or not Path(resolved).is_file():
        return {"status": "EFFECT_FAILED_CONFIRMED", "returncode": 127,
                "stdout": b"", "stderr": b"command unavailable",
                "timed_out": False, "uncertainty": False}
    timeout = _TIMEOUTS[command] if timeout_seconds is None else float(timeout_seconds)
    if timeout <= 0 or timeout > _TIMEOUTS[command]:
        raise PermissionError("probe timeout outside registered bound")
    eid = "local-probe:" + command
    argv = (eid, *args)
    eff = GovernedProcessEffector(
        executable_registry={eid: {"path": resolved, "argv_prefix": list(args)}},
        environment_registry={"local-probe": _minimal_env()},
    )
    handle = SimpleNamespace(
        target_binding=eff.canonical_target(eid),
        operation_id="PROCESS_EXECUTE",
        adapter_id=ADAPTER_ID,
    )
    req = ProcessEffectRequest(
        eid, argv, None, "local-probe", "CLOSED", timeout,
        "NO_DESCENDANTS", "READ_ONLY_OBSERVATION",
    )
    return eff.execute(request=req, handle=handle, adapter_id=ADAPTER_ID)

def probe_text(command, *args, timeout_seconds=None):
    result = run_local_system_probe(command, *args, timeout_seconds=timeout_seconds)
    payload = (result.get("stdout") or b"") or (result.get("stderr") or b"")
    return payload.decode("utf-8", errors="replace").strip()
