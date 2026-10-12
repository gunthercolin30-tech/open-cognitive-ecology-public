from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
py_compile.compile(str(ROOT / "ontology" / "prediction_registry.py"), cfile="/private/tmp/prediction_registry.pyc", doraise=True)

from ontology.prediction_registry import PredictionRegistry

r = PredictionRegistry().step(inputs={"synthetic_context": True}, persist=False)

assert r["primitive"] == "PREDICTION_REGISTRY"
assert r["step"] == "AT1"
assert r["status"] == "PREDICTION_REGISTRY_READY"
assert r["prediction_registry_status"] == "PREDICTION_REGISTRY_READY"
assert r["registry_ready"] is True
assert r["prediction_count"] >= 6
assert set(r["categories"]) >= {"structural", "dynamic", "topological", "spectral", "developmental", "collective"}
assert all(r["category_counts"][c] >= 1 for c in r["categories"])
assert not r["validation"]["missing_categories"]
assert not r["validation"]["duplicate_ids"]
assert r["allowed_statuses"] == ["validated", "invalidated", "unknown"]
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False
assert r["phenomenology_undetermined"] is True
assert r["functional_conclusion_only"] is True
assert r["persisted"] is False

print("AT1_FAST_ACCEPTANCE_ALL_OK")
