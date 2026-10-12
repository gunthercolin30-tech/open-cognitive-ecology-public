from ontology.theorem_prediction_generator import TheoremPredictionGenerator

r = TheoremPredictionGenerator().step(inputs={}, persist=False)

assert r["primitive"] == "THEOREM_PREDICTION_GENERATOR"
assert r["step"] == "AT2"
assert r["prediction_count"] >= r["theorem_count"]
assert isinstance(r["theorem_predictions"], list)
assert isinstance(r["generated_prediction_categories"], list)

for k in [
    "consciousness_proven",
    "qualia_proven",
    "subjectivity_proven",
    "phenomenology_proven",
]:
    assert r[k] is False

assert r["functional_conclusion_only"] is True
assert r["phenomenology_undetermined"] is True

print("AT2_PUBLIC_SCHEMA_SMOKE_OK")
