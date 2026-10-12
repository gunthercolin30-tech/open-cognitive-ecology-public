from __future__ import annotations
import copy
from ontology.comparative_science_certifier import ComparativeScienceCertifier

def main() -> None:
    certifier = ComparativeScienceCertifier()
    nominal = certifier.step(inputs={}, persist=False)
    assert nominal["comparative_science_certification_status"] == "COMPARATIVE_RF_SCIENCE_COMPLETE"
    assert nominal["comparative_rf_science_complete"] is True
    assert all(nominal["certification_checks"].values())
    assert len(nominal["certification_hash"]) == 64
    nominal_sources = certifier._build_sources()
    nominal_history = nominal_sources["comparative_history"]
    assert nominal_history["change_set"]["change_type"] in {
        "INITIAL_SNAPSHOT",
        "COMPARATIVE_STATE_CHANGED",
        "NO_CHANGE",
    }
    if nominal_history.get("record_hash") is None:
        assert nominal_history["change_set"]["change_type"] == "NO_CHANGE"
        assert isinstance(
            nominal_history["chain_integrity"].get("head_hash"),
            str,
        )
        assert len(nominal_history["chain_integrity"]["head_hash"]) == 64
    nominal_recheck = certifier.step(
        inputs=nominal_sources,
        persist=False,
    )
    assert nominal_recheck["certification_checks"]["hash_integrity"] is True
    assert len(nominal_recheck["history_record_hash"]) == 64
    sources = certifier._build_sources()
    cases = [
        ("comparative_blueprint", "comparative_blueprint_status", "MISSING"),
        ("comparative_dashboard", "comparative_dashboard_status", "COMPARATIVE_DASHBOARD_INCOMPLETE"),
        ("comparative_history", "comparative_history_status", "COMPARATIVE_HISTORY_INCOMPLETE"),
    ]
    for module, key, value in cases:
        degraded = copy.deepcopy(sources); degraded[module][key] = value
        r = certifier.step(inputs=degraded, persist=False)
        assert r["comparative_rf_science_complete"] is False
    low = copy.deepcopy(sources); low["comparative_dashboard"]["dashboard_summary"]["coverage_score"] = 0.0
    assert certifier.step(inputs=low, persist=False)["certification_checks"]["coverage"] is False
    bad = copy.deepcopy(sources); bad["comparative_history"]["dashboard_hash"] = "0" * 64
    assert certifier.step(inputs=bad, persist=False)["certification_checks"]["hash_integrity"] is False
    guard = copy.deepcopy(sources); guard["taxonomy_builder"]["phenomenology_proven"] = True
    assert certifier.step(inputs=guard, persist=False)["certification_checks"]["epistemic_guards"] is False
    print("AU10_FAST_ACCEPTANCE_OK")

if __name__ == "__main__": main()
