from copy import deepcopy
from oif.interface.manifest_diff import compare_manifests
from oif2h_test_support import base_mapping

before = base_mapping(); after = deepcopy(before)
after["interface"]["description"] = "tamper-test"
report = compare_manifests(before, after)
canonical = report.canonical_json(); digest = report.sha256()

for mapping in (report.counts, report.as_dict()):
    try:
        mapping["x"] = 1
    except TypeError:
        pass
    else:
        raise AssertionError("immutable public mapping was mutable")

copy_view = dict(report.as_dict())
copy_view["entries"][0]["path"] = "/forged"
copy_view["counts"]["modified"] = 999
assert report.canonical_json() == canonical
assert report.sha256() == digest
assert "/forged" not in report.human_text()
print("OIF2H_CROWN_IMMUTABILITY_TAMPER_OK")
