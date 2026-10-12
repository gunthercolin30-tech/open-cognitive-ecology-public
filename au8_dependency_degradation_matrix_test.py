from ontology.comparative_dashboard import ComparativeDashboard


EXPECTED = {
    "comparative_blueprint": (
        "COMPARATIVE_BLUEPRINT_READY"
    ),
    "architecture_registry": (
        "ARCHITECTURE_REGISTRY_READY"
    ),
    "unified_measurement_protocol": (
        "UNIFIED_MEASUREMENT_PROTOCOL_READY"
    ),
    "rf_profile_builder": (
        "RF_PROFILE_BUILDER_READY"
    ),
    "comparative_similarity_engine": (
        "COMPARATIVE_SIMILARITY_ENGINE_READY"
    ),
    "consciousness_distance_metric": (
        "CONSCIOUSNESS_DISTANCE_METRIC_READY"
    ),
    "clustering_engine": (
        "CLUSTERING_ENGINE_READY"
    ),
    "taxonomy_builder": (
        "TAXONOMY_BUILDER_READY"
    ),
}


def status_key(module_name):
    return f"{module_name}_status"


def main():
    dashboard = ComparativeDashboard()

    for degraded_module in EXPECTED:
        context = {}

        for module_name, expected_status in EXPECTED.items():
            context[module_name] = {
                status_key(module_name): (
                    "DEGRADED"
                    if module_name == degraded_module
                    else expected_status
                )
            }

        result = dashboard.step(
            inputs=context,
            persist=False,
        )

        assert result["dependencies_ready"] is False
        assert result["comparative_dashboard_ready"] is False
        assert result["comparative_dashboard_status"] == (
            "COMPARATIVE_DASHBOARD_INCOMPLETE"
        )

        assert result["module_statuses"][
            degraded_module
        ] == "DEGRADED"

        assert result["functional_conclusion_only"] is True
        assert result["phenomenology_undetermined"] is True

    print("AU8_DEPENDENCY_DEGRADATION_MATRIX_OK")


if __name__ == "__main__":
    main()
