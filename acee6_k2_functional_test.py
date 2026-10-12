from acee6_k2_fuzz_runner import build_report,verify_report
r=build_report(62002,16,reduce_failures=False)
assert r["case_count"]==16 and set(r["family_counts"])
assert verify_report(r)["valid"],verify_report(r)
print("ACEE6_K2_FUNCTIONAL_OK")
