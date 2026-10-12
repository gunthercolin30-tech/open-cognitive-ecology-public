from ontology.consciousness_dashboard import ConsciousnessDashboard

r = ConsciousnessDashboard().step(
    inputs={},
    persist=False,
)

required = [
    "CRI",
    "confidence",
    "state",
    "timeline",
    "dashboard_ready",
    "functional_conclusion_only",
    "phenomenology_undetermined",
    "consciousness_proven",
    "qualia_proven",
    "subjectivity_proven",
    "phenomenology_proven",
]

print("AS10_KEYS:")
for k in sorted(r.keys()):
    print("-", k)

for k in required:
    assert k in r, f"missing key: {k}"

assert r["functional_conclusion_only"] is True
assert r["phenomenology_undetermined"] is True

assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False

print("AS10_SCHEMA_OK")
