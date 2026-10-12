from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_autonomous_scheduler import AceeAutonomousScheduler

def main():
    with TemporaryDirectory() as tmp:
        root=Path(tmp)
        AceeAutonomousScheduler(root=root).step(inputs={"operation":"schedule_cycle","transaction_id":"R1","cycle_id":"C","due_at_utc":"2026-07-14T10:00:00Z","priority":0.7,"governance_authorization":{"approved":True},"constitutional_authorization":{"approved":True}},persist=True)
        inspected=AceeAutonomousScheduler(root=root).step(inputs={"operation":"inspect_schedule","cycle_id":"C"},persist=False)
        assert inspected["cycle"]["cycle_id"] == "C"
    print("ACEE15_RESTART_CONTINUITY_OK")
if __name__ == "__main__": main()
