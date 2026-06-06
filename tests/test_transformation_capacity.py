from ontology.transformation_capacity import (
    TransformationCapacity,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_constants():
    assert PRIMITIVE_NAME == "TRANSFORMATION_CAPACITY"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = TransformationCapacity()
    result = primitive.evaluate({})
    assert abs(result["transformation_capacity_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["primitive"] == PRIMITIVE_NAME


def test_nominal_case():
    primitive = TransformationCapacity()
    result = primitive.evaluate(
        {
            "structural_reconfiguration": 0.8,
            "institutional_innovation": 0.7,
            "goal_redefinition": 0.9,
        }
    )
    expected = (0.8 + 0.7 + 0.9) / 3.0
    assert abs(result["transformation_capacity_index"] - expected) < 1e-12
    assert result["diagnostics"]["status"] == "transformative"


def test_negative_case():
    primitive = TransformationCapacity()
    result = primitive.evaluate(
        {
            "structural_reconfiguration": 0.1,
            "institutional_innovation": 0.2,
            "goal_redefinition": 0.1,
        }
    )
    assert result["diagnostics"]["status"] == "path_dependent"


def test_bounding():
    primitive = TransformationCapacity()
    result = primitive.evaluate(
        {
            "structural_reconfiguration": 2.0,
            "institutional_innovation": -1.0,
            "goal_redefinition": 5.0,
        }
    )
    assert abs(result["structural_reconfiguration"] - 1.0) < 1e-12
    assert abs(result["institutional_innovation"] - 0.0) < 1e-12
    assert abs(result["goal_redefinition"] - 1.0) < 1e-12
    assert 0.0 <= result["transformation_capacity_index"] <= 1.0


def test_step_consistency():
    primitive = TransformationCapacity()
    inputs = {
        "structural_reconfiguration": 0.6,
        "institutional_innovation": 0.6,
        "goal_redefinition": 0.6,
    }
    assert primitive.step(inputs) == primitive.evaluate(inputs)


def test_validate_consistency():
    primitive = TransformationCapacity()
    inputs = {
        "structural_reconfiguration": 0.4,
        "institutional_innovation": 0.5,
        "goal_redefinition": 0.6,
    }
    evaluation = primitive.evaluate(inputs)
    validation = primitive.validate(inputs)
    assert validation["is_valid"] is True
    assert (
        abs(
            validation["transformation_capacity_index"]
            - evaluation["transformation_capacity_index"]
        )
        < 1e-12
    )
