#!/usr/bin/env python3
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_meta_analysis import ACEEMetaAnalysis


def main():
    observations = [
        {"observation_id": "b", "effect_size": 0.2, "variance": 0.1},
        {"observation_id": "a", "effect_size": 0.1, "variance": 0.1},
    ]
    first = ACEEMetaAnalysis().step(
        inputs={"observations": observations},
        persist=False,
    )
    second = ACEEMetaAnalysis().step(
        inputs={"observations": list(reversed(observations))},
        persist=False,
    )
    assert first["analysis_hash"] == second["analysis_hash"]
    assert [
        item["observation_id"]
        for item in first["included_observations"]
    ] == ["a", "b"]

    try:
        ACEEMetaAnalysis().step(
            inputs={
                "observations": [
                    {"observation_id": "dup", "effect_size": 0.1, "variance": 1.0},
                    {"observation_id": " dup ", "effect_size": 0.2, "variance": 1.0},
                ]
            },
            persist=False,
        )
    except ValueError as exc:
        assert str(exc) == "duplicate_observation_id:dup"
    else:
        raise AssertionError("duplicate observation accepted")

    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        runtime = root / "runtime"
        result = ACEEMetaAnalysis(
            root=root,
            runtime_dir=runtime,
        ).step(
            inputs={"observations": observations},
            persist=True,
        )
        path = Path(result["artifacts"]["json_path"])
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["persisted"] is True
        assert payload["analysis_hash"] == result["analysis_hash"]

    try:
        ACEEMetaAnalysis(
            root=Path.cwd(),
            runtime_dir=Path.cwd().parent / "outside",
        )
    except ValueError as exc:
        assert str(exc) == "runtime_dir_outside_root"
    else:
        raise AssertionError("outside-root path accepted")

    print("ACEE19_SPECIALIZED_TESTS_OK")


if __name__ == "__main__":
    main()
