from aw14_context import build_context
from ontology.ecological_certifier import EcologicalCertifier

result = EcologicalCertifier().step(inputs=build_context(), persist=False)
assert all(len(item["hash"]) == 64 for item in result["evidence_manifest"])
assert all(len(item["hash"]) == 64 for item in result["test_manifest"])
assert len({item["id"] for item in result["evidence_manifest"]}) == len(result["evidence_manifest"])
assert len({item["id"] for item in result["test_manifest"]}) == len(result["test_manifest"])
print("AW14_MANIFEST_INTEGRITY_OK")
