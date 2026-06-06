from ontology.problem_solving import (
    MATURITY_LEVEL,
    PRIMITIVE_NAME,
    ProblemSolving,
)


def test_constants():
    assert PRIMITIVE_NAME == "PROBLEM_SOLVING"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = ProblemSolving()
    result = primitive.evaluate()

    assert abs(result["problem_structuring"] - 0.0) < 1e-12
    assert abs(result["solution_search"] - 0.0) < 1e-12
    assert abs(result["resolution_effectiveness"] - 0.0) < 1e-12
    assert abs(result["problem_solving_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = ProblemSolving()
    result = primitive.evaluate(
        structuring_signals=[1.0, 0.8],
        search_signals=[1.0, 0.9],
        resolution_signals=[0.7, 1.0],
    )

    assert result["problem_solving_index"] > 0.0
    assert result["diagnostics"]["status"] == "nominal"


def test_negative_case():
    primitive = ProblemSolving()
    result = primitive.evaluate(
        structuring_signals=[0.0],
        search_signals=[0.0],
        resolution_signals=[0.0],
    )

    assert abs(result["problem_solving_index"] - 0.0) < 1e-12


def test_bounded_values():
    primitive = ProblemSolving()
    result = primitive.evaluate(
        structuring_signals=[10.0, -5.0],
        search_signals=[2.0],
        resolution_signals=[3.0],
    )

    for key in (
        "problem_structuring",
        "solution_search",
        "resolution_effectiveness",
        "problem_solving_index",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_matches_evaluate():
    primitive = ProblemSolving()
    kwargs = {
        "structuring_signals": [1.0, 0.5],
        "search_signals": [1.0],
        "resolution_signals": [0.75],
    }

    evaluation = primitive.evaluate(**kwargs)
    stepped = primitive.step(**kwargs)

    assert abs(
        stepped["problem_solving_index"]
        - evaluation["problem_solving_index"]
    ) < 1e-12


def test_validate_matches_evaluate():
    primitive = ProblemSolving()
    kwargs = {
        "structuring_signals": [1.0, 0.5],
        "search_signals": [1.0],
        "resolution_signals": [0.75],
    }

    evaluation = primitive.evaluate(**kwargs)
    validation = primitive.validate(**kwargs)

    assert validation["is_valid"] is True
    assert abs(
        validation["problem_solving_index"]
        - evaluation["problem_solving_index"]
    ) < 1e-12
