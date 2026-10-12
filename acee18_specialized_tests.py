#!/usr/bin/env python3
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_prediction_engine import ACEEPredictionEngine


def main() -> None:
    candidates = [
        {"candidate_id": "b", "predicted_gain": 0.2, "risk": 0.1},
        {"candidate_id": "a", "predicted_gain": 0.2, "risk": 0.1},
    ]
    first = ACEEPredictionEngine().step(
        inputs={"candidates": candidates},
        persist=False,
    )
    second = ACEEPredictionEngine().step(
        inputs={"candidates": list(reversed(candidates))},
        persist=False,
    )
    assert first["prediction_hash"] == second["prediction_hash"]
    assert [x["candidate_id"] for x in first["ranked_candidates"]] == ["a", "b"]

    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        runtime = root / "runtime"
        result = ACEEPredictionEngine(
            root=root,
            runtime_dir=runtime,
        ).step(
            inputs={"candidates": candidates},
            persist=True,
        )
        path = Path(result["artifacts"]["json_path"])
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["persisted"] is True
        assert payload["prediction_hash"] == result["prediction_hash"]

    try:
        ACEEPredictionEngine(
            root=Path.cwd(),
            runtime_dir=Path.cwd().parent / "outside",
        )
    except ValueError as exc:
        assert str(exc) == "runtime_dir_outside_root"
    else:
        raise AssertionError("outside-root path accepted")

    print("ACEE18_SPECIALIZED_TESTS_OK")


if __name__ == "__main__":
    main()
