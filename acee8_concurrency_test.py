\
import json, tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from acee8_fast_acceptance_suite import context
from ontology.acee_impact_evaluator import AceeImpactEvaluator
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    def run(i):
        data = context(); data["evaluation_id"] = "impact-%03d" % i
        return AceeImpactEvaluator(root=root).step(inputs=data, persist=True)
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(run, range(20)))
    history = Path(results[-1]["history_path"])
    lines = [json.loads(x) for x in history.read_text(encoding="utf-8").splitlines() if x.strip()]
    assert len(lines) == 20 and all(item["persisted"] for item in results)
    assert all(lines[i]["previous_impact_hash"] == lines[i-1]["impact_hash"] for i in range(1, len(lines)))
print("ACEE8_CONCURRENCY_OK")
