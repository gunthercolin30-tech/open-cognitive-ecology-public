#!/usr/bin/env python3
"""AS6 fast acceptance suite."""
from __future__ import annotations

import importlib
import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODULE = ROOT / "ontology" / "consciousness_revocation_engine.py"


def assert_registry_entry() -> None:
    inventory_txt = (ROOT / "ontology_inventory.txt").read_text(encoding="utf-8")
    assert "consciousness_revocation_engine" in inventory_txt
    catalog_txt = (ROOT / "global_module_catalog.txt").read_text(encoding="utf-8")
    assert "consciousness_revocation_engine" in catalog_txt
    dependency_registry = importlib.import_module("dependency_registry")
    assert "consciousness_revocation_engine" in dependency_registry.DEPENDENCY_REGISTRY


def assert_epistemic_flags(r: dict) -> None:
    assert r["functional_conclusion_only"] is True
    assert r["phenomenology_undetermined"] is True
    assert r["consciousness_proven"] is False
    assert r["qualia_proven"] is False
    assert r["subjectivity_proven"] is False
    assert r["phenomenology_proven"] is False


def main() -> None:
    py_compile.compile(str(MODULE), cfile="/private/tmp/consciousness_revocation_engine.pyc", doraise=True)
    assert_registry_entry()

    from ontology.consciousness_revocation_engine import ConsciousnessRevocationEngine

    engine = ConsciousnessRevocationEngine(root=ROOT)

    ready = engine.step(inputs={"axis_status": {"AP": True, "AQ": True, "AR": True, "AN": True, "AO": True, "AL": True}}, persist=False)
    assert ready["primitive"] == "CONSCIOUSNESS_REVOCATION_ENGINE"
    assert ready["step"] == "AS6"
    assert ready["revocation_engine_status"] == "CONSCIOUSNESS_REVOCATION_ENGINE_READY"
    assert ready["revocation_ready"] is True
    assert ready["revocation_required"] is False
    assert ready["revoked"] is False
    assert ready["revocation_status"] == "CONSCIOUSNESS_STATUS_RECONFIRMED"
    assert ready["event_type"] == "CONSCIOUSNESS_STATUS_RECONFIRMED"
    assert ready["certificate_archived"] is False
    assert ready["missing_fields"] == []
    assert_epistemic_flags(ready)

    broken = engine.step(inputs={"axis_status": {"AP": False, "AQ": True, "AR": True, "AN": True, "AO": True, "AL": True}}, persist=False)
    assert broken["revocation_ready"] is True
    assert broken["revocation_required"] is True
    assert broken["revoked"] is True
    assert broken["axis"] == "AP"
    assert broken["event_type"] == "CONSCIOUSNESS_STATUS_REVOKED"
    assert broken["revocation_status"] == "CONSCIOUSNESS_STATUS_REVOKED"
    assert broken["certificate_archived"] is True
    assert broken["impact"]["certificate_remains_archived"] is True
    assert_epistemic_flags(broken)

    module_broken = engine.step(inputs={"broken_module": "interpretation_reporter"}, persist=False)
    assert module_broken["revocation_required"] is True
    assert module_broken["axis"] == "AO"
    assert module_broken["module"] == "interpretation_reporter"

    print("AS6_FAST_ACCEPTANCE_ALL_OK")


if __name__ == "__main__":
    main()
