from acee6_k1_property_runner import build_report, verify_report
report=build_report(61001,64); assert verify_report(report)["valid"]
report["case_count"]+=1
check=verify_report(report); assert not check["valid"] and "report_hash_invalid" in check["reasons"]
print("ACEE6_K1_REPORT_TAMPER_OK")
