from acee6_k4_resource_runner import run_campaign
r = run_campaign(warmup=1, cycles=8)
m = r["report"]["metrics"]
assert m["temporary_residue_count"] == 0, m
assert m["child_process_delta"] == 0, m
print("ACEE6_K4_CLEANUP_OK")
