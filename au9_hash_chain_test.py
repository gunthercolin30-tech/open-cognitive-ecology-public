import json
from pathlib import Path

from ontology.comparative_history import ComparativeHistory


def main():
    history = ComparativeHistory()

    result = history.step(
        inputs={},
        persist=True,
    )

    path = Path(
        result["canonical_paths"]["history"]
    )

    records = [
        json.loads(line)
        for line in path.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]

    chain = history._validate_chain(records)

    assert chain["chain_valid"] is True
    assert chain["record_count"] == len(records)
    assert chain["valid_record_count"] == len(records)
    assert chain["chain_errors"] == []

    previous = None

    for index, record in enumerate(records, start=1):
        assert record["sequence_index"] == index
        assert record["previous_record_hash"] == previous
        assert len(record["record_hash"]) == 64
        previous = record["record_hash"]

    print("AU9_HASH_CHAIN_OK")


if __name__ == "__main__":
    main()
