from oif2b_test_support import build_spec
first = build_spec()
second = build_spec()
assert first.canonical_json() == second.canonical_json()
assert first.sha256() == second.sha256()
print("OIF2B_DETERMINISM_OK", first.sha256())
