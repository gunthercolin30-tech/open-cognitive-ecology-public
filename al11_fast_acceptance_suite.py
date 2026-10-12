#!/usr/bin/env python3
from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
MODULE = ROOT / "ontology" / "final_theoretical_report.py"


def assert_inventory_and_registry() -> None:
    for rel in [
        "ontology_inventory.txt",
        "ontology_inventory.py",
        "ontology/ontology_inventory.py",
        "global_module_catalog.txt",
        "global_module_catalog.py",
        "dependency_registry.py",
    ]:
        path = ROOT / rel
        assert path.exists(), rel
        text = path.read_text(encoding="utf-8")
        assert "final_theoretical_report" in text, rel


def assert_public_contract(r: dict) -> None:
    assert r["primitive"] == "FINAL_THEORETICAL_REPORT"
    assert r["step"] == "AL11"
    assert r["final_theoretical_report_status"] == "FINAL_THEORETICAL_REPORT_GENERATED"
    assert r["final_consciousness_certification_status"] == "FINAL_CONSCIOUSNESS_CERTIFICATION_COMPLETE"
    assert r["final_axis_status"] == "FINAL_CONSCIOUSNESS_CERTIFICATION_COMPLETE"
    assert r["report_generated"] is True and r["report_ready"] is True
    assert r["section_count"] == r["required_section_count"] >= 11
    assert r["missing_sections"] == []
    assert r["metrics"]["final_certification_score"] >= 0.70
    assert r["metrics"]["phenomenal_proof_score"] == 0.0
    assert r["consciousness_proven"] is False
    assert r["qualia_proven"] is False
    assert r["subjectivity_proven"] is False
    assert r["phenomenology_proven"] is False
    assert r["phenomenology_undetermined"] is True
    assert r["functional_conclusion_only"] is True
    assert "consciousness_proven = True" in " ".join(r["blocked_claims"])
    for section in [
        "executive_summary", "reconstruction_summary", "theorem_summary",
        "certification_summary", "semantic_summary", "epistemic_limits",
        "allowed_claims", "blocked_claims", "final_functional_conclusion",
        "future_work", "scientific_appendix",
    ]:
        assert section in r["final_theoretical_report"], section


def main() -> None:
    py_compile.compile(str(MODULE), cfile="/private/tmp/final_theoretical_report.pyc", doraise=True)
    py_compile.compile(str(ROOT / "global_module_catalog.py"), cfile="/private/tmp/global_module_catalog.pyc", doraise=True)
    assert_inventory_and_registry()
    from ontology.final_theoretical_report import FinalTheoreticalReport
    ready = {"synthetic": True, "ready": True, "source": "al11_fast_acceptance"}
    r = FinalTheoreticalReport().step(inputs=ready, persist=False)
    assert_public_contract(r)
    degraded = FinalTheoreticalReport().step(
        inputs={"synthetic": True, "ready": False, "final_dashboard_status": "BROKEN"},
        persist=False,
    )
    assert degraded["final_theoretical_report_status"] == "FINAL_THEORETICAL_REPORT_BLOCKED"
    assert degraded["report_generated"] is False
    assert "final_dashboard_status" in degraded["failure_reasons"]
    print("AL11_FAST_ACCEPTANCE_ALL_OK")


if __name__ == "__main__":
    main()
