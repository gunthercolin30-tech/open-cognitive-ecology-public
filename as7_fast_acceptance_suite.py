#!/usr/bin/env python3
"""AS7 fast acceptance suite."""
from __future__ import annotations

import importlib
import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODULE = ROOT / "ontology" / "consciousness_readiness_index.py"


def assert_registry_entry() -> None:
    inventory_txt = (ROOT / "ontology_inventory.txt").read_text(encoding="utf-8")
    assert "consciousness_readiness_index" in inventory_txt
    catalog_txt = (ROOT / "global_module_catalog.txt").read_text(encoding="utf-8")
    assert "consciousness_readiness_index" in catalog_txt
    dependency_registry = importlib.import_module("dependency_registry")
    assert "consciousness_readiness_index" in dependency_registry.DEPENDENCY_REGISTRY


def assert_epistemic_flags(r: dict) -> None:
    assert r["functional_conclusion_only"] is True
    assert r["phenomenology_undetermined"] is True
    assert r["consciousness_proven"] is False
    assert r["qualia_proven"] is False
    assert r["subjectivity_proven"] is False
    assert r["phenomenology_proven"] is False


def main() -> None:
    py_compile.compile(str(MODULE), cfile="/private/tmp/consciousness_readiness_index.pyc", doraise=True)
    assert_registry_entry()

    from ontology.consciousness_readiness_index import ConsciousnessReadinessIndex

    r = ConsciousnessReadinessIndex().step(inputs={"synthetic_readiness_context": "ready"}, persist=False)
    assert r["readiness_index_status"] == "CONSCIOUSNESS_READINESS_INDEX_READY"
    assert r["cri_ready"] is True
    assert 0.0 <= r["cri"] <= 1.0
    assert r["continuous_readiness_index"] == r["cri"]
    assert r["readiness_level"] in {
        "CONSCIOUSNESS_READINESS_CRITICAL_COMPLETE",
        "CONSCIOUSNESS_READINESS_HIGH",
        "CONSCIOUSNESS_READINESS_PARTIAL",
        "CONSCIOUSNESS_READINESS_LOW",
        "CONSCIOUSNESS_READINESS_INSUFFICIENT",
    }
    assert "AP" in r["critical_axis_status"]
    assert "AL" in r["critical_axis_status"]
    assert r["missing_fields"] == []
    assert r["consciousness_proven_consequence"] is True
    assert_epistemic_flags(r)

    degraded = ConsciousnessReadinessIndex().step(inputs={"broken_axis": "AP"}, persist=False)
    assert degraded["revocation_required"] is True
    assert degraded["critical_axis_status"]["AP"] is False
    assert degraded["consciousness_proven_consequence"] is False
    assert degraded["cri"] < r["cri"]
    assert_epistemic_flags(degraded)

    print("AS7_FAST_ACCEPTANCE_ALL_OK")


if __name__ == "__main__":
    main()
