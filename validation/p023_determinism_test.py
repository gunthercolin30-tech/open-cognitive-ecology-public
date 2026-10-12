from ontology import dna_fitness_suite as d
kw=dict(scale="CRITICAL_COMPONENT",required_invariants=("a","b"),observed_invariants={"a":True,"b":None},provenance="det")
assert d.evaluate_scale(**kw)==d.evaluate_scale(**kw)
assert d.fitness_manifest()==d.fitness_manifest()
print("P023_DETERMINISM_TEST_OK")
