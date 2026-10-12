from ontology import dna_fitness_suite as d
req=("a","b")
fail=d.evaluate_scale(scale="INSTITUTION",required_invariants=req,observed_invariants={"a":True,"b":False},provenance="deg")
unk=d.evaluate_scale(scale="ROLE",required_invariants=req,observed_invariants={"a":True,"b":None},provenance="deg")
assert fail["status"]==d.FAIL and unk["status"]==d.UNDETERMINED
r=d.compose_multiscale((fail,unk),required_scales=("INSTITUTION","ROLE"),provenance="deg")
assert r["status"]==d.FAIL
print("P023_DEGRADATION_TEST_OK")
