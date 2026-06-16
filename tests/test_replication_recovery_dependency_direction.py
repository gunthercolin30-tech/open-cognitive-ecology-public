import ontology.civilizational_replication_engine as replication_module
from ontology.failure_recovery_orchestrator import (
    DEPENDENCIES as RECOVERY_DEPENDENCIES,
)


def test_replication_accepts_recovery_result_without_calling_recovery(
    monkeypatch,
    tmp_path,
):
    recovery_result = {
        "primitive": "failure_recovery_orchestrator",
        "success": True,
        "distributed_snapshot_recovery_index": 0.93,
        "snapshot_recovery_validated": True,
    }
    called_components = []

    monkeypatch.setattr(replication_module, "_ssd_continuity_root", lambda: None)
    engine = replication_module.CivilizationalReplicationEngine(root=tmp_path)

    def component_result(module_name, class_name, payload=None):
        called_components.append(module_name)
        return {"primitive": module_name, "success": True}

    monkeypatch.setattr(engine, "_call_component", component_result)

    result = engine.step({"recovery_result": recovery_result})

    assert "failure_recovery_orchestrator" not in replication_module.DEPENDENCIES
    assert "civilizational_replication_engine" in RECOVERY_DEPENDENCIES
    assert "failure_recovery_orchestrator" not in called_components
    assert (
        result["component_results"]["failure_recovery_orchestrator"]
        == recovery_result
    )
