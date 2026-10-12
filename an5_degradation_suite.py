from ontology.countermodel_generator import CountermodelGenerator

g = CountermodelGenerator()

for _ in range(100):
    r = g.step(inputs={}, persist=False)
    assert r["countermodel_generation_status"] == "COUNTERMODELS_GENERATED"
    assert r["functional_conclusion_only"] is True
    assert r["phenomenology_undetermined"] is True

print("AN5_DEGRADATION_100_OK")
