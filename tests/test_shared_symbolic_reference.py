from ontology.shared_symbolic_reference import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    SharedSymbolicReference,
)


def test_metadata():
    assert PRIMITIVE_NAME == "SHARED_SYMBOLIC_REFERENCE"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = SharedSymbolicReference()
    result = primitive.evaluate({})
    assert abs(result["shared_symbolic_reference_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["primitive"] == PRIMITIVE_NAME


def test_nominal_case():
    primitive = SharedSymbolicReference()
    state = {
        "usage_convergence": 0.8,
        "sign_consistency": 0.6,
        "referential_agreement": 0.9,
        "semantic_persistence": 0.7,
    }

    result = primitive.evaluate(state)

    expected_conventionalization = 0.7
    expected_index = (0.7 + 0.9 + 0.7) / 3.0

    assert abs(
        result["symbol_conventionalization"]
        - expected_conventionalization
    ) < 1e-12
    assert abs(result["reference_consensus"] - 0.9) < 1e-12
    assert abs(result["semantic_stability"] - 0.7) < 1e-12
    assert abs(
        result["shared_symbolic_reference_index"]
        - expected_index
    ) < 1e-12


def test_negative_case():
    primitive = SharedSymbolicReference()
    state = {
        "usage_convergence": 0.1,
        "sign_consistency": 0.0,
        "referential_agreement": 0.1,
        "semantic_persistence": 0.0,
    }

    result = primitive.evaluate(state)
    assert result["shared_symbolic_reference_index"] < 0.5


def test_bounding():
    primitive = SharedSymbolicReference()
    state = {
        "usage_convergence": 5.0,
        "sign_consistency": -2.0,
        "referential_agreement": 10.0,
        "semantic_persistence": -1.0,
    }

    result = primitive.evaluate(state)

    for key in (
        "symbol_conventionalization",
        "reference_consensus",
        "semantic_stability",
        "shared_symbolic_reference_index",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_consistency():
    primitive = SharedSymbolicReference()
    state = {
        "usage_convergence": 0.7,
        "sign_consistency": 0.8,
        "referential_agreement": 0.6,
        "semantic_persistence": 0.9,
    }

    evaluate_result = primitive.evaluate(state)
    step_result = primitive.step(state)

    assert abs(
        evaluate_result["shared_symbolic_reference_index"]
        - step_result["shared_symbolic_reference_index"]
    ) < 1e-12


def test_validate_consistency():
    primitive = SharedSymbolicReference()
    state = {
        "usage_convergence": 0.9,
        "sign_consistency": 0.9,
        "referential_agreement": 0.9,
        "semantic_persistence": 0.9,
    }

    evaluate_result = primitive.evaluate(state)
    validate_result = primitive.validate(state)

    assert abs(
        evaluate_result["shared_symbolic_reference_index"]
        - validate_result["value"]
    ) < 1e-12
    assert validate_result["is_valid"] is True
