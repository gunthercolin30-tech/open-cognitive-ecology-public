from copy import deepcopy
from acee6_k4_resource_runner import run_campaign, verify_report
r = run_campaign(warmup=1, cycles=8)["report"]
t = deepcopy(r); t["metrics"]["unhandled_exception_count"] = 99
v = verify_report(t)
assert not v["valid"] and "report_hash_invalid" in v["reasons"], v
print("ACEE6_K4_DEGRADATION_OK")
