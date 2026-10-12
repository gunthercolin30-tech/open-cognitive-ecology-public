from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
py_compile.compile(str(ROOT / "ontology" / "predictive_blueprint.py"), cfile="/private/tmp/predictive_blueprint.pyc", doraise=True)

from ontology.predictive_blueprint import PredictiveBlueprint

r = PredictiveBlueprint().step(inputs={"synthetic_context": True}, persist=False)

assert r["primitive"] == "PREDICTIVE_BLUEPRINT"
assert r["step"] == "AT0"
assert r["status"] == "PREDICTIVE_BLUEPRINT_READY"
assert r["predictive_blueprint_status"] == "PREDICTIVE_BLUEPRINT_READY"
assert r["rf_star_predictive_program_ready"] is True
assert set(r["prediction_types"]) >= {"structural", "dynamic", "topological", "spectral", "developmental", "collective"}
assert r["blueprint"]["prediction_definition"]["requires_refutation_path"] is True
assert r["blueprint"]["refutation_rules"]["refutable"] is True
assert 0.0 <= r["readiness_score"] <= 1.0
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False
assert r["phenomenology_undetermined"] is True
assert r["functional_conclusion_only"] is True
assert r["persisted"] is False

print("AT0_FAST_ACCEPTANCE_ALL_OK")
