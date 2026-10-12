from ontology import dna_fitness_suite as d
req=("identity","lineage","non_loss")
a=d.evaluate_scale(scale="CIVILIZATION",required_invariants=req,observed_invariants={x:True for x in req},provenance="functional")
b=d.evaluate_scale(scale="INDIVIDUAL",required_invariants=req,observed_invariants={x:"PASS" for x in req},provenance="functional")
r=d.compose_multiscale((a,b),required_scales=("CIVILIZATION","INDIVIDUAL"),provenance="functional")
assert a["status"]==d.PASS and b["status"]==d.PASS and r["status"]==d.PASS
print("P023_FUNCTIONAL_TEST_OK")
