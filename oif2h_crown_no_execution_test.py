from copy import deepcopy
from oif.interface.manifest_diff import ManifestDiffViolation, compare_manifests
from oif2h_test_support import base_mapping

class Trap:
    called=False
    def __call__(self):
        type(self).called=True
        raise AssertionError("trap executed")

before=base_mapping(); after=deepcopy(before)
after["interface"]["metadata"]["trap"] = Trap()
try:
    compare_manifests(before,after)
except ManifestDiffViolation:
    pass
else:
    raise AssertionError("non-declarative callable accepted")
assert Trap.called is False
print("OIF2H_CROWN_NO_EXECUTION_OK")
