import inspect

from ontology.cooperative_specialization_engine import (
    CooperativeSpecializationEngine,
)
from ontology.specialization_engine import SpecializationEngine


assert CooperativeSpecializationEngine is not SpecializationEngine

cooperative_signature = inspect.signature(
    CooperativeSpecializationEngine.step
)
developmental_signature = inspect.signature(
    SpecializationEngine.step
)

assert "inputs" in developmental_signature.parameters
assert "persist" in developmental_signature.parameters

developmental_result = SpecializationEngine().step(
    inputs={},
    persist=False,
)

assert developmental_result["primitive"] == "SPECIALIZATION_ENGINE"
assert developmental_result["step"] == "AV3"
assert "specialization_strength" in developmental_result
assert "closure_pressure" in developmental_result
assert "specialization_hash" in developmental_result

print("AV3_COOPERATIVE_NON_REDUNDANCY_OK")
print("cooperative_signature =", cooperative_signature)
print("developmental_signature =", developmental_signature)
