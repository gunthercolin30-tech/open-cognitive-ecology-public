from validation.ontology_organization import build_report


def test_all_ontology_modules_have_valid_logical_organization():
    report = build_report()

    assert report["summary"]["modules"] > 0
    assert report["parse_errors"] == []
    assert sum(
        report["summary"]["classification_confidence_counts"].values()
    ) == report["summary"]["modules"]
    assert sum(
        report["summary"]["unresolved_dependency_category_counts"].values()
    ) == report["summary"]["unresolved_dependency_references"]
    assert sum(
        report["summary"]["unresolved_dependency_source_counts"].values()
    ) == report["summary"]["unresolved_dependency_references"]
    assert (
        report["summary"]["unresolved_dependency_identifiers"]
        <= report["summary"]["unresolved_dependency_references"]
    )
    assert report["summary"]["confirmed_missing_component_identifiers"] == len({
        item["dependency"]
        for item in report["unresolved_dependencies"]
        if item["category"] == "missing_component"
    })
    assert report["summary"]["unresolved_dependency_source_counts"] == {
        "policy_decision": report["summary"]["unresolved_dependency_references"]
    }
    assert report["summary"]["classification_confidence_counts"].get(
        "review_required", 0
    ) == 0
    assert report["summary"]["hierarchical_level_mismatches"] == 0
    assert report["summary"]["internal_dependency_edges"] > 0
    assert len(report["dependency_topology"]["cycle_details"]) == (
        report["summary"]["dependency_cycles"]
    )
    assert all(
        "edge_candidates" in detail
        for detail in report["dependency_topology"]["cycle_details"]
    )
    assert all(
        len(detail["reciprocal_core_modules"])
        + len(detail["peripheral_modules"])
        == detail["size"]
        for detail in report["dependency_topology"]["cycle_details"]
    )
    assert report["summary"]["cycle_review_queue_entries"] == len(
        report["cycle_review_queue"]
    )
    assert report["summary"]["cycle_review_queue_entries"] == (
        report["summary"]["dependency_cycles"]
    )
    assert sum(
        report["summary"]["cycle_review_category_counts"].values()
    ) == report["summary"]["cycle_review_queue_entries"]
    assert sum(
        report["summary"]["cycle_review_priority_counts"].values()
    ) == report["summary"]["cycle_review_queue_entries"]
    assert sum(
        report["summary"]["cycle_review_decision_status_counts"].values()
    ) == report["summary"]["cycle_review_queue_entries"]
    assert all(
        cycle["cycle_decisions"] or cycle["subgraph_decisions"]
        for cycle in report["cycle_review_queue"]
        if cycle["decision_status"] == "approved"
    )
    assert all(
        len(decision["active_scope_modules"]) >= 2
        and set(decision["active_scope_modules"]).issubset(cycle["modules"])
        for cycle in report["cycle_review_queue"]
        for decision in cycle["subgraph_decisions"]
    )
    assert all(
        cycle["approved_theoretical_edge_removals"] > 0
        for cycle in report["cycle_review_queue"]
        if cycle["decision_status"] == "approved"
    )
    assert report["summary"]["residual_decision_queue_entries"] == len(
        report["residual_decision_queue"]
    )
    assert sum(
        report["summary"]["residual_decision_category_counts"].values()
    ) == report["summary"]["residual_decision_queue_entries"]
    assert sum(
        report["summary"]["residual_decision_priority_counts"].values()
    ) == report["summary"]["residual_decision_queue_entries"]
    assert sum(
        report["summary"]["semantic_review_severity_counts"].values()
    ) == report["summary"]["semantic_review_findings"]
    assert sum(report["summary"]["identity_source_counts"].values()) == (
        report["summary"]["modules"]
    )
    assert sum(
        report["summary"]["identity_binding_scope_counts"].values()
    ) == report["summary"]["identity_source_counts"].get("binding", 0)
    assert sum(
        report["summary"]["identity_normalization_priority_counts"].values()
    ) == report["summary"]["identity_normalization_candidates"]
    assert sum(
        report["summary"]["identity_normalization_category_counts"].values()
    ) == report["summary"]["identity_normalization_candidates"]
    assert report["summary"]["identity_normalization_candidates"] == (
        report["summary"]["semantic_review_type_counts"].get(
            "operational_module_without_primitive_identity", 0
        )
    )
    assert sum(
        report["summary"]["variant_authority_decision_counts"].values()
    ) == report["summary"]["variant_authority_families"]
    assert all(
        family["variants"]
        for family in report["variant_authority_families"]
    )
    assert all(
        family["reference_sources"]
        for family in report["variant_authority_families"]
        if family["decision"] == "active_variant_only"
    )
    assert report["summary"]["active_superseded_variants"] == len(
        report["active_superseded_variants"]
    )
    assert report["summary"]["variant_migration_queue_entries"] == len(
        report["variant_migration_queue"]
    )
    assert sum(
        report["summary"]["variant_migration_priority_counts"].values()
    ) == report["summary"]["variant_migration_queue_entries"]
    assert sum(
        report["summary"]["variant_migration_decision_status_counts"].values()
    ) == report["summary"]["variant_migration_queue_entries"]
    assert {
        item["variant"] for item in report["variant_migration_queue"]
    } == set(report["active_superseded_variants"])
    assert report["summary"]["legacy_only_variant_references"] == len(
        report["legacy_only_variant_references"]
    )
    assert report["validation_errors"] == []
