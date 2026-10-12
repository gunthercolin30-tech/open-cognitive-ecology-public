from __future__ import annotations
from oif.interface import ManifestValidator

validator = ManifestValidator(max_errors=8)
for source, fmt in (("{", "json"), ("- item", "yaml"), ("null", "json"), ("{}", "toml")):
    report = validator.validate(source, fmt)
    assert not report.valid
    assert report.error_count >= 1
    assert report.errors[0].path == "/"
print("OIF2D_DEGRADATION_OK")
