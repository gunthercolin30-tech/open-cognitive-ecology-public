from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_autonomous_scheduler import AceeAutonomousScheduler

def main():
    with TemporaryDirectory() as tmp:
        root=Path(tmp)
        def add(i):
            return AceeAutonomousScheduler(root=root).step(inputs={"operation":"schedule_cycle","transaction_id":f"T{i}","cycle_id":f"C{i}","due_at_utc":"2026-07-14T10:00:00Z","priority":i/20,"governance_authorization":{"approved":True},"constitutional_authorization":{"approved":True}},persist=True)
        with ThreadPoolExecutor(max_workers=8) as pool: results=list(pool.map(add,range(20)))
        assert all(x["persisted"] for x in results)
        listing=AceeAutonomousScheduler(root=root).step(inputs={"operation":"list_pending_cycles"},persist=False)
        assert listing["pending_count"] == 20
    print("ACEE15_CONCURRENCY_OK")
if __name__ == "__main__": main()
