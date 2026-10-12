from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_longitudinal_tracker import AceeLongitudinalTracker

def main():
    with TemporaryDirectory() as tmp:
        tracker = AceeLongitudinalTracker(root=Path(tmp))
        result = tracker.step(inputs={"operation":"record_cycle","transaction_id":"FA-1","cycle_id":"C-1","timestamp_utc":"2026-07-14T10:00:00Z","before_score":0.8,"after_score":0.9,"validation_result":{"validation_passed":True},"selection_decision":{"decision":"accept"}}, persist=True)
        assert result["longitudinal_tracking_ready"] is True
        assert result["record_created"] is True and result["persisted"] is True
        assert result["score_delta"] == 0.1
    print("ACEE16_FAST_ACCEPTANCE_OK")
if __name__ == "__main__": main()
