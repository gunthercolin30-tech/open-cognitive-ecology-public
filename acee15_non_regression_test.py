from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_autonomous_scheduler import AceeAutonomousScheduler

def main():
    with TemporaryDirectory() as tmp:
        root=Path(tmp); s=AceeAutonomousScheduler(root=root)
        inputs={"operation":"schedule_cycle","transaction_id":"IDEM","cycle_id":"C","due_at_utc":"2026-07-14T10:00:00Z","priority":0.5,"governance_authorization":{"approved":True},"constitutional_authorization":{"approved":True}}
        first=s.step(inputs=inputs,persist=True); second=s.step(inputs=inputs,persist=True)
        assert second["idempotent_replay"] is True
        assert first["cycle_id"] == second["cycle_id"]
    print("ACEE15_NON_REGRESSION_OK")
if __name__ == "__main__": main()
