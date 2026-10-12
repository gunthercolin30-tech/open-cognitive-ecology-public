from acee6_k2_fuzz_runner import build_report
r=build_report(62002,8,reduce_failures=False)
assert r["real_root_mutation_count"]==0 and r["root_guard_mode"]=="bounded_critical_fingerprint_v2"
assert r["cleanup_failure_count"]==0
print("ACEE6_K2_REAL_ROOT_IMMUTABILITY_OK")
