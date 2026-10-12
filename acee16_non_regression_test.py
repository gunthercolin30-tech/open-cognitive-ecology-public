from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_longitudinal_tracker import AceeLongitudinalTracker

def main():
    with TemporaryDirectory() as tmp:
        tracker = AceeLongitudinalTracker(root=Path(tmp)); payload={"operation":"record_cycle","transaction_id":"NR-1","cycle_id":"NR-C","before_score":0.1,"after_score":0.2}
        first=tracker.step(inputs=payload,persist=True); second=tracker.step(inputs=payload,persist=True)
        assert first["record_hash"] == second["record_hash"] and second["idempotent_replay"] is True
    print("ACEE16_NON_REGRESSION_OK")
if __name__ == "__main__": main()
