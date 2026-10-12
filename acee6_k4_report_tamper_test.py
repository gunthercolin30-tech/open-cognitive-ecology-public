from copy import deepcopy
from acee6_k4_resource_runner import run_campaign, verify_report
r = run_campaign(warmup=1, cycles=8)["report"]
t = deepcopy(r); t["checks"]["no_child_process_leak"] = False
v = verify_report(t)
assert not v["valid"]
print("ACEE6_K4_REPORT_TAMPER_OK")
