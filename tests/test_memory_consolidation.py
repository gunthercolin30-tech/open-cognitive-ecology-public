from ontology.memory_consolidation import (
    MATURITY_LEVEL,
    PRIMITIVE_NAME,
    MemoryConsolidation,
)


def test_constants():
    assert PRIMITIVE_NAME == "MEMORY_CONSOLIDATION"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = MemoryConsolidation()
    result = primitive.evaluate()

    assert abs(result["retention_stability"] - 0.0) < 1e-12
    assert abs(result["integration_consistency"] - 0.0) < 1e-12
    assert abs(result["long_term_persistence"] - 0.0) < 1e-12
    assert abs(result["memory_consolidation_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = MemoryConsolidation()
    result = primitive.evaluate(
        retained_patterns=[1.0, 0.8],
        consistency_signals=[1.0, 0.9],
        persistence_signals=[0.7, 1.0],
    )

    assert result["memory_consolidation_index"] > 0.0
    assert result["diagnostics"]["status"] == "nominal"


def test_negative_case():
    primitive = MemoryConsolidation()
    result = primitive.evaluate(
        retained_patterns=[0.0],
        consistency_signals=[0.0],
        persistence_signals=[0.0],
    )

    assert abs(result["memory_consolidation_index"] - 0.0) < 1e-12


def test_bounded_values():
    primitive = MemoryConsolidation()
    result = primitive.evaluate(
        retained_patterns=[10.0, -5.0],
        consistency_signals=[2.0],
        persistence_signals=[3.0],
    )

    for key in (
        "retention_stability",
        "integration_consistency",
        "long_term_persistence",
        "memory_consolidation_index",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_matches_evaluate():
    primitive = MemoryConsolidation()
    kwargs = {
        "retained_patterns": [1.0, 0.5],
        "consistency_signals": [1.0],
        "persistence_signals": [0.75],
    }

    evaluation = primitive.evaluate(**kwargs)
    stepped = primitive.step(**kwargs)

    assert (
        abs(
            stepped["memory_consolidation_index"]
            - evaluation["memory_consolidation_index"]
        )
        < 1e-12
    )


def test_validate_matches_evaluate():
    primitive = MemoryConsolidation()
    kwargs = {
        "retained_patterns": [1.0, 0.5],
        "consistency_signals": [1.0],
        "persistence_signals": [0.75],
    }

    evaluation = primitive.evaluate(**kwargs)
    validation = primitive.validate(**kwargs)

    assert validation["is_valid"] is True
    assert (
        abs(
            validation["memory_consolidation_index"]
            - evaluation["memory_consolidation_index"]
        )
        < 1e-12
    )
