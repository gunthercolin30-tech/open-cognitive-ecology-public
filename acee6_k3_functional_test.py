from acee6_k3_mutation_runner import run
r=run(limit=5); assert r["verification"]["valid"] and r["report"]["mutation_score"]==1.0,r
print("ACEE6_K3_FUNCTIONAL_OK")
