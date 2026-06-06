"""
tests/test_robustness.py
"""

from ontology.robustness import (
    Robustness,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_constants():
    assert PRIMITIVE_NAME == "ROBUSTNESS"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = Robustness()
    result = primitive.evaluate()

    assert abs(result["perturbation_tolerance"] - 0.0) < 1e-12
    assert abs(result["functional_stability"] - 0.0) < 1e-12
    assert abs(result["viability_preservation"] - 0.0) < 1e-12
    assert abs(result["robustness_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = Robustness(
        perturbation_tolerance=0.9,
        functional_stability=0.6,
        viability_preservation=0.3,
    )
    result = primitive.evaluate()

    expected = (0.9 + 0.6 + 0.3) / 3.0
    assert abs(result["robustness_index"] - expected) < 1e-12


def test_negative_case():
    primitive = Robustness(
        perturbation_tolerance=-1.0,
        functional_stability=-2.0,
        viability_preservation=-3.0,
    )
    result = primitive.evaluate()

    assert abs(result["robustness_index"] - 0.0) < 1e-12


def test_bounding():
    primitive = Robustness(
        perturbation_tolerance=2.0,
        functional_stability=1.5,
        viability_preservation=10.0,
    )
    result = primitive.evaluate()

    assert abs(result["perturbation_tolerance"] - 1.0) < 1e-12
    assert abs(result["functional_stability"] - 1.0) < 1e-12
    assert abs(result["viability_preservation"] - 1.0) < 1e-12
    assert abs(result["robustness_index"] - 1.0) < 1e-12


def test_step_matches_evaluate():
    primitive = Robustness(0.7, 0.8, 0.9)

    result_eval = primitive.evaluate()
    result_step = primitive.step()

    assert abs(
        result_eval["robustness_index"] - result_step["robustness_index"]
    ) < 1e-12


def test_validate_matches_evaluate():
    primitive = Robustness(0.2, 0.4, 0.6)

    result = primitive.evaluate()
    validation = primitive.validate()

    assert validation["is_valid"] is True
    assert abs(
        validation["robustness_index"] - result["robustness_index"]
    ) < 1e-12
