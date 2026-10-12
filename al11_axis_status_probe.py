from ontology.final_theoretical_report import FinalTheoreticalReport

r = FinalTheoreticalReport().step(
    inputs={"synthetic_certification_context": "ready"},
    persist=False,
)

for k in [
    "final_axis_status",
    "final_consciousness_certification_status",
    "functional_status",
    "scientific_status",
    "final_conclusion",
]:
    print(k, "=", repr(r.get(k)))
