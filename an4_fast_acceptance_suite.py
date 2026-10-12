#!/usr/bin/env python3
from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "ontology" / "model_generator.py"

py_compile.compile(str(TARGET), cfile="/private/tmp/model_generator.pyc", doraise=True)
py_compile.compile(str(ROOT / "an4_final_lock.py"), cfile="/private/tmp/an4_final_lock.pyc", doraise=True)

from ontology.model_generator import ModelGenerator

r = ModelGenerator().step(inputs={"synthetic": True, "axis": "AN", "step": "AN4"}, persist=False)

assert r["model_generation_status"] == "AXIOMATIC_MODELS_GENERATED"
assert r["axiomatic_models_generated"] is True
assert r["axiom_count"] >= 10
assert r["minimal_axiom_count"] >= 10
assert r["model_count"] >= 3
assert r["satisfying_model_count"] >= 2
assert r["mean_model_axiom_coverage"] >= 0.95
assert r["mean_model_consistency_score"] >= 0.90
assert r["axiom_core_satisfiable"] is True
assert r["ready_for_AN5_countermodel_generation"] is True
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_undetermined"] is True
assert r["functional_conclusion_only"] is True
print("AN4_FAST_ACCEPTANCE_OK")
