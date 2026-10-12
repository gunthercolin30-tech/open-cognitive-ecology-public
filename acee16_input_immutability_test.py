from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_longitudinal_tracker import AceeLongitudinalTracker

def main():
    payload={"operation":"record_cycle","transaction_id":"I-1","cycle_id":"I-C","selection_decision":{"decision":"accept","decision_reasons":["x"]}}; original=deepcopy(payload)
    with TemporaryDirectory() as tmp: AceeLongitudinalTracker(root=Path(tmp)).step(inputs=payload,persist=False)
    assert payload == original
    print("ACEE16_INPUT_IMMUTABILITY_OK")
if __name__ == "__main__": main()
