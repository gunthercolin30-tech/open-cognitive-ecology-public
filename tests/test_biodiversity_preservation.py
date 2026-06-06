from ontology.biodiversity_preservation import (
    BiodiversityPreservation,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_constants():
    assert PRIMITIVE_NAME == "BIODIVERSITY_PRESERVATION"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = BiodiversityPreservation()
    result = primitive.evaluate({})
    assert abs(result["biodiversity_preservation_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["primitive"] == PRIMITIVE_NAME


def test_nominal_case():
    primitive = BiodiversityPreservation()
    result = primitive.evaluate(
        {
            "species_diversity": 0.8,
            "habitat_integrity": 0.7,
            "conservation_effectiveness": 0.9,
        }
    )
    expected = (0.8 + 0.7 + 0.9) / 3.0
    assert abs(result["biodiversity_preservation_index"] - expected) < 1e-12
    assert result["diagnostics"]["status"] == "preserved"


def test_negative_case():
    primitive = BiodiversityPreservation()
    result = primitive.evaluate(
        {
            "species_diversity": 0.1,
            "habitat_integrity": 0.2,
            "conservation_effectiveness": 0.1,
        }
    )
    assert result["diagnostics"]["status"] == "degraded"


def test_bounding():
    primitive = BiodiversityPreservation()
    result = primitive.evaluate(
        {
            "species_diversity": 2.0,
            "habitat_integrity": -1.0,
            "conservation_effectiveness": 5.0,
        }
    )
    assert abs(result["species_diversity"] - 1.0) < 1e-12
    assert abs(result["habitat_integrity"] - 0.0) < 1e-12
    assert abs(result["conservation_effectiveness"] - 1.0) < 1e-12
    assert 0.0 <= result["biodiversity_preservation_index"] <= 1.0


def test_step_consistency():
    primitive = BiodiversityPreservation()
    inputs = {
        "species_diversity": 0.6,
        "habitat_integrity": 0.6,
        "conservation_effectiveness": 0.6,
    }
    assert primitive.step(inputs) == primitive.evaluate(inputs)


def test_validate_consistency():
    primitive = BiodiversityPreservation()
    inputs = {
        "species_diversity": 0.4,
        "habitat_integrity": 0.5,
        "conservation_effectiveness": 0.6,
    }
    evaluation = primitive.evaluate(inputs)
    validation = primitive.validate(inputs)
    assert validation["is_valid"] is True
    assert (
        abs(
            validation["biodiversity_preservation_index"]
            - evaluation["biodiversity_preservation_index"]
        )
        < 1e-12
    )
