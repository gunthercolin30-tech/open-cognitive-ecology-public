from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_longitudinal_tracker import AceeLongitudinalTracker

def main():
    with TemporaryDirectory() as tmp:
        result = AceeLongitudinalTracker(root=Path(tmp)).step(inputs={"operation":"record_cycle","transaction_id":"D-1","before_score":"nan"}, persist=True)
        assert result["persisted"] is False and "cycle_id_missing" in result["blocking_reasons"]
    print("ACEE16_DEGRADATION_OK")
if __name__ == "__main__": main()
