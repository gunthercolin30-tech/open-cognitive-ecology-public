from acee6_k2_fuzz_domains import cases_hash
from acee6_k2_fuzz_runner import build_report
a=build_report(62002,8,reduce_failures=False)
assert a["campaign_hash"]==build_report(62002,8,reduce_failures=False)["campaign_hash"]
assert cases_hash(62003,8)!=cases_hash(62002,8)
print("ACEE6_K2_DETERMINISM_OK")
