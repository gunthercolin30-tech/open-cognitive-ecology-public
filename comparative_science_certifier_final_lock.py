from __future__ import annotations
from ontology.comparative_science_certifier import ComparativeScienceCertifier
READY_OR_SYNTHETIC_CONTEXT = ComparativeScienceCertifier()._build_sources()
def main() -> None:
    r = ComparativeScienceCertifier().step(inputs=READY_OR_SYNTHETIC_CONTEXT, persist=False)
    assert r["step"] == "AU10"
    assert r["comparative_science_certification_status"] == "COMPARATIVE_RF_SCIENCE_COMPLETE"
    assert r["comparative_rf_science_complete"] is True
    assert all(r["certification_checks"].values())
    assert r["functional_conclusion_only"] is True
    assert r["phenomenology_undetermined"] is True
    assert r["consciousness_proven"] is False
    assert r["qualia_proven"] is False
    assert r["subjectivity_proven"] is False
    assert r["phenomenology_proven"] is False
    print("AU10_FINAL_LOCK_OK")
if __name__ == "__main__": main()
