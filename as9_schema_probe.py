from ontology.consciousness_longitudinal_tracker import ConsciousnessLongitudinalTracker

r = ConsciousnessLongitudinalTracker().step(
    inputs={},
    persist=False,
)

print(sorted(r.keys()))
