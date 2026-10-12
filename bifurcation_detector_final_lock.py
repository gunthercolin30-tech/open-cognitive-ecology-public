from ontology.bifurcation_detector import BifurcationDetector
READY_OR_SYNTHETIC_CONTEXT = {"observations": [{"timestamp_utc": f"2026-12-{i:02d}T00:00:00Z", "state_vector": {"stability": a, "integration": b, "openness": c}, "data_quality": .98, "synthetic": True} for i,(a,b,c) in enumerate([(.80,.78,.84),(.79,.77,.83),(.81,.79,.82),(.22,.28,.31),(.24,.27,.30),(.23,.29,.32),(.25,.28,.31)],1)]}
def main():
    r = BifurcationDetector().step(inputs=READY_OR_SYNTHETIC_CONTEXT, persist=False)
    assert r["primitive"] == "BIFURCATION_DETECTOR" and r["step"] == "AV4" and r["public_schema_version"] == "1.0"
    assert r["bifurcation_status"] in {"FUNCTIONAL_BIFURCATION_DETECTED","FUNCTIONAL_STRUCTURAL_BREAK_DETECTED"}
    assert len(r["bifurcation_hash"]) == 64
    assert r["functional_conclusion_only"] is True and r["phenomenology_undetermined"] is True
    assert all(r[k] is False for k in ["consciousness_proven","qualia_proven","subjectivity_proven","phenomenology_proven"])
    print("AV4_FINAL_LOCK_OK")
if __name__ == "__main__": main()
