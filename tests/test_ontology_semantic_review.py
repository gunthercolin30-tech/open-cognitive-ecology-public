from validation.ontology_organization import build_report


def test_physical_deployment_planner_has_stable_operational_identity():
    report = build_report()

    planner = next(
        item
        for item in report["modules"]
        if item["module"] == "autonomous_physical_deployment_planner"
    )

    assert planner["identity"] == "autonomous_physical_deployment_planner"
    assert planner["identity_source"] == "module_primitive"
    assert all(
        item["module"] != "autonomous_physical_deployment_planner"
        for item in report["identity_normalization"]
    )


def test_effectful_modules_have_explicit_operational_roles_or_boundary():
    report = build_report()
    modules = {item["module"]: item for item in report["modules"]}

    assert modules["embodied_continuity_preservation"]["role"] == "runtime"
    assert (
        modules["embodied_continuity_preservation"]["identity_source"]
        == "module_primitive"
    )
    assert (
        modules["environmental_grounding_longitudinal_observatory"]["role"]
        == "observability"
    )
    assert modules["multi_site_physical_ecology"]["role"] == "runtime"
    assert report["semantic_review"] == []
