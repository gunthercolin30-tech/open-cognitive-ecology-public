from copy import deepcopy
from oif2g_test_support import *
from oif.interface.complex_manifest_profile import validate_complex_profile
r=validator().validate(MANIFEST_DIR/"portal_pilot.yaml"); assert r.valid
d=deepcopy(dict(r.manifest.as_dict())); d["layout"][0]["regions"][0]["properties"]["composition"]["tabs"][0]["component_ids"]=["unknown.component"]
bad=validator()._build_specification(d); p=validate_complex_profile(bad); assert not p.valid and any("unknown_tab_component" in e for e in p.errors)
print("OIF2G_CROSS_REFERENCE_OK")
