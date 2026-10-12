from __future__ import annotations

import copy
import py_compile
import tempfile
from pathlib import Path

from ontology.comparative_dashboard import ComparativeDashboard
from ontology.comparative_history import ComparativeHistory

ROOT = Path.home() / "open-cognitive-ecology"


def main() -> None:
    for path in [
        ROOT / "ontology/comparative_history.py",
        ROOT / "au9_fast_acceptance_suite.py",
        ROOT / "comparative_history_final_lock.py",
    ]:
        py_compile.compile(str(path), cfile=str(Path("/private/tmp") / (path.name + ".pyc")), doraise=True)

    dashboard = ComparativeDashboard().step(inputs={}, persist=False)
    with tempfile.TemporaryDirectory(prefix="oce_au9_") as tmp:
        history = ComparativeHistory(root=Path(tmp))

        first = history.step(inputs={"comparative_dashboard": dashboard}, persist=True)
        assert first["comparative_history_status"] == "COMPARATIVE_HISTORY_READY"
        assert first["persisted"] is True
        assert first["history_count_before"] == 0
        assert first["history_count_after"] == 1
        assert first["change_set"]["change_type"] == "INITIAL_SNAPSHOT"
        assert first["chain_integrity"]["chain_valid"] is True

        unchanged = history.step(inputs={"comparative_dashboard": dashboard}, persist=True)
        assert unchanged["comparative_history_status"] == "COMPARATIVE_HISTORY_READY"
        assert unchanged["change_set"]["change_type"] == "NO_CHANGE"
        assert unchanged["append_required"] is False
        assert unchanged["history_count_before"] == 1
        assert unchanged["history_count_after"] == 1

        changed_dashboard = copy.deepcopy(dashboard)
        changed_dashboard["architecture_registry"].append({
            "architecture_id": "AU9_NEW_ARCHITECTURE",
            "display_name": "AU9 new architecture",
        })
        changed_dashboard["dashboard_hash"] = "a" * 64
        changed = history.step(inputs={"comparative_dashboard": changed_dashboard}, persist=True)
        assert changed["change_set"]["change_type"] == "COMPARATIVE_STATE_CHANGED"
        assert "AU9_NEW_ARCHITECTURE" in changed["change_set"]["added_architectures"]
        assert changed["history_count_after"] == 2
        assert changed["chain_integrity"]["chain_valid"] is True
        assert changed["record"]["previous_record_hash"] == first["record_hash"]

        profile_dashboard = copy.deepcopy(changed_dashboard)
        profile_dashboard["rf_profiles"][0]["profile_confidence"] = 0.123456
        profile_dashboard["dashboard_hash"] = "b" * 64
        profile_change = history.step(inputs={"comparative_dashboard": profile_dashboard}, persist=False)
        assert profile_change["change_set"]["profiles_changed"] is True
        assert profile_change["persisted"] is False

        cluster_dashboard = copy.deepcopy(changed_dashboard)
        cluster_dashboard["cluster_assignments"]["AU9_NEW_ARCHITECTURE"] = "cluster_999"
        cluster_dashboard["dashboard_hash"] = "c" * 64
        cluster_change = history.step(inputs={"comparative_dashboard": cluster_dashboard}, persist=False)
        assert cluster_change["change_set"]["clusters_changed"] is True

        taxonomy_dashboard = copy.deepcopy(changed_dashboard)
        taxonomy_dashboard["taxonomy_hash"] = "d" * 64
        taxonomy_dashboard["dashboard_hash"] = "e" * 64
        taxonomy_change = history.step(inputs={"comparative_dashboard": taxonomy_dashboard}, persist=False)
        assert taxonomy_change["change_set"]["taxonomy_changed"] is True

        degraded = history.step(inputs={"comparative_dashboard": {
            "comparative_dashboard_status": "COMPARATIVE_DASHBOARD_INCOMPLETE",
            "comparative_dashboard_ready": False,
        }}, persist=False)
        assert degraded["comparative_history_status"] == "COMPARATIVE_HISTORY_INCOMPLETE"
        assert degraded["comparative_history_ready"] is False
        assert degraded["persisted"] is False

        for payload in [first, unchanged, changed, profile_change, cluster_change, taxonomy_change, degraded]:
            assert payload["functional_conclusion_only"] is True
            assert payload["phenomenology_undetermined"] is True
            assert payload["consciousness_proven"] is False
            assert payload["qualia_proven"] is False
            assert payload["subjectivity_proven"] is False
            assert payload["phenomenology_proven"] is False

    print("AU9_FAST_ACCEPTANCE_OK")


if __name__ == "__main__":
    main()
