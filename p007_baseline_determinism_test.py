from ontology.baseline_integrity import build_manifest

a = build_manifest()
b = build_manifest()
assert a["baseline_identity_sha256"] == b["baseline_identity_sha256"]
assert a["functional_files"] == b["functional_files"]
assert a["dependencies"] == b["dependencies"]
assert a["git"] == b["git"]
print("P007_BASELINE_DETERMINISM_OK")
