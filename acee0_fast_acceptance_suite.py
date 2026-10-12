\
from pathlib import Path
import py_compile
import tempfile
from ontology.acee_integration_auditor import AceeIntegrationAuditor


def build_context():
    return {
        "audit_timestamp_utc": "2026-07-13T12:00:00Z",
        "modules": [
            "auto_improvement_runtime_bridge",
            "controlled_evolution_orchestrator",
            "recursive_self_improvement_controller",
            "recursive_self_improvement_governor",
            "evolution_sandbox",
            "constitutional_evolution_gate",
            "runtime_experiment_manager",
            "genealogical_evolution_dashboard",
            "scientific_meta_analysis_engine",
            "ontology_gap_detector",
            "ontology_redundancy_audit",
            "metrics_history_recorder",
            "validation_history_archive",
        ],
        "dependencies": {
            "controlled_evolution_orchestrator": ["evolution_sandbox"],
            "auto_improvement_runtime_bridge": ["controlled_evolution_orchestrator"],
        },
    }


def main():
    with tempfile.TemporaryDirectory(prefix="oce_acee0_compile_") as tmp:
        py_compile.compile(
            "ontology/acee_integration_auditor.py",
            cfile=str(Path(tmp) / "acee0.pyc"),
            doraise=True,
        )
    with tempfile.TemporaryDirectory(prefix="oce_acee0_") as tmp:
        result = AceeIntegrationAuditor(root=Path(tmp)).step(inputs=build_context(), persist=True)
        assert result["audit_status"] == "ACEE_INTEGRATION_AUDIT_COMPLETE"
        assert result["audit_completed"] is True
        assert 0.0 <= result["coverage_score"] <= 1.0
        assert len(result["integration_hash"]) == 64
        assert len(result["audit_hash"]) == 64
        assert result["recommendation_justifications_complete"] is True
        assert Path(result["output_path"]).is_file()
        assert Path(result["history_path"]).is_file()
        assert result["consciousness_proven"] is False
        assert result["collective_consciousness_proven"] is False
        assert result["functional_conclusion_only"] is True
        assert result["phenomenology_undetermined"] is True
    print("ACEE0_FAST_ACCEPTANCE_OK")


if __name__ == "__main__":
    main()
