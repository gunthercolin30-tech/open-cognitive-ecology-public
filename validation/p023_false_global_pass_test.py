from ontology import dna_fitness_suite as d
req=("identity",)
c=d.evaluate_scale(scale="CIVILIZATION",required_invariants=req,observed_invariants={"identity":True},provenance="fgp")
# A local PASS cannot become global PASS when required scales are absent.
r=d.compose_multiscale((c,),required_scales=("CIVILIZATION","INSTITUTION","INDIVIDUAL"),provenance="fgp")
assert r["status"]==d.UNDETERMINED
assert r["missing_scales"]==("INSTITUTION","INDIVIDUAL")
# UNDETERMINED on one required scale also blocks PASS.
i=d.evaluate_scale(scale="INSTITUTION",required_invariants=req,observed_invariants={"identity":None},provenance="fgp")
x=d.evaluate_scale(scale="INDIVIDUAL",required_invariants=req,observed_invariants={"identity":True},provenance="fgp")
r2=d.compose_multiscale((c,i,x),required_scales=("CIVILIZATION","INSTITUTION","INDIVIDUAL"),provenance="fgp")
assert r2["status"]==d.UNDETERMINED
print("P023_FALSE_GLOBAL_PASS_TEST_OK")
