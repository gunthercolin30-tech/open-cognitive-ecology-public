from acee6_k4_resource_support import TARGET, file_sha
from acee6_k4_resource_runner import run_campaign
before = file_sha(TARGET)
r = run_campaign(warmup=1, cycles=8)
after = file_sha(TARGET)
assert before == after
assert r["report"]["real_root_mutation_count"] == 0
print("ACEE6_K4_NON_REGRESSION_OK")
