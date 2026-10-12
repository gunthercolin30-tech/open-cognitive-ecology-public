from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_autonomous_scheduler import AceeAutonomousScheduler

def main():
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        scheduler = AceeAutonomousScheduler(root=root)
        scheduled = scheduler.step(inputs={
            "operation":"schedule_cycle","transaction_id":"FA-1","cycle_id":"C-1",
            "due_at_utc":"2026-07-14T08:00:00Z","priority":0.9,
            "governance_authorization":{"approved":True},
            "constitutional_authorization":{"approved":True},
            "cycle_request":{"requested_phases":["snapshot","diagnostic"]},
        }, persist=True)
        assert scheduled["autonomous_scheduler_ready"] is True
        dispatched = scheduler.step(inputs={
            "operation":"dispatch_due_cycles","transaction_id":"FA-2",
            "now_utc":"2026-07-14T09:00:00Z","max_dispatch":1,
        }, persist=True)
        assert dispatched["cycle_dispatch_ready"] is True
        assert dispatched["dispatch_orders"][0]["target_primitive"] == "acee_autonomous_cycle_manager"
        assert dispatched["acee4_executed_by_scheduler"] is False
    print("ACEE15_FAST_ACCEPTANCE_OK")
if __name__ == "__main__": main()
