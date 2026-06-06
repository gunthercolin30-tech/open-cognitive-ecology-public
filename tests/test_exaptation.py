from ontology.exaptation import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    Exaptation,
)


def test_metadata():
    assert PRIMITIVE_NAME == "EXAPTATION"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = Exaptation()
    result = primitive.evaluate()

    assert abs(result["exaptation_potential"] - 0.0) < 1e-12
    assert result["diagnostics"]["status"] == "specialized"


def test_nominal_case():
    primitive = Exaptation(
        functional_repurposing=0.8,
        latent_utility=0.6,
        cooption_probability=0.7,
    )
    result = primitive.evaluate()

    expected = (0.8 + 0.6 + 0.7) / 3.0

    assert abs(result["exaptation_potential"] - expected) < 1e-12
    assert result["diagnostics"]["status"] == "exaptive"


def test_negative_inputs_are_clamped():
    primitive = Exaptation(
        functional_repurposing=-1.0,
        latent_utility=-2.0,
        cooption_probability=-3.0,
    )
    result = primitive.evaluate()

    assert abs(result["exaptation_potential"] - 0.0) < 1e-12


def test_values_are_bounded():
    primitive = Exaptation(
        functional_repurposing=10.0,
        latent_utility=10.0,
        cooption_probability=10.0,
    )
    result = primitive.evaluate()

    for key in (
        "functional_repurposing",
        "latent_utility",
        "cooption_probability",
        "exaptation_potential",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_matches_evaluate():
    primitive = Exaptation(
        functional_repurposing=0.4,
        latent_utility=0.5,
        cooption_probability=0.9,
    )

    evaluate_result = primitive.evaluate()
    step_result = primitive.step()

    for key in (
        "functional_repurposing",
        "latent_utility",
        "cooption_probability",
        "exaptation_potential",
    ):
        assert abs(step_result[key] - evaluate_result[key]) < 1e-12


def test_validate_consistency():
    primitive = Exaptation(
        functional_repurposing=0.7,
        latent_utility=0.8,
        cooption_probability=0.6,
    )

    evaluation = primitive.evaluate()
    validation = primitive.validate()

    assert validation["valid"] is True
    assert (
        abs(
            validation["exaptation_potential"]
            - evaluation["exaptation_potential"]
        )
        < 1e-12
    )
