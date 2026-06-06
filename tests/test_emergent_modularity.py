from ontology.emergent_modularity import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    EmergentModularity,
)


def test_metadata():
    assert PRIMITIVE_NAME == "EMERGENT_MODULARITY"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = EmergentModularity()
    result = primitive.evaluate()

    assert abs(result["modularity_strength"] - 0.0) < 1e-12
    assert result["diagnostics"]["status"] == "unstructured"


def test_nominal_case():
    primitive = EmergentModularity(
        functional_specialization=0.8,
        boundary_definition=0.6,
        inter_module_coordination=0.7,
    )
    result = primitive.evaluate()

    expected = (0.8 + 0.6 + 0.7) / 3.0

    assert abs(result["modularity_strength"] - expected) < 1e-12
    assert result["diagnostics"]["status"] == "modular"


def test_negative_inputs_are_clamped():
    primitive = EmergentModularity(
        functional_specialization=-1.0,
        boundary_definition=-2.0,
        inter_module_coordination=-3.0,
    )
    result = primitive.evaluate()

    assert abs(result["modularity_strength"] - 0.0) < 1e-12


def test_values_are_bounded():
    primitive = EmergentModularity(
        functional_specialization=10.0,
        boundary_definition=10.0,
        inter_module_coordination=10.0,
    )
    result = primitive.evaluate()

    for key in (
        "functional_specialization",
        "boundary_definition",
        "inter_module_coordination",
        "modularity_strength",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_matches_evaluate():
    primitive = EmergentModularity(
        functional_specialization=0.4,
        boundary_definition=0.5,
        inter_module_coordination=0.9,
    )

    evaluate_result = primitive.evaluate()
    step_result = primitive.step()

    for key in (
        "functional_specialization",
        "boundary_definition",
        "inter_module_coordination",
        "modularity_strength",
    ):
        assert abs(step_result[key] - evaluate_result[key]) < 1e-12


def test_validate_consistency():
    primitive = EmergentModularity(
        functional_specialization=0.7,
        boundary_definition=0.8,
        inter_module_coordination=0.6,
    )

    evaluation = primitive.evaluate()
    validation = primitive.validate()

    assert validation["valid"] is True
    assert (
        abs(
            validation["modularity_strength"]
            - evaluation["modularity_strength"]
        )
        < 1e-12
    )
