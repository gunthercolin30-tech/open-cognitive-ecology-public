from copy import deepcopy
from oif.interface.manifest_diff import DiffEntry, _escape, compare_manifests
from oif2h_test_support import base_mapping

assert _escape("a~/b") == "a~0~1b"
entry = DiffEntry("moved", "/x/@a~0~1b", from_path="/x/0", to_path="/x/1")
assert dict(entry.as_dict())["path"] == "/x/@a~0~1b"

before = base_mapping()
after = deepcopy(before)
ids = after["layout"][0]["regions"][0]["component_ids"]
assert len(ids) >= 2
ids[0], ids[1] = ids[1], ids[0]
report = compare_manifests(before, after)
moves = [e for e in report.entries if e.change == "moved"]
assert len(moves) >= 2, report.as_dict()
assert all(e.from_path and e.to_path for e in moves)
assert all(e.domain == "layouts" for e in moves)
print("OIF2H_CROWN_IDENTITY_PATH_OK")
