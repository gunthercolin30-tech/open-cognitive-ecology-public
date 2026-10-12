from oif2g_test_support import *
from oif.interface.complex_manifest_profile import validate_complex_profile
count=0
for name in NAMES:
 r=validator().validate(MANIFEST_DIR/(name+".yaml")); assert r.valid and not r.manifest.operations; assert all(not c.operation_ids for c in r.manifest.components); p=validate_complex_profile(r.manifest); assert p.valid; count+=p.dormant_operation_count
assert count>=2
print("OIF2G_DORMANT_OPERATIONS_OK")
