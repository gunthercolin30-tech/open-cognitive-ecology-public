from copy import deepcopy
from aw14_context import build_context
from ontology.ecological_certifier import EcologicalCertifier

certifier = EcologicalCertifier()
context = build_context()
first = certifier.step(inputs=context, persist=False)
second = certifier.step(inputs=context, persist=False)
assert first["certification_hash"] == second["certification_hash"]
changed = deepcopy(context)
changed["module_statuses"]["AW8_civilizational_memory_engine"] = "FAILED"
third = certifier.step(inputs=changed, persist=False)
assert third["ecology_complete"] is False
assert "AW8_civilizational_memory_engine" in third["missing_modules"]
assert third["certification_hash"] != first["certification_hash"]
print("AW14_FUNCTIONAL_OK")
