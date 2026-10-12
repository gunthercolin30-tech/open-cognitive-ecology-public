from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_longitudinal_tracker import AceeLongitudinalTracker

def main():
    with TemporaryDirectory() as tmp:
        root=Path(tmp); t=AceeLongitudinalTracker(root=root); t.step(inputs={"operation":"record_cycle","transaction_id":"C-1","cycle_id":"C-C"},persist=True)
        p=root/"acee_runtime"/"ACEE16_acee_longitudinal_tracker"/"cycle_history.jsonl"; p.write_text(p.read_text()+"broken\n")
        result=t.step(inputs={"operation":"verify_history"},persist=False); assert result["history_valid"] is False
    print("ACEE16_CORRUPTION_OK")
if __name__ == "__main__": main()
