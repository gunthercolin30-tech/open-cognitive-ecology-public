import json
import multiprocessing as mp
import tempfile
from pathlib import Path

from aw12_context import build_context
from ontology.ecological_prediction_engine import EcologicalPredictionEngine


def worker(root_string, index, queue):
    try:
        context = build_context()
        context["issued_at"] = f"2026-08-{index + 1:02d}T08:00:00Z"
        context["trend_signals"]["stability"] = round(-0.45 + index * 0.05, 6)
        context["trend_signals"]["resilience"] = round(0.35 - index * 0.03, 6)
        result = EcologicalPredictionEngine(Path(root_string)).step(context, persist=True)
        queue.put({"ok": True, "prediction_id": result["prediction_id"], "prediction_hash": result["prediction_hash"]})
    except Exception as error:
        queue.put({"ok": False, "error": repr(error)})


if __name__ == "__main__":
    process_count = 8
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        queue = mp.Queue()
        processes = [mp.Process(target=worker, args=(str(root), index, queue)) for index in range(process_count)]
        for process in processes:
            process.start()
        for process in processes:
            process.join(timeout=20)
            assert not process.is_alive(), "concurrent writer timeout"
            assert process.exitcode == 0, f"concurrent writer exitcode={process.exitcode}"

        results = [queue.get(timeout=5) for _ in processes]
        assert all(result["ok"] for result in results), results

        base = root / "rf_ecology" / "AW12_ecological_prediction"
        history_path = base / "ecological_prediction_history.jsonl"
        latest_path = base / "latest_ecological_prediction.json"
        assert history_path.is_file() and latest_path.is_file()

        records = [json.loads(line) for line in history_path.read_text(encoding="utf-8").splitlines()]
        assert len(records) == process_count
        history_ids = [record["prediction_id"] for record in records]
        history_hashes = [record["prediction_hash"] for record in records]
        returned_ids = [result["prediction_id"] for result in results]
        returned_hashes = [result["prediction_hash"] for result in results]
        assert len(set(history_ids)) == process_count
        assert len(set(history_hashes)) == process_count
        assert set(history_ids) == set(returned_ids)
        assert set(history_hashes) == set(returned_hashes)

        latest = json.loads(latest_path.read_text(encoding="utf-8"))
        assert latest["prediction_id"] in set(history_ids)
        assert latest["prediction_hash"] in set(history_hashes)

    print("AW12_CONCURRENT_PERSISTENCE_OK")
