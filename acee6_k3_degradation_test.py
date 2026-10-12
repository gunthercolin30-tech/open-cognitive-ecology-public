from acee6_k3_mutation_runner import run,verify
r=run(limit=1)["report"]; r["killed_count"]=0; assert not verify(r)["valid"]
print("ACEE6_K3_DEGRADATION_OK")
