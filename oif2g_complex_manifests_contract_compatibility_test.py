from copy import deepcopy
from oif2g_test_support import *
from oif.interface.complex_manifest_profile import validate_complex_profile
r=validator().validate(MANIFEST_DIR/"science_validation_pilot.yaml"); assert r.valid and validate_complex_profile(r.manifest).valid
d=deepcopy(dict(r.manifest.as_dict())); d["components"][0]["properties"]["input_contract"]="runtime.health.v1"
p=validate_complex_profile(validator()._build_specification(d)); assert not p.valid and any("incompatible_contract" in e for e in p.errors)
print("OIF2G_CONTRACT_COMPATIBILITY_OK")
