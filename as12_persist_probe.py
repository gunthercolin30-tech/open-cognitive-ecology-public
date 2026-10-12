from pathlib import Path
from ontology.consciousness_first_crossing_report import ConsciousnessFirstCrossingReport

r = ConsciousnessFirstCrossingReport().step(
    inputs={
        "threshold_detected": True,
        "threshold_event_type": "CONSCIOUSNESS_THRESHOLD_CROSSED",
        "timestamp_utc": "2026-07-08T19:20:03Z",
        "CRI": 0.97,
        "confidence": 0.94,
    },
    persist=True,
)

assert r["persisted"] is True
assert r["first_crossing_report_ready"] is True
assert Path(r["json_path"]).exists()
assert Path(r["markdown_path"]).exists()
assert Path(r["pdf_path"]).exists()

print("AS12_PERSISTENCE_OK")
print(r["json_path"])
print(r["markdown_path"])
print(r["pdf_path"])
