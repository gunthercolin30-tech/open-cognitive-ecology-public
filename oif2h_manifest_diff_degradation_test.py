from copy import deepcopy
from oif.interface.manifest_diff import ManifestDiffViolation, compare_manifests
from oif2h_test_support import base_mapping
b=base_mapping()
for bad in (None, {'schema_version':'bad'}, {'x':float('nan')}):
    try: compare_manifests(b,bad)
    except ManifestDiffViolation: pass
    else: raise AssertionError('invalid manifest accepted')
deep=deepcopy(b); cursor=deep['interface']['metadata']
for i in range(40): cursor['x']={}; cursor=cursor['x']
try: compare_manifests(b,deep)
except ManifestDiffViolation: pass
else: raise AssertionError('excessive depth accepted')
print('OIF2H_MANIFEST_DIFF_DEGRADATION_OK')
