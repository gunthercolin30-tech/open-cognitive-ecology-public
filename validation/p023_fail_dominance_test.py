from ontology import dna_fitness_suite as d
req=("x",)
def ev(scale,value):
    return d.evaluate_scale(scale=scale,required_invariants=req,observed_invariants={"x":value},provenance="dom")
p=ev("CIVILIZATION",True); u=ev("INSTITUTION",None); f=ev("INDIVIDUAL",False)
r=d.compose_multiscale((p,u,f),required_scales=("CIVILIZATION","INSTITUTION","INDIVIDUAL"),provenance="dom")
assert r["status"]==d.FAIL
# Missing scale does not hide an explicit failure.
r2=d.compose_multiscale((p,f),required_scales=("CIVILIZATION","INSTITUTION","INDIVIDUAL"),provenance="dom")
assert r2["status"]==d.UNDETERMINED  # coverage incomplete: no global claim
assert r2["missing_scales"]==("INSTITUTION",)
print("P023_FAIL_DOMINANCE_TEST_OK")
