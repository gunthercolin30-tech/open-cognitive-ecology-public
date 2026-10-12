from pathlib import Path
import json
import py_compile
import tempfile

from ontology.comparative_dashboard import ComparativeDashboard

ROOT = Path.home() / "open-cognitive-ecology"


def main():
    for path in [ROOT / "ontology/comparative_dashboard.py", ROOT / "au8_fast_acceptance_suite.py", ROOT / "comparative_dashboard_final_lock.py"]:
        py_compile.compile(str(path), cfile=f"/private/tmp/{path.name}.pyc", doraise=True)

    result = ComparativeDashboard().step(inputs={}, persist=False)
    assert result["step"] == "AU8"
    assert result["comparative_dashboard_status"] == "COMPARATIVE_DASHBOARD_READY"
    assert result["comparative_dashboard_ready"] is True
    assert result["dependencies_ready"] is True
    assert result["dashboard_summary"]["architecture_count"] >= 2
    assert result["dashboard_summary"]["profile_count"] >= 2
    assert result["export_integrity"] == {"json_valid": True, "markdown_nonempty": True, "html_document_valid": True}
    assert json.loads(result["exports"]["json"])["dashboard_hash"] == result["dashboard_hash"]
    assert "<!doctype html>" in result["exports"]["html"]
    assert "# AU8 Comparative RF Dashboard" in result["exports"]["markdown"]

    repeated = ComparativeDashboard().step(inputs={}, persist=False)
    assert repeated["dashboard_hash"] == result["dashboard_hash"]
    assert repeated["dashboard_summary"] == result["dashboard_summary"]

    persisted = ComparativeDashboard().step(inputs={}, persist=True)
    assert persisted["dashboard_hash"] == result["dashboard_hash"]
    assert persisted["persist_requested"] is True
    assert persisted["persisted"] is True
    assert persisted["output_paths"]

    degraded = ComparativeDashboard().step(inputs={"taxonomy_builder": {"taxonomy_builder_status": "TAXONOMY_BUILDER_INCOMPLETE"}}, persist=False)
    assert degraded["comparative_dashboard_ready"] is False
    assert degraded["comparative_dashboard_status"] == "COMPARATIVE_DASHBOARD_INCOMPLETE"

    for payload in (result, degraded):
        assert payload["functional_conclusion_only"] is True
        assert payload["phenomenology_undetermined"] is True
        assert payload["consciousness_proven"] is False
        assert payload["qualia_proven"] is False
        assert payload["subjectivity_proven"] is False
        assert payload["phenomenology_proven"] is False

    print("AU8_FAST_ACCEPTANCE_OK")


if __name__ == "__main__":
    main()
