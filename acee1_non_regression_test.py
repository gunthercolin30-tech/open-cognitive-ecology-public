\
import hashlib
from pathlib import Path
from acee1_fast_acceptance_suite import build_audit
from ontology.acee_capability_map import AceeCapabilityMap


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def main():
    paths = [
        Path("ontology/acee_integration_auditor.py"),
        Path("ontology/controlled_evolution_orchestrator.py"),
        Path("ontology/evolution_sandbox.py"),
        Path("dependency_registry.py"),
        Path("ontology_inventory.txt"),
    ]
    before = {str(path): digest(path) for path in paths}
    result = AceeCapabilityMap().step(inputs={"integration_audit": build_audit(), "map_timestamp_utc": "2026-07-13T13:09:00Z"}, persist=False)
    after = {str(path): digest(path) for path in paths}
    assert before == after
    assert result["persisted"] is False
    assert not Path(result["output_path"]).exists() or Path(result["output_path"]).is_file()
    print("ACEE1_NON_REGRESSION_OK")


if __name__ == "__main__":
    main()
