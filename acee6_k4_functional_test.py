from acee6_k4_resource_runner import run_campaign
r = run_campaign(warmup=1, cycles=8)
assert r["verification"]["valid"], r
assert r["report"]["measured_cycles"] == 8
print("ACEE6_K4_FUNCTIONAL_OK")
