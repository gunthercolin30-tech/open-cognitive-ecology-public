\
import hashlib
from pathlib import Path

from acee3_fast_acceptance_suite import SAMPLES
from ontology.acee_bridge_adapter import AceeBridgeAdapter


def digest(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def main() -> None:
    paths = [
        Path("ontology/acee_integration_auditor.py"),
        Path("ontology/acee_capability_map.py"),
        Path("ontology/auto_improvement_runtime_bridge.py"),
        Path("ontology/controlled_evolution_orchestrator.py"),
        Path("ontology/recursive_self_improvement_controller.py"),
        Path("ontology/recursive_self_improvement_governor.py"),
        Path("ontology/evolution_sandbox.py"),
        Path("ontology/runtime_experiment_manager.py"),
        Path("dependency_registry.py"),
        Path("ontology_inventory.txt"),
    ]
    before = {str(path): digest(path) for path in paths}
    result = AceeBridgeAdapter().step(
        inputs={
            "source_module": "auto_improvement_runtime_bridge",
            "source_result": SAMPLES["auto_improvement_runtime_bridge"],
            "adapter_timestamp_utc": "2026-07-13T15:45:00Z",
        },
        persist=False,
    )
    after = {str(path): digest(path) for path in paths}
    assert before == after
    assert result["persisted"] is False
    print("ACEE3_NON_REGRESSION_OK")


if __name__ == "__main__":
    main()
