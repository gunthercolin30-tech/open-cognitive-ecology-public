#!/usr/bin/env python3
"""AS17 fast acceptance suite."""
from __future__ import annotations

import importlib
import py_compile
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
MODULE_PATH = ROOT / "ontology" / "consciousness_dependency_visualizer.py"
LOCK_PATH = ROOT / "as17_final_lock.py"


def main() -> None:
    py_compile.compile(str(MODULE_PATH), cfile="/private/tmp/consciousness_dependency_visualizer.pyc", doraise=True)
    py_compile.compile(str(LOCK_PATH), cfile="/private/tmp/as17_final_lock.pyc", doraise=True)
    mod = importlib.import_module("ontology.consciousness_dependency_visualizer")
    cls = getattr(mod, "ConsciousnessDependencyVisualizer")
    r = cls().step(inputs={"status_payloads": {}}, persist=False)
    assert r["primitive"] == "CONSCIOUSNESS_DEPENDENCY_VISUALIZER"
    assert r["step"] == "AS17"
    assert r["dependency_visualizer_status"] == "CONSCIOUSNESS_DEPENDENCY_VISUALIZER_READY"
    assert r["node_count"] >= 18
    assert r["edge_count"] >= 17
    assert isinstance(r["nodes"], list) and isinstance(r["edges"], list)
    assert set(r["color_counts"]).issuperset({"green", "orange", "red"})
    assert 0.0 <= r["dependency_health"] <= 1.0
    assert "digraph" in r["dot"]
    assert "flowchart" in r["mermaid"]
    assert r["consciousness_proven"] is False
    assert r["qualia_proven"] is False
    assert r["subjectivity_proven"] is False
    assert r["phenomenology_proven"] is False
    assert r["phenomenology_undetermined"] is True
    assert r["functional_conclusion_only"] is True
    degraded = cls().step(inputs={"status_payloads": {"consciousness_dashboard": [{"status": "missing", "confidence": 0.2}]}}, persist=False)
    assert degraded["dependency_visualizer_status"] == "CONSCIOUSNESS_DEPENDENCY_VISUALIZER_READY"
    assert degraded["node_count"] == r["node_count"]
    print("AS17_FAST_ACCEPTANCE_ALL_OK")


if __name__ == "__main__":
    main()
