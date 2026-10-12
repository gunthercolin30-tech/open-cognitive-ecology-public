
from __future__ import annotations

from pathlib import Path
import py_compile

from ontology.architecture_registry import ArchitectureRegistry

ROOT = Path(__file__).resolve().parent


def main() -> None:
    py_compile.compile(str(ROOT / "ontology" / "architecture_registry.py"), cfile="/private/tmp/architecture_registry.pyc", doraise=True)
    py_compile.compile(str(ROOT / "au1_final_lock.py"), cfile="/private/tmp/au1_final_lock.pyc", doraise=True)
    r = ArchitectureRegistry().step(inputs={"source": "au1_fast_acceptance"}, persist=False)
    assert r["primitive"] == "ARCHITECTURE_REGISTRY"
    assert r["step"] == "AU1"
    assert r["architecture_registry_status"] == "ARCHITECTURE_REGISTRY_READY"
    assert r["architecture_registry_ready"] is True
    assert r["comparative_registry_ready"] is True
    assert r["architecture_count"] >= 6
    assert r["architecture_type_count"] >= 6
    assert r["oce_registered"] is True
    assert r["llm_registered"] is True
    assert r["agentic_system_registered"] is True
    assert r["robotic_system_registered"] is True
    assert r["human_dataset_placeholder_registered"] is True
    assert r["future_architecture_slots"] >= 1
    assert len(r["registered_architecture_ids"]) == len(set(r["registered_architecture_ids"]))
    assert "unified_measurement_protocol" in r["downstream_modules"]
    assert r["registration_policy"]["forbids_phenomenological_inference_from_registration"] is True
    assert r["normalization_contract"]["upstream_blueprint"] == "comparative_blueprint"
    assert r["functional_conclusion_only"] is True
    assert r["phenomenology_undetermined"] is True
    assert r["consciousness_proven"] is False
    assert r["qualia_proven"] is False
    assert r["subjectivity_proven"] is False
    assert r["phenomenology_proven"] is False
    print("AU1_FAST_ACCEPTANCE_OK")


if __name__ == "__main__":
    main()
