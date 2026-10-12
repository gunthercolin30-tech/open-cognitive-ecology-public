\
from __future__ import annotations

import py_compile
import tempfile
from pathlib import Path

from ontology.acee_bridge_adapter import AceeBridgeAdapter, SUPPORTED_SOURCES

SAMPLES = {
    "auto_improvement_runtime_bridge": {
        "primitive": "AUTO_IMPROVEMENT_RUNTIME_BRIDGE",
        "integration_status": "ready",
        "pipeline_score": 0.91,
        "confidence": 0.88,
        "rollback_available": True,
        "state_path": "/tmp/state.json",
    },
    "controlled_evolution_orchestrator": {
        "primitive": "CONTROLLED_EVOLUTION_ORCHESTRATOR",
        "status": "approved",
        "approved": True,
        "orchestration_stability_index": 0.92,
        "governance_approval_rate": 0.9,
        "rollback_available": True,
    },
    "recursive_self_improvement_controller": {
        "primitive": "RECURSIVE_SELF_IMPROVEMENT_CONTROLLER",
        "status": "ready",
        "accepted": True,
        "self_improvement_control_score": 0.89,
        "confidence": 0.87,
    },
    "recursive_self_improvement_governor": {
        "primitive": "RECURSIVE_SELF_IMPROVEMENT_GOVERNOR",
        "status": "operational",
        "approved": True,
        "governance_approval_rate": 0.93,
    },
    "evolution_sandbox": {
        "primitive": "EVOLUTION_SANDBOX",
        "sandbox_decision": "sandbox_approved",
        "sandbox_approved": True,
        "sandbox_score": 0.94,
        "sandbox_rollback_required": False,
    },
    "runtime_experiment_manager": {
        "primitive": "RUNTIME_EXPERIMENT_MANAGER",
        "status": "completed",
        "cycles_executed": 3,
        "final_metrics": {"global_viability_score": 0.93},
        "report_path": "/tmp/report.json",
    },
}


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="acee3_compile_") as directory:
        py_compile.compile(
            "ontology/acee_bridge_adapter.py",
            cfile=str(Path(directory) / "acee_bridge_adapter.pyc"),
            doraise=True,
        )
    adapter = AceeBridgeAdapter(root=Path("/nonexistent"))
    for source in SUPPORTED_SOURCES:
        result = adapter.step(
            inputs={
                "source_module": source,
                "source_result": SAMPLES[source],
                "adapter_timestamp_utc": "2026-07-13T15:40:00Z",
            },
            persist=False,
        )
        assert result["adapter_status"] == "ACEE_BRIDGE_ADAPTER_READY"
        assert result["adapter_ready"] is True
        assert result["source_module"] == source
        assert result["raw_result"] == SAMPLES[source]
        assert len(result["normalized_hash"]) == 64
        assert result["functional_conclusion_only"] is True
        assert result["phenomenology_undetermined"] is True
    print("ACEE3_FAST_ACCEPTANCE_OK")


if __name__ == "__main__":
    main()
