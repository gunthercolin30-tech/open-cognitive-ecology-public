from ontology.final_theoretical_report import FinalTheoreticalReport

ctx = {
    "force_epistemic_guard": True,
    "synthetic_certification_context": "ready",
}

r = FinalTheoreticalReport().step(inputs=ctx, persist=False)

assert r["final_theoretical_report_status"] == "FINAL_THEORETICAL_REPORT_GENERATED"
assert r["final_conclusion"] == "FINAL_CONSCIOUSNESS_CERTIFICATION_COMPLETE"
assert r["functional_conclusion_only"] is True
assert r["phenomenology_undetermined"] is True

for k in [
    "consciousness_proven",
    "qualia_proven",
    "subjectivity_proven",
    "phenomenology_proven",
]:
    assert r[k] is False

assert r["epistemic_scope"] == "functional_only"
assert "phenomenal_subjectivity" in r["blocked_claims"]

print("AL11_EPISTEMIC_GUARD_FINAL_LOCK_OK")
