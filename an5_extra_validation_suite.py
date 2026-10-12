from ontology.countermodel_generator import CountermodelGenerator

g = CountermodelGenerator()

r1 = g.step(persist=False)
r2 = g.step(persist=False)

assert r1 == r2
assert r1["countermodel_generation_status"] == "COUNTERMODELS_GENERATED"
assert r1["step"] == "AN5"

expected = {
    "step",
    "countermodel_generation_status",
    "countermodels",
    "necessary_axiom_count",
    "functional_conclusion_only",
    "phenomenology_undetermined",
    "consciousness_proven",
    "qualia_proven",
    "subjectivity_proven",
}

assert not (expected - set(r1))

assert isinstance(r1["countermodels"], list)
assert isinstance(r1["necessary_axiom_count"], int)
assert r1["necessary_axiom_count"] >= 0

assert r1["functional_conclusion_only"] is True
assert r1["phenomenology_undetermined"] is True
assert r1["consciousness_proven"] is False
assert r1["qualia_proven"] is False
assert r1["subjectivity_proven"] is False

for _ in range(100):
    g.step(persist=False)

print("AN5_EXTRA_VALIDATION_SUITE_OK")
