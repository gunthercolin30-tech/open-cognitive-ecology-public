import json
import tempfile
from pathlib import Path

from ontology.comparative_dashboard import ComparativeDashboard
from ontology.comparative_history import ComparativeHistory


def read_json(path):
    return json.loads(
        Path(path).read_text(encoding="utf-8")
    )


def main():
    dashboard = ComparativeDashboard().step(
        inputs={},
        persist=False,
    )

    with tempfile.TemporaryDirectory(
        prefix="oce_au9_views_"
    ) as tmp:
        history = ComparativeHistory(
            root=Path(tmp),
        )

        result = history.step(
            inputs={
                "comparative_dashboard": dashboard,
            },
            persist=True,
        )

        paths = result["canonical_paths"]

        jsonl_records = [
            json.loads(line)
            for line in Path(paths["history"])
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip()
        ]

        latest = read_json(paths["latest"])
        index = read_json(paths["index"])

        assert jsonl_records
        last_record = jsonl_records[-1]

        assert latest["record_hash"] == last_record["record_hash"]
        assert latest["snapshot_hash"] == last_record["snapshot_hash"]
        assert latest["dashboard_hash"] == last_record["dashboard_hash"]

        assert index["record_count"] == len(jsonl_records)

        assert result["record_hash"] == last_record["record_hash"]
        assert result["snapshot_hash"] == last_record["snapshot_hash"]
        assert result["dashboard_hash"] == last_record["dashboard_hash"]

        assert result["chain_integrity"]["chain_valid"] is True
        assert result["chain_integrity"]["record_count"] == len(
            jsonl_records
        )

    print("AU9_PERSISTED_VIEWS_CONSISTENCY_OK")


if __name__ == "__main__":
    main()
