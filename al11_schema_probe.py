from ontology.final_theoretical_report import FinalTheoreticalReport

r = FinalTheoreticalReport().step(
    inputs={"synthetic_certification_context": "ready"},
    persist=False,
)

print("AL11_KEYS:")
for k in sorted(r.keys()):
    print("-", k)

print("final_conclusion =", repr(r.get("final_conclusion")))
print("scientific_status =", repr(r.get("scientific_status")))
print("functional_status =", repr(r.get("functional_status")))
