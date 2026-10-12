from ontology import dna_fitness_suite as d

# Near-miss statuses/scales must be rejected.
for bad in ("pass","PASSED","TRUE","UNKNOWN",""):
    try:
        d.evaluate_scale(scale="CIVILIZATION",required_invariants=("x",),observed_invariants={"x":bad},provenance="adv")
        raise AssertionError("accepted_bad_observation:"+repr(bad))
    except ValueError:
        pass
for bad in ("civilization","GLOBAL","SYSTEM",""):
    try:
        d.evaluate_scale(scale=bad,required_invariants=("x",),observed_invariants={"x":True},provenance="adv")
        raise AssertionError("accepted_bad_scale:"+repr(bad))
    except ValueError:
        pass

# Duplicate requirements and malformed observations are rejected.
for req in (("x","x"), (), ["x"]):
    try:
        d.evaluate_scale(scale="CIVILIZATION",required_invariants=req,observed_invariants={"x":True},provenance="adv")
        raise AssertionError("accepted_bad_requirements")
    except ValueError:
        pass
print("P023_BOUNDARY_ADVERSARIAL_TEST_OK")
