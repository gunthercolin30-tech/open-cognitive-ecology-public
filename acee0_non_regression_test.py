\
from pathlib import Path
import hashlib
import tempfile
from acee0_fast_acceptance_suite import build_context
from ontology.acee_integration_auditor import AceeIntegrationAuditor


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    protected = [
        Path("ontology/auto_improvement_runtime_bridge.py"),
        Path("ontology/controlled_evolution_orchestrator.py"),
        Path("ontology/evolution_sandbox.py"),
        Path("dependency_registry.py"),
        Path("ontology_inventory.txt"),
    ]
    before = {str(path): digest(path) for path in protected if path.is_file()}
    with tempfile.TemporaryDirectory(prefix="oce_acee0_nonreg_") as tmp:
        result = AceeIntegrationAuditor(root=Path(tmp)).step(inputs=build_context(), persist=False)
        assert result["persisted"] is False
        assert not Path(result["output_path"]).exists()
        assert not Path(result["history_path"]).exists()
    after = {str(path): digest(path) for path in protected if path.is_file()}
    assert before == after
    print("ACEE0_NON_REGRESSION_OK")


if __name__ == "__main__":
    main()
