\
from pathlib import Path
import py_compile
import tempfile

from ontology.acee_capability_map import AceeCapabilityMap
from ontology.acee_integration_auditor import AceeIntegrationAuditor


def build_audit():
    modules = [
        "acee_integration_auditor", "acee_capability_map",
        "auto_improvement_runtime_bridge", "controlled_evolution_orchestrator",
        "recursive_self_improvement_controller", "evolution_sandbox",
        "constitutional_evolution_gate", "runtime_experiment_manager",
        "genealogical_evolution_dashboard", "scientific_meta_analysis_engine",
        "validation_history_archive", "metrics_history_recorder",
        "performance_improvement_planner", "trajectory_prediction",
    ]
    return AceeIntegrationAuditor(root=Path("/nonexistent")).step(
        inputs={"modules": modules, "dependencies": {}, "audit_timestamp_utc": "2026-07-13T13:00:00Z"},
        persist=False,
    )


def main():
    with tempfile.TemporaryDirectory(prefix="oce_acee1_compile_") as tmp:
        py_compile.compile("ontology/acee_capability_map.py", cfile=str(Path(tmp) / "acee1.pyc"), doraise=True)
    with tempfile.TemporaryDirectory(prefix="oce_acee1_") as tmp:
        result = AceeCapabilityMap(root=Path(tmp)).step(
            inputs={"integration_audit": build_audit(), "map_timestamp_utc": "2026-07-13T13:01:00Z"},
            persist=True,
        )
        assert result["capability_map_status"] == "ACEE_CAPABILITY_MAP_READY"
        assert result["capability_map_ready"] is True
        assert result["capability_count"] == 21
        assert result["deferred_capabilities"] == ["ACEE5", "ACEE6"]
        assert 0.0 <= result["coverage_score"] <= 1.0
        assert len(result["mapping_hash"]) == 64
        assert result["recommendation_justifications_complete"] is True
        assert Path(result["output_path"]).is_file()
        assert Path(result["history_path"]).is_file()
        assert result["functional_conclusion_only"] is True
        assert result["phenomenology_undetermined"] is True
    print("ACEE1_FAST_ACCEPTANCE_OK")


if __name__ == "__main__":
    main()
