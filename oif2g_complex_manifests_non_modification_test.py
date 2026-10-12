from pathlib import Path
R=Path(__file__).resolve().parent
for rel in ("oif/interface/models.py","oif/interface/specification.py","oif/interface/serialization.py","oif/interface/manifest_validator.py","oif/interface/reference_catalog.py","oif/interface/reference_resolver.py","oif/interface/abstract_renderer.py","oif/application/default_providers.py","oif/application/shell_service.py","oif/schemas/oif_interface_schema_v1.json","interfaces/examples/minimal/home_minimal.yaml","interfaces/examples/minimal/runtime_health_minimal.yaml","interfaces/examples/minimal/civilizational_state_minimal.yaml"): assert (R/rel).is_file()
print("OIF2G_NON_MODIFICATION_OK")
