from copy import deepcopy
from oif.interface.manifest_diff import compare_manifests
from oif2h_test_support import base_mapping
b=base_mapping(); a=deepcopy(b); a['interface']['description']='changed'; a['data_sources']=list(reversed(a['data_sources']))
reports=[compare_manifests(b,a) for _ in range(25)]
assert len({r.canonical_json() for r in reports})==1
assert len({r.sha256() for r in reports})==1
# Reordering top-level entity collections is non-semantic.
c=deepcopy(b); c['components']=list(reversed(c['components'])); c['layout']=list(reversed(c['layout']))
assert not compare_manifests(b,c).changed
print('OIF2H_MANIFEST_DIFF_DETERMINISM_OK')
