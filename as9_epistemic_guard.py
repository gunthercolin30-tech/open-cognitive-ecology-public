from ontology.consciousness_longitudinal_tracker import ConsciousnessLongitudinalTracker

r = ConsciousnessLongitudinalTracker().step(
    inputs={},
    persist=False,
)

assert r["functional_conclusion_only"] is True
assert r["phenomenology_undetermined"] is True

assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False

print("AS9_EPISTEMIC_GUARD_OK")
