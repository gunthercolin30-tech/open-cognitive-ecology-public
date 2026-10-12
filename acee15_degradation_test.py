from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_autonomous_scheduler import AceeAutonomousScheduler

def main():
    with TemporaryDirectory() as tmp:
        result = AceeAutonomousScheduler(root=Path(tmp)).step(inputs={"operation":"schedule_cycle","cycle_id":"X","due_at_utc":"bad","priority":float("nan")}, persist=True)
        assert result["autonomous_scheduler_ready"] is False
        assert result["persisted"] is False
    print("ACEE15_DEGRADATION_OK")
if __name__ == "__main__": main()
