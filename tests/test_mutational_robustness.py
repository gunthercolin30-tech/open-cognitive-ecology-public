"""
tests/test_mutational_robustness.py
"""

from ontology.mutational_robustness import (
    MutationalRobustness,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_constants():
    assert PRIMITIVE_NAME == "MUTATIONAL_ROBUSTNESS"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = MutationalRobustness()
    result = primitive.evaluate()

    assert abs(result["mutation_tolerance"] - 0.0) < 1e-12
    assert abs(result["fitness_preservation"] - 0.0) < 1e-12
    assert abs(result["structural_resilience"] - 0.0) < 1e-12
    assert abs(result["mutational_robustness_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = MutationalRobustness(
        mutation_tolerance=0.9,
        fitness_preservation=0.6,
        structural_resilience=0.3,
    )
    result = primitive.evaluate()

    expected = (0.9 + 0.6 + 0.3) / 3.0
    assert abs(result["mutational_robustness_index"] - expected) < 1e-12


def test_negative_case():
    primitive = MutationalRobustness(
        mutation_tolerance=-1.0,
        fitness_preservation=-2.0,
        structural_resilience=-3.0,
    )
    result = primitive.evaluate()

    assert abs(result["mutational_robustness_index"] - 0.0) < 1e-12


def test_bounding():
    primitive = MutationalRobustness(
        mutation_tolerance=2.0,
        fitness_preservation=1.5,
        structural_resilience=10.0,
    )
    result = primitive.evaluate()

    assert abs(result["mutation_tolerance"] - 1.0) < 1e-12
    assert abs(result["fitness_preservation"] - 1.0) < 1e-12
    assert abs(result["structural_resilience"] - 1.0) < 1e-12
    assert abs(result["mutational_robustness_index"] - 1.0) < 1e-12


def test_step_matches_evaluate():
    primitive = MutationalRobustness(0.7, 0.8, 0.9)

    result_eval = primitive.evaluate()
    result_step = primitive.step()

    assert abs(
        result_eval["mutational_robustness_index"]
        - result_step["mutational_robustness_index"]
    ) < 1e-12


def test_validate_matches_evaluate():
    primitive = MutationalRobustness(0.2, 0.4, 0.6)

    result = primitive.evaluate()
    validation = primitive.validate()

    assert validation["is_valid"] is True
    assert abs(
        validation["mutational_robustness_index"]
        - result["mutational_robustness_index"]
    ) < 1e-12
