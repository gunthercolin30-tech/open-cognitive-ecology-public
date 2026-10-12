from copy import deepcopy
from oif.interface.manifest_diff import compare_manifests
from oif2h_test_support import base_mapping
b=base_mapping(); a=deepcopy(b)
a["interface"]["description"]="multiprocess-determinism"
a["layout"][0]["regions"][0]["component_ids"] = list(reversed(a["layout"][0]["regions"][0]["component_ids"]))
r=compare_manifests(b,a)
print(r.sha256())
