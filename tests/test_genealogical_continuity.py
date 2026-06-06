from ontology.genealogical_continuity import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    GenealogicalContinuity,
)


def test_metadata():
    assert PRIMITIVE_NAME == "GENEALOGICAL_CONTINUITY"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = GenealogicalContinuity()
    result = primitive.evaluate()

    expected = 1.0 / 3.0
    assert abs(result["lineage_integrity"] - expected) < 1e-12
    assert abs(result["continuity_strength"] - expected) < 1e-12
    assert result["diagnostics"]["status"] == "continuous"


def test_nominal_case():
    primitive = GenealogicalContinuity(
        inheritance_fidelity=0.9,
        cumulative_divergence=0.3,
        succession_stability=0.8,
    )
    result = primitive.evaluate()

    expected = (0.9 + 0.7 + 0.8) / 3.0
    assert abs(result["lineage_integrity"] - expected) < 1e-12
    assert abs(result["continuity_strength"] - expected) < 1e-12


def test_negative_inputs_are_clamped():
    primitive = GenealogicalContinuity(
        inheritance_fidelity=-1.0,
        cumulative_divergence=-1.0,
        succession_stability=-1.0,
    )
    result = primitive.evaluate()

    expected = (0.0 + 1.0 + 0.0) / 3.0
    assert abs(result["lineage_integrity"] - expected) < 1e-12


def test_values_are_bounded():
    primitive = GenealogicalContinuity(
        inheritance_fidelity=10.0,
        cumulative_divergence=10.0,
        succession_stability=10.0,
    )
    result = primitive.evaluate()

    for key in (
        "lineage_integrity",
        "inheritance_fidelity",
        "cumulative_divergence",
        "continuity_strength",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_matches_evaluate():
    primitive = GenealogicalContinuity(
        inheritance_fidelity=0.5,
        cumulative_divergence=0.2,
        succession_stability=0.7,
    )
    evaluate_result = primitive.evaluate()
    step_result = primitive.step()

    for key in (
        "lineage_integrity",
        "inheritance_fidelity",
        "cumulative_divergence",
        "continuity_strength",
    ):
        assert abs(step_result[key] - evaluate_result[key]) < 1e-12


def test_validate_consistency():
    primitive = GenealogicalContinuity(
        inheritance_fidelity=0.8,
        cumulative_divergence=0.4,
        succession_stability=0.9,
    )
    evaluation = primitive.evaluate()
    validation = primitive.validate()

    assert validation["valid"] is True
    assert (
        abs(
            validation["continuity_strength"]
            - evaluation["continuity_strength"]
        )
        < 1e-12
    )
