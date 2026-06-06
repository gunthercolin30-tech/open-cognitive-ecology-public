from ontology.ecosystem_services import (
    EcosystemServices,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_constants():
    assert PRIMITIVE_NAME == "ECOSYSTEM_SERVICES"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = EcosystemServices()
    result = primitive.evaluate({})
    assert abs(result["ecosystem_services_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["primitive"] == PRIMITIVE_NAME


def test_nominal_case():
    primitive = EcosystemServices()
    result = primitive.evaluate(
        {
            "provisioning_services": 0.8,
            "regulating_services": 0.7,
            "supporting_services": 0.9,
        }
    )
    expected = (0.8 + 0.7 + 0.9) / 3.0
    assert abs(result["ecosystem_services_index"] - expected) < 1e-12
    assert result["diagnostics"]["status"] == "sustained"


def test_negative_case():
    primitive = EcosystemServices()
    result = primitive.evaluate(
        {
            "provisioning_services": 0.1,
            "regulating_services": 0.2,
            "supporting_services": 0.1,
        }
    )
    assert result["diagnostics"]["status"] == "degraded"


def test_bounding():
    primitive = EcosystemServices()
    result = primitive.evaluate(
        {
            "provisioning_services": 2.0,
            "regulating_services": -1.0,
            "supporting_services": 5.0,
        }
    )
    assert abs(result["provisioning_services"] - 1.0) < 1e-12
    assert abs(result["regulating_services"] - 0.0) < 1e-12
    assert abs(result["supporting_services"] - 1.0) < 1e-12
    assert 0.0 <= result["ecosystem_services_index"] <= 1.0


def test_step_consistency():
    primitive = EcosystemServices()
    inputs = {
        "provisioning_services": 0.6,
        "regulating_services": 0.6,
        "supporting_services": 0.6,
    }
    assert primitive.step(inputs) == primitive.evaluate(inputs)


def test_validate_consistency():
    primitive = EcosystemServices()
    inputs = {
        "provisioning_services": 0.4,
        "regulating_services": 0.5,
        "supporting_services": 0.6,
    }
    evaluation = primitive.evaluate(inputs)
    validation = primitive.validate(inputs)
    assert validation["is_valid"] is True
    assert (
        abs(
            validation["ecosystem_services_index"]
            - evaluation["ecosystem_services_index"]
        )
        < 1e-12
    )
