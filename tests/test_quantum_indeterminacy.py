from ontology.quantum_indeterminacy import (
    QuantumIndeterminacy,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_constants():
    assert PRIMITIVE_NAME == "QUANTUM_INDETERMINACY"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = QuantumIndeterminacy()
    result = primitive.evaluate(
        state_superposition=0.0,
        measurement_precision=1.0,
        information_access=1.0,
        predictive_horizon=1.0,
    )
    assert abs(result["indeterminacy_level"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = QuantumIndeterminacy()
    result = primitive.evaluate(
        state_superposition=1.0,
        measurement_precision=0.0,
        information_access=0.0,
        predictive_horizon=0.0,
    )
    assert abs(result["indeterminacy_level"] - 1.0) < 1e-12


def test_bounding():
    primitive = QuantumIndeterminacy()
    result = primitive.evaluate(
        state_superposition=2.0,
        measurement_precision=-1.0,
        information_access=3.0,
        predictive_horizon=5.0,
    )
    assert 0.0 <= result["indeterminacy_level"] <= 1.0
    assert 0.0 <= result["prediction_limit"] <= 1.0
    assert 0.0 <= result["knowledge_incompleteness"] <= 1.0
    assert 0.0 <= result["uncertainty_floor"] <= 1.0


def test_step_consistency():
    primitive = QuantumIndeterminacy()
    kwargs = dict(
        state_superposition=0.7,
        measurement_precision=0.6,
        information_access=0.8,
        predictive_horizon=0.5,
    )
    assert primitive.step(**kwargs) == primitive.evaluate(**kwargs)


def test_validate_consistency():
    primitive = QuantumIndeterminacy()
    kwargs = dict(
        state_superposition=0.4,
        measurement_precision=0.9,
        information_access=0.9,
        predictive_horizon=0.9,
    )
    validation = primitive.validate(**kwargs)
    assert validation["valid"] is True


def test_negative_case():
    primitive = QuantumIndeterminacy()
    result = primitive.evaluate(
        state_superposition=0.0,
        measurement_precision=1.0,
        information_access=1.0,
        predictive_horizon=1.0,
    )
    assert abs(result["uncertainty_floor"] - 0.0) < 1e-12
