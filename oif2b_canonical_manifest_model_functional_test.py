from oif2b_test_support import build_spec
spec = build_spec()
assert spec.schema_version == "oif.interface.v1"
assert spec.interface.interface_id == "oce.main"
assert spec.navigation.default_zone_id == "overview"
assert spec.data_sources[0].provider_id == "runtime.health"
assert spec.sha256() == spec.sha256()
assert '"schema_version":"oif.interface.v1"' in spec.canonical_json()
print("OIF2B_FUNCTIONAL_OK")
