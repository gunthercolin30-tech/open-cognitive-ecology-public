from acee6_k1_property_runner import build_report

a=build_report(61001,192); b=build_report(61001,192)
assert a["campaign_hash"]==b["campaign_hash"]
assert a["case_count"]==b["case_count"]==192
assert build_report(61002,192)["campaign_hash"]!=a["campaign_hash"]
print("ACEE6_K1_DETERMINISM_OK")
