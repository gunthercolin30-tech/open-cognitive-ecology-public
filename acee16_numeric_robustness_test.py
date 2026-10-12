from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_longitudinal_tracker import AceeLongitudinalTracker

def main():
    with TemporaryDirectory() as tmp:
        for value in [float("nan"),float("inf"),True,"abc"]:
            result=AceeLongitudinalTracker(root=Path(tmp)).step(inputs={"operation":"record_cycle","transaction_id":str(value),"cycle_id":str(value),"before_score":value},persist=False)
            assert "before_score_invalid" in result["blocking_reasons"]
    print("ACEE16_NUMERIC_ROBUSTNESS_OK")
if __name__ == "__main__": main()
