from pathlib import Path

from ontology.comparative_history import ComparativeHistory


def main():
    result = ComparativeHistory().step(
        inputs={},
        persist=True,
    )

    assert result["comparative_history_status"] == (
        "COMPARATIVE_HISTORY_READY"
    )
    assert result["persisted"] is True
    assert result["chain_integrity"]["chain_valid"] is True

    for name, raw_path in result["output_paths"].items():
        path = Path(raw_path)
        assert path.exists(), (name, path)
        assert path.stat().st_size > 0, (name, path)

    print("AU9_PERSISTENCE_OK")


if __name__ == "__main__":
    main()
