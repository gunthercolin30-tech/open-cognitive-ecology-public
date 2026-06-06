"""
tests/test_evolvability.py
"""

from ontology.evolvability import (
    Evolvability,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_constants():
    assert PRIMITIVE_NAME == "EVOLVABILITY"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = Evolvability()
    result = primitive.evaluate()

    assert abs(result["variation_generativity"] - 0.0) < 1e-12
    assert abs(result["viable_mutation_fraction"] - 0.0) < 1e-12
    assert abs(result["adaptive_accessibility"] - 0.0) < 1e-12
    assert abs(result["evolvability_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = Evolvability(
        variation_generativity=0.9,
        viable_mutation_fraction=0.6,
        adaptive_accessibility=0.3,
    )
    result = primitive.evaluate()

    expected = (0.9 + 0.6 + 0.3) / 3.0
    assert abs(result["evolvability_index"] - expected) < 1e-12


def test_negative_case():
    primitive = Evolvability(
        variation_generativity=-1.0,
        viable_mutation_fraction=-2.0,
        adaptive_accessibility=-3.0,
    )
    result = primitive.evaluate()

    assert abs(result["evolvability_index"] - 0.0) < 1e-12


def test_bounding():
    primitive = Evolvability(
        variation_generativity=2.0,
        viable_mutation_fraction=1.5,
        adaptive_accessibility=10.0,
    )
    result = primitive.evaluate()

    assert abs(result["variation_generativity"] - 1.0) < 1e-12
    assert abs(result["viable_mutation_fraction"] - 1.0) < 1e-12
    assert abs(result["adaptive_accessibility"] - 1.0) < 1e-12
    assert abs(result["evolvability_index"] - 1.0) < 1e-12


def test_step_matches_evaluate():
    primitive = Evolvability(0.7, 0.8, 0.9)

    result_eval = primitive.evaluate()
    result_step = primitive.step()

    assert abs(
        result_eval["evolvability_index"] - result_step["evolvability_index"]
    ) < 1e-12


def test_validate_matches_evaluate():
    primitive = Evolvability(0.2, 0.4, 0.6)

    result = primitive.evaluate()
    validation = primitive.validate()

    assert validation["is_valid"] is True
    assert abs(
        validation["evolvability_index"] - result["evolvability_index"]
    ) < 1e-12
