from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_lineage_manager import AceeLineageManager
with TemporaryDirectory() as tmp:
    root=Path(tmp); AceeLineageManager(root=root).step({"operation":"register_root","transaction_id":"T0","lineage_id":"L","architecture_id":"A0"},persist=True)
    def work(i):
        return AceeLineageManager(root=root).step({"operation":"register_candidate","transaction_id":f"T{i}","lineage_id":"L","generation_id":i,"architecture_id":f"A{i}","parent_id":"A0","mutation_id":f"M{i}","fitness_delta":0.01*i},persist=True)
    with ThreadPoolExecutor(max_workers=8) as ex: results=list(ex.map(work,range(1,21)))
    assert all(r["persisted"] for r in results)
    lines=(root/"acee_runtime/ACEE13_acee_lineage_manager/lineage_event_history.jsonl").read_text().splitlines()
    assert len(lines)==21
print("ACEE13_CONCURRENCY_OK")
