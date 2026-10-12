from aw14_context import build_context
from ontology.ecological_certifier import EcologicalCertifier

result = EcologicalCertifier().step(inputs=build_context(), persist=False)
required = {
    "certification_status", "certified_modules", "module_statuses",
    "evidence_manifest", "test_manifest", "functional_conclusion",
    "limitations", "allowed_claims", "blocked_claims", "certification_hash",
}
assert required <= set(result)
assert tuple(result["module_statuses"]) == EcologicalCertifier.REQUIRED_MODULES
print("AW14_NON_REGRESSION_OK")
