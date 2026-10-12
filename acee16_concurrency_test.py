from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_longitudinal_tracker import AceeLongitudinalTracker

def main():
    with TemporaryDirectory() as tmp:
        root=Path(tmp)
        def run(i): return AceeLongitudinalTracker(root=root).step(inputs={"operation":"record_cycle","transaction_id":f"T-{i}","cycle_id":f"C-{i}","before_score":0.1,"after_score":0.2},persist=True)
        with ThreadPoolExecutor(max_workers=8) as pool: results=list(pool.map(run,range(20)))
        assert all(r["persisted"] for r in results)
        listing=AceeLongitudinalTracker(root=root).step(inputs={"operation":"list_cycles"},persist=False); assert listing["cycle_count"] == 20
    print("ACEE16_CONCURRENCY_OK")
if __name__ == "__main__": main()
