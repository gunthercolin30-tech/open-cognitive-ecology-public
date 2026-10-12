from ontology.final_theoretical_report import FinalTheoreticalReport

r = FinalTheoreticalReport().step(
    inputs={"synthetic_certification_context": "ready"},
    persist=False,
)

assert r["final_theoretical_report_status"] == "FINAL_THEORETICAL_REPORT_GENERATED"
assert r["final_consciousness_certification_status"] == "FINAL_CONSCIOUSNESS_CERTIFICATION_COMPLETE"
assert r["final_axis_status"] == "AL_AXIS_COMPLETE"
assert r["report_generated"] is True
assert r["report_ready"] is True
assert r["functional_conclusion_only"] is True
assert r["phenomenology_undetermined"] is True

for k in [
    "consciousness_proven",
    "qualia_proven",
    "subjectivity_proven",
    "phenomenology_proven",
]:
    assert r[k] is False

assert "FUNCTIONAL" in r["functional_status"]
assert "EPISTEMIC" in r["functional_status"]
assert "EMPIRICAL_VALIDATION" in r["scientific_status"]
assert "FINAL_CONSCIOUSNESS_CERTIFICATION_COMPLETE" in r["final_conclusion"]

report = r["final_theoretical_report"]
for key in [
    "executive_summary",
    "reconstruction_summary",
    "theorem_summary",
    "certification_summary",
    "semantic_summary",
    "epistemic_limits",
    "allowed_claims",
    "blocked_claims",
    "final_functional_conclusion",
    "future_work",
    "scientific_appendix",
]:
    assert key in report

assert r["missing_sections"] == []
assert r["section_count"] == r["required_section_count"]

print("AL11_FUNCTIONAL_COMPLETION_FINAL_LOCK_OK")
