from oif.interface.manifest_diff import (
    MAX_DIFF_ENTRIES, DiffEntry, ManifestDiffViolation, _append, _plain
)

entries = []
for index in range(MAX_DIFF_ENTRIES):
    _append(entries, DiffEntry("added", f"/x/{index}", after=index))
assert len(entries) == MAX_DIFF_ENTRIES
try:
    _append(entries, DiffEntry("added", "/overflow", after=True))
except ManifestDiffViolation as exc:
    assert "maximum diff entry count" in str(exc)
else:
    raise AssertionError("diff limit did not fail closed")

value = "leaf"
for _ in range(32):
    value = {"x": value}
_plain(value)
value = {"x": value}
try:
    _plain(value)
except ManifestDiffViolation as exc:
    assert "nesting depth" in str(exc)
else:
    raise AssertionError("depth limit did not fail closed")
print("OIF2H_CROWN_LIMITS_FAIL_CLOSED_OK")
