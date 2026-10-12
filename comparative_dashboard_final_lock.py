from ontology.comparative_dashboard import ComparativeDashboard

READY_OR_SYNTHETIC_CONTEXT = {}


def main():
    result = ComparativeDashboard().step(inputs=READY_OR_SYNTHETIC_CONTEXT, persist=False)
    assert result["step"] == "AU8"
    assert result["comparative_dashboard_status"] == "COMPARATIVE_DASHBOARD_READY"
    assert result["comparative_dashboard_ready"] is True
    assert result["dependencies_ready"] is True
    assert result["dashboard_summary"]["architecture_count"] >= 2
    assert result["dashboard_summary"]["comparability_ready"] is True
    assert result["dashboard_summary"]["auditability_ready"] is True
    assert result["export_integrity"]["json_valid"] is True
    assert result["export_integrity"]["markdown_nonempty"] is True
    assert result["export_integrity"]["html_document_valid"] is True
    assert len(result["dashboard_hash"]) == 64
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False
    print("AU8_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
