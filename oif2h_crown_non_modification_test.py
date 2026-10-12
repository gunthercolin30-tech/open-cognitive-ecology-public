import hashlib
from copy import deepcopy
from pathlib import Path
from oif.interface.manifest_diff import compare_manifests
from oif2h_test_support import base_mapping

ROOT=Path(__file__).resolve().parent
paths=sorted((ROOT/"interfaces"/"examples").rglob("*.json"))+sorted((ROOT/"interfaces"/"examples").rglob("*.yaml"))+sorted((ROOT/"interfaces"/"examples").rglob("*.yml"))
before_hashes={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
left=base_mapping(); right=deepcopy(left); right["interface"]["title"]="non-modification"
left_snapshot=deepcopy(left); right_snapshot=deepcopy(right)
for _ in range(12):
    compare_manifests(left,right)
assert left==left_snapshot and right==right_snapshot
assert before_hashes=={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
print("OIF2H_CROWN_NON_MODIFICATION_OK")
