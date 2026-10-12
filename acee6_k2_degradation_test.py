from acee6_k2_fuzz_runner import build_report,verify_report
r=build_report(62002,8,reduce_failures=False); r["failure_count"]=1
check=verify_report(r)
assert not check["valid"] and "report_hash_invalid" in check["reasons"] and "failure_count_nonzero" in check["reasons"]
print("ACEE6_K2_DEGRADATION_OK")
