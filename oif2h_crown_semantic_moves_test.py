from copy import deepcopy
from oif.interface.manifest_diff import compare_manifests
from oif2h_test_support import base_mapping

before = base_mapping()
# Top-level entity collections are identity-addressed and non-semantic in order.
after = deepcopy(before)
after["components"] = list(reversed(after["components"]))
after["data_sources"] = list(reversed(after["data_sources"]))
assert not compare_manifests(before, after).changed

# Ordered component references retain move semantics, even with another change.
after = deepcopy(before)
refs = after["layout"][0]["regions"][0]["component_ids"]
assert len(refs) >= 2
refs[0], refs[1] = refs[1], refs[0]
after["components"][0]["properties"]["text"] = "crown-modified"
report = compare_manifests(before, after)
assert report.counts["moved"] >= 2, report.as_dict()
assert report.counts["modified"] >= 1, report.as_dict()
assert [e.path for e in report.entries] == sorted(e.path for e in report.entries)
print("OIF2H_CROWN_SEMANTIC_MOVES_OK")
