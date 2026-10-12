import importlib
import inspect

module = importlib.import_module("ontology.specialization_engine")

assert module.__name__ == "ontology.specialization_engine"
assert hasattr(module, "SpecializationEngine")

cls = module.SpecializationEngine
assert inspect.isclass(cls)

result = cls().step(
    inputs={
        "maturation_result": {
            "maturation_complete": True,
            "maturation_status": "FUNCTIONAL_MATURATION_COMPLETE",
        },
        "observations": [
            {
                "timestamp_utc": "2026-08-01T00:00:00Z",
                "functional_profile": {
                    "reasoning": 0.78,
                    "memory": 0.10,
                    "governance": 0.07,
                    "exploration": 0.05,
                },
                "diversity": 0.45,
                "resource_cost": 0.35,
                "reversibility": 0.80,
                "openness": 0.88,
                "data_quality": 0.98,
            },
            {
                "timestamp_utc": "2026-08-02T00:00:00Z",
                "functional_profile": {
                    "reasoning": 0.82,
                    "memory": 0.08,
                    "governance": 0.06,
                    "exploration": 0.04,
                },
                "diversity": 0.42,
                "resource_cost": 0.37,
                "reversibility": 0.78,
                "openness": 0.86,
                "data_quality": 0.98,
            },
            {
                "timestamp_utc": "2026-08-03T00:00:00Z",
                "functional_profile": {
                    "reasoning": 0.84,
                    "memory": 0.07,
                    "governance": 0.05,
                    "exploration": 0.04,
                },
                "diversity": 0.40,
                "resource_cost": 0.39,
                "reversibility": 0.76,
                "openness": 0.85,
                "data_quality": 0.98,
            },
        ],
    },
    persist=False,
)

assert result["primitive"] == "SPECIALIZATION_ENGINE"
assert result["step"] == "AV3"
assert isinstance(result["specialization_strength"], float)
assert isinstance(result["closure_pressure"], float)
assert result["specialization_hash"]

print("AV3_EXACT_MODULE_OK")
