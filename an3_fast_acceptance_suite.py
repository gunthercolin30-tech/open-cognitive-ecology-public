#!/usr/bin/env python3
from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "ontology" / "axiom_minimality_analyzer.py"

py_compile.compile(str(TARGET), cfile="/private/tmp/axiom_minimality_analyzer.pyc", doraise=True)
py_compile.compile(str(ROOT / "an3_final_lock.py"), cfile="/private/tmp/an3_final_lock.pyc", doraise=True)

from ontology.axiom_minimality_analyzer import AxiomMinimalityAnalyzer

r = AxiomMinimalityAnalyzer().step(inputs={"synthetic": True, "axis": "AN", "step": "AN3"}, persist=False)

assert r["axiom_minimality_status"] == "AXIOM_MINIMALITY_ANALYZED"
assert r["axiom_minimality_analyzed"] is True
assert r["axiom_count"] >= 10
assert r["axiom_minimality_score"] >= 0.70
assert r["redundant_axiom_count"] == 0
assert r["removable_axiom_count"] == 0
assert r["axiom_set_functionally_minimal"] is True
assert r["ready_for_AN4_model_generation"] is True
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_undetermined"] is True
assert r["functional_conclusion_only"] is True
print("AN3_FAST_ACCEPTANCE_OK")
