from ontology.adaptive_landscape import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    AdaptiveLandscape,
)


def test_metadata():
    assert PRIMITIVE_NAME == "ADAPTIVE_LANDSCAPE"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = AdaptiveLandscape()
    result = primitive.evaluate()

    assert abs(result["navigation_complexity"] - 0.5) < 1e-12
    assert abs(result["adaptive_potential"] - (1.0 / 6.0)) < 1e-12
    assert result["diagnostics"]["status"] == "flat"


def test_nominal_case():
    primitive = AdaptiveLandscape(
        landscape_ruggedness=0.6,
        peak_density=0.8,
        viability_connectivity=0.4,
    )
    result = primitive.evaluate()

    expected_navigation = 0.6
    expected_potential = (0.8 + 0.4 + 0.4) / 3.0

    assert abs(result["navigation_complexity"] - expected_navigation) < 1e-12
    assert abs(result["adaptive_potential"] - expected_potential) < 1e-12
    assert result["diagnostics"]["status"] == "structured"


def test_negative_inputs_are_clamped():
    primitive = AdaptiveLandscape(
        landscape_ruggedness=-1.0,
        peak_density=-1.0,
        viability_connectivity=-1.0,
    )
    result = primitive.evaluate()

    assert abs(result["navigation_complexity"] - 0.5) < 1e-12


def test_values_are_bounded():
    primitive = AdaptiveLandscape(
        landscape_ruggedness=10.0,
        peak_density=10.0,
        viability_connectivity=10.0,
    )
    result = primitive.evaluate()

    for key in (
        "landscape_ruggedness",
        "peak_density",
        "navigation_complexity",
        "adaptive_potential",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_matches_evaluate():
    primitive = AdaptiveLandscape(
        landscape_ruggedness=0.7,
        peak_density=0.5,
        viability_connectivity=0.9,
    )

    evaluate_result = primitive.evaluate()
    step_result = primitive.step()

    for key in (
        "landscape_ruggedness",
        "peak_density",
        "navigation_complexity",
        "adaptive_potential",
    ):
        assert abs(step_result[key] - evaluate_result[key]) < 1e-12


def test_validate_consistency():
    primitive = AdaptiveLandscape(
        landscape_ruggedness=0.3,
        peak_density=0.7,
        viability_connectivity=0.8,
    )

    evaluation = primitive.evaluate()
    validation = primitive.validate()

    assert validation["valid"] is True
    assert (
        abs(
            validation["adaptive_potential"]
            - evaluation["adaptive_potential"]
        )
        < 1e-12
    )
