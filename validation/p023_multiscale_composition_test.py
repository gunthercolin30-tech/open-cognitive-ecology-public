from ontology import dna_fitness_suite as d
req=("x",)
c=d.evaluate_scale(scale="CIVILIZATION",required_invariants=req,observed_invariants={"x":True},provenance="multi")
i=d.evaluate_scale(scale="INDIVIDUAL",required_invariants=req,observed_invariants={"x":True},provenance="multi")
partial=d.compose_multiscale((c,),required_scales=("CIVILIZATION","INDIVIDUAL"),provenance="multi")
full=d.compose_multiscale((c,i),required_scales=("CIVILIZATION","INDIVIDUAL"),provenance="multi")
assert partial["status"]==d.UNDETERMINED and partial["missing_scales"]==("INDIVIDUAL",)
assert full["status"]==d.PASS
print("P023_MULTISCALE_COMPOSITION_TEST_OK")
