from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_autonomous_scheduler import AceeAutonomousScheduler

def main():
    with TemporaryDirectory() as tmp:
        root=Path(tmp); s=AceeAutonomousScheduler(root=root)
        s.step(inputs={"operation":"schedule_cycle","transaction_id":"S1","cycle_id":"C","due_at_utc":"2026-07-14T08:00:00Z","priority":1.0,"governance_authorization":{"approved":True},"constitutional_authorization":{"approved":True}},persist=True)
        s.step(inputs={"operation":"suspend_scheduler","transaction_id":"S2"},persist=True)
        blocked=s.step(inputs={"operation":"dispatch_due_cycles","transaction_id":"S3","now_utc":"2026-07-14T09:00:00Z"},persist=True)
        assert "scheduler_suspended" in blocked["blocking_reasons"]
        s.step(inputs={"operation":"resume_scheduler","transaction_id":"S4"},persist=True)
        ok=s.step(inputs={"operation":"dispatch_due_cycles","transaction_id":"S5","now_utc":"2026-07-14T09:00:00Z"},persist=True)
        assert ok["dispatch_count"] == 1
    print("ACEE15_SUSPEND_RESUME_OK")
if __name__ == "__main__": main()
