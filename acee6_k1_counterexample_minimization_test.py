from acee6_k1_property_runner import minimize_counterexample
case={"phase":"before_mutation","persist":False,"duplicated":True,"gate":"absent","noise":"x"}
def failing(value): return value.get("phase")=="before_mutation"
minimal=minimize_counterexample(case,failing)
assert minimal=={"phase":"before_mutation"}
print("ACEE6_K1_COUNTEREXAMPLE_MINIMIZATION_OK")
