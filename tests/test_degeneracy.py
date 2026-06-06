"""
tests/test_degeneracy.py
"""

from ontology.degeneracy import (
    Degeneracy,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_constants():
    assert PRIMITIVE_NAME == "DEGENERACY"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = Degeneracy()
    result = primitive.evaluate()

    assert abs(result["structural_diversity"] - 0.0) < 1e-12
    assert abs(result["functional_overlap"] - 0.0) < 1e-12
    assert abs(result["substitutability"] - 0.0) < 1e-12
    assert abs(result["degeneracy_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = Degeneracy(
        structural_diversity=0.9,
        functional_overlap=0.6,
        substitutability=0.3,
    )
    result = primitive.evaluate()

    expected = (0.9 + 0.6 + 0.3) / 3.0
    assert abs(result["degeneracy_index"] - expected) < 1e-12


def test_negative_case():
    primitive = Degeneracy(
        structural_diversity=-1.0,
        functional_overlap=-2.0,
        substitutability=-3.0,
    )
    result = primitive.evaluate()

    assert abs(result["degeneracy_index"] - 0.0) < 1e-12


def test_bounding():
    primitive = Degeneracy(
        structural_diversity=2.0,
        functional_overlap=1.5,
        substitutability=10.0,
    )
    result = primitive.evaluate()

    assert abs(result["structural_diversity"] - 1.0) < 1e-12
    assert abs(result["functional_overlap"] - 1.0) < 1e-12
    assert abs(result["substitutability"] - 1.0) < 1e-12
    assert abs(result["degeneracy_index"] - 1.0) < 1e-12


def test_step_matches_evaluate():
    primitive = Degeneracy(0.7, 0.8, 0.9)

    result_eval = primitive.evaluate()
    result_step = primitive.step()

    assert abs(
        result_eval["degeneracy_index"] - result_step["degeneracy_index"]
    ) < 1e-12


def test_validate_matches_evaluate():
    primitive = Degeneracy(0.2, 0.4, 0.6)

    result = primitive.evaluate()
    validation = primitive.validate()

    assert validation["is_valid"] is True
    assert abs(
        validation["degeneracy_index"] - result["degeneracy_index"]
    ) < 1e-12
