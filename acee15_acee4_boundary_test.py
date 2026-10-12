from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_autonomous_scheduler import AceeAutonomousScheduler

def main():
    with TemporaryDirectory() as tmp:
        root=Path(tmp); s=AceeAutonomousScheduler(root=root)
        s.step(inputs={"operation":"schedule_cycle","transaction_id":"B1","cycle_id":"C","due_at_utc":"2026-07-14T08:00:00Z","priority":1.0,"governance_authorization":{"approved":True},"constitutional_authorization":{"approved":True},"cycle_request":{"requested_phases":["snapshot"]}},persist=True)
        result=s.step(inputs={"operation":"dispatch_due_cycles","transaction_id":"B2","now_utc":"2026-07-14T09:00:00Z"},persist=True)
        order=result["dispatch_orders"][0]
        assert order["target_primitive"] == "acee_autonomous_cycle_manager"
        assert order["execution_authorized"] is False
        assert result["cycle_executed_by_scheduler"] is False
        assert result["acee4_executed_by_scheduler"] is False
    print("ACEE15_ACEE4_BOUNDARY_OK")
if __name__ == "__main__": main()
