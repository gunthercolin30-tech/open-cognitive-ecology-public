from pathlib import Path
from ontology.predictive_theory_certifier import PredictiveTheoryCertifier

ready = PredictiveTheoryCertifier().step(persist=False)

assert ready["step"] == "AT10"
assert ready["certification_status"] == "RF_PREDICTIVE_THEORY_CERTIFIED"
assert ready["predictive_theory_certified"] is True
assert ready["functional_conclusion_only"] is True
assert ready["phenomenology_undetermined"] is True
assert ready["consciousness_proven"] is False
assert ready["qualia_proven"] is False
assert ready["subjectivity_proven"] is False
assert ready["phenomenology_proven"] is False

bad = {
    "prediction_registry": {"registry_complete": False},
    "predictive_power_index": {"predictive_power_index": 0.1},
}

degraded = PredictiveTheoryCertifier().step(inputs=bad, persist=False)

assert degraded["predictive_theory_certified"] is False
assert degraded["certification_status"] != "RF_PREDICTIVE_THEORY_CERTIFIED"
assert degraded["functional_conclusion_only"] is True
assert degraded["consciousness_proven"] is False

persisted = PredictiveTheoryCertifier().step(persist=True)
path = Path(persisted["certification_record_path"])
assert path.exists()
assert path.suffix == ".json"

print("AT10_EXTENDED_FINAL_LOCK_OK")
