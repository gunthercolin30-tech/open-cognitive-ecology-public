from acee6_k2_fuzz_runner import build_report,verify_report
r=build_report(62002,8,reduce_failures=False); assert verify_report(r)["valid"]
r["family_counts"][next(iter(r["family_counts"]))]+=1
assert "report_hash_invalid" in verify_report(r)["reasons"]
print("ACEE6_K2_REPORT_TAMPER_OK")
