import hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
EXPECTED={'oif/interface/models.py': '661c517dd422d47f62c0385ce2b41735bee1faf595d20b20f79b2bae4178f57f', 'oif/interface/specification.py': '38b562dfb4b3f9beb81302810e284dd56c3ea0912266bf5a6359377ea15a1e59', 'oif/interface/serialization.py': '279051f631b87eb7fc296a470b812590ffaaece29d248e243dbbf9910610f3e5', 'oif/interface/manifest_validator.py': '24150c355444de4dbdb76c1bc7dda859fc1bf6a1864b5ac67f782fd88a187b61', 'oif/interface/reference_catalog.py': 'd5a2dcc7d1071383e600d25b72c5ceb76015ff4dce3f7d66cb9ccaa8a3035dd9', 'oif/interface/reference_resolver.py': '56021fde1f7269c8ccb9bf0cf760055c4555409ba342b3684edfb78539cb7599', 'oif/application/default_providers.py': 'd7b8a2e014cc9e94477e835b3abaaea9737beb13d46b01e449af25971349ad4f', 'oif/application/shell_service.py': '5fcaef2f26114f893249b658fd0afea154b3ee9952b588bc76d453198286e009', 'oif/schemas/oif_interface_schema_v1.json': '723ce0f44250ef9570d72430299bd12edac0b84dfd577bd72934e2fa2bce0603'}
for rel, expected in EXPECTED.items():
    actual=hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
    assert actual == expected, (rel, expected, actual)
print("OIF2F_NON_MODIFICATION_OK")
