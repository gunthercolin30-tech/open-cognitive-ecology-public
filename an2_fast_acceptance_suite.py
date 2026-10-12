#!/usr/bin/env python3
from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "ontology" / "axiom_independence_tester.py"

py_compile.compile(str(TARGET), cfile="/private/tmp/axiom_independence_tester.pyc", doraise=True)
py_compile.compile(str(ROOT / "an2_final_lock.py"), cfile="/private/tmp/an2_final_lock.pyc", doraise=True)

from ontology.axiom_independence_tester import AxiomIndependenceTester

r = AxiomIndependenceTester().step(inputs={"synthetic": True, "axis": "AN", "step": "AN2"}, persist=False)

assert r["axiom_independence_status"] == "AXIOM_INDEPENDENCE_TESTED"
assert r["axiom_independence_tested"] is True
assert r["axiom_count"] >= 10
assert r["mean_axiom_independence_score"] >= 0.70
assert r["potentially_derivable_axiom_count"] == 0
assert r["circular_dependency_count"] == 0
assert r["ready_for_AN3_minimality_analysis"] is True
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_undetermined"] is True
assert r["functional_conclusion_only"] is True
print("AN2_FAST_ACCEPTANCE_OK")
