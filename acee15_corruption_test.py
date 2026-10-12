from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_autonomous_scheduler import AceeAutonomousScheduler

def main():
    with TemporaryDirectory() as tmp:
        root=Path(tmp); s=AceeAutonomousScheduler(root=root)
        s.step(inputs={"operation":"suspend_scheduler","transaction_id":"C1"},persist=True)
        history=root/"acee_runtime"/"ACEE15_acee_autonomous_scheduler"/"schedule_history.jsonl"
        history.write_text(history.read_text(encoding="utf-8")+"broken\n",encoding="utf-8")
        result=s.step(inputs={"operation":"inspect_schedule"},persist=False)
        assert result["schedule_history_corrupted"] is True
    print("ACEE15_CORRUPTION_OK")
if __name__ == "__main__": main()
