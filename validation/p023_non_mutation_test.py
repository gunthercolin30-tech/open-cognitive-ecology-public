from copy import deepcopy
from ontology import dna_fitness_suite as d
obs={"a":True,"b":False}; before=deepcopy(obs)
r=d.evaluate_scale(scale="INSTITUTION",required_invariants=("a","b"),observed_invariants=obs,provenance="nm")
assert obs==before
m=d.fitness_manifest(); m["boundaries"]["fitness_does_not_create_norms"]=False
assert d.fitness_manifest()["boundaries"]["fitness_does_not_create_norms"] is True
print("P023_NON_MUTATION_TEST_OK")
