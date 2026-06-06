from ontology.measurement_perturbation import (
    MeasurementPerturbation,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_constants():
    assert PRIMITIVE_NAME == "MEASUREMENT_PERTURBATION"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = MeasurementPerturbation()
    result = primitive.evaluate()
    assert abs(result["perturbation_level"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = MeasurementPerturbation()
    result = primitive.evaluate(
        measurement_intensity=1.0,
        observation_precision=1.0,
        system_sensitivity=1.0,
        interaction_strength=1.0,
    )
    assert abs(result["perturbation_level"] - 1.0) < 1e-12


def test_negative_case():
    primitive = MeasurementPerturbation()
    result = primitive.evaluate(
        measurement_intensity=0.0,
        observation_precision=0.0,
        system_sensitivity=0.0,
        interaction_strength=0.0,
    )
    assert abs(result["information_cost"] - 0.0) < 1e-12


def test_bounding():
    primitive = MeasurementPerturbation()
    result = primitive.evaluate(
        measurement_intensity=2.0,
        observation_precision=-1.0,
        system_sensitivity=3.0,
        interaction_strength=5.0,
    )
    assert 0.0 <= result["perturbation_level"] <= 1.0
    assert 0.0 <= result["information_cost"] <= 1.0
    assert 0.0 <= result["irreversibility"] <= 1.0
    assert 0.0 <= result["predictive_degradation"] <= 1.0


def test_step_consistency():
    primitive = MeasurementPerturbation()
    kwargs = dict(
        measurement_intensity=0.7,
        observation_precision=0.6,
        system_sensitivity=0.8,
        interaction_strength=0.5,
    )
    assert primitive.step(**kwargs) == primitive.evaluate(**kwargs)


def test_validate_consistency():
    primitive = MeasurementPerturbation()
    validation = primitive.validate(
        measurement_intensity=0.5,
        observation_precision=0.5,
        system_sensitivity=0.5,
        interaction_strength=0.5,
    )
    assert validation["valid"] is True
