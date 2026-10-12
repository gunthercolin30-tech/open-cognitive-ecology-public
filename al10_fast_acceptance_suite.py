#!/usr/bin/env python3
from __future__ import annotations
import py_compile
from pathlib import Path
ROOT = Path.home() / "open-cognitive-ecology"
MODULE = ROOT / "ontology" / "final_dashboard.py"
def assert_inventory_and_registry() -> None:
    for rel in ["ontology_inventory.txt", "ontology_inventory.py", "ontology/ontology_inventory.py", "global_module_catalog.txt", "global_module_catalog.py", "dependency_registry.py"]:
        assert "final_dashboard" in (ROOT / rel).read_text(encoding="utf-8"), rel
def assert_public_contract(r: dict) -> None:
    assert r["primitive"] == "FINAL_DASHBOARD" and r["step"] == "AL10"
    assert r["final_dashboard_status"] == "FINAL_DASHBOARD_GENERATED"
    assert r["final_certification_dashboard_status"] == "FINAL_DASHBOARD_GENERATED"
    assert r["dashboard_generated"] is True and r["dashboard_ready"] is True
    assert r["component_count"] >= 9 and r["passed_component_count"] == r["component_count"]
    assert r["consciousness_proven"] is False and r["qualia_proven"] is False and r["subjectivity_proven"] is False and r["phenomenology_proven"] is False
    assert r["phenomenology_undetermined"] is True and r["functional_conclusion_only"] is True
    assert r["metrics"]["certification_readiness_score"] >= 0.70 and r["metrics"]["phenomenal_proof_score"] == 0.0
    assert "consciousness_proven = True" in " ".join(r["blocked_claims"])
def main() -> None:
    py_compile.compile(str(MODULE), cfile="/private/tmp/final_dashboard.pyc", doraise=True)
    py_compile.compile(str(ROOT / "global_module_catalog.py"), cfile="/private/tmp/global_module_catalog.pyc", doraise=True)
    assert_inventory_and_registry()
    from ontology.final_dashboard import FinalDashboard
    r = FinalDashboard().step(inputs={"synthetic": True, "ready": True, "source": "al10_fast_acceptance"}, persist=False)
    assert_public_contract(r)
    d = FinalDashboard().step(inputs={"synthetic": True, "metaphysical_status_reporter_status": "BROKEN"}, persist=False)
    assert d["final_dashboard_status"] == "FINAL_DASHBOARD_BLOCKED" and d["dashboard_generated"] is False
    print("AL10_FAST_ACCEPTANCE_ALL_OK")
if __name__ == "__main__": main()
