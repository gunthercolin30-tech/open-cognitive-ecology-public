from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_longitudinal_tracker import AceeLongitudinalTracker

def main():
    with TemporaryDirectory() as tmp:
        root=Path(tmp); AceeLongitudinalTracker(root=root).step(inputs={"operation":"record_cycle","transaction_id":"R-1","cycle_id":"R-C","before_score":0.2,"after_score":0.3},persist=True)
        result=AceeLongitudinalTracker(root=root).step(inputs={"operation":"inspect_cycle","cycle_id":"R-C"},persist=False)
        assert result["cycle_record"]["cycle_id"] == "R-C"
    print("ACEE16_RESTART_CONTINUITY_OK")
if __name__ == "__main__": main()
