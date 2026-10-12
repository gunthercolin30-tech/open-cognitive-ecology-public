from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_autonomous_scheduler import AceeAutonomousScheduler

def main():
    with TemporaryDirectory() as tmp:
        s=AceeAutonomousScheduler(root=Path(tmp))
        for cid,p in (("LOW",0.1),("HIGH",0.9),("MID",0.5)):
            s.step(inputs={"operation":"schedule_cycle","transaction_id":"T"+cid,"cycle_id":cid,"due_at_utc":"2026-07-14T08:00:00Z","priority":p,"governance_authorization":{"approved":True},"constitutional_authorization":{"approved":True}},persist=True)
        out=s.step(inputs={"operation":"dispatch_due_cycles","transaction_id":"D","now_utc":"2026-07-14T09:00:00Z","max_dispatch":3},persist=True)
        assert [x["cycle_id"] for x in out["dispatch_orders"]] == ["HIGH","MID","LOW"]
    print("ACEE15_PRIORITY_ORDER_OK")
if __name__ == "__main__": main()
