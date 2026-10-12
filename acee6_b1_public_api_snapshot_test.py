import inspect
import ontology.acee_installation_executor as m
assert callable(m.AceeInstallationExecutor)
assert tuple(inspect.signature(m.AceeInstallationExecutor.step).parameters)==("self","inputs","persist")
for name in ("STATUS_ADMISSIBLE","STATUS_REJECTED","REQUIRED_MANIFEST_FIELDS","REQUIRED_INVENTORY_TARGETS","ACCEPTED_ACEE5_SCHEMAS"):
 assert hasattr(m,name)
print("ACEE6_B1_PUBLIC_API_SNAPSHOT_OK")
