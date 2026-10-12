import json
import tempfile
from pathlib import Path

from ontology.comparative_dashboard import ComparativeDashboard
from ontology.comparative_history import ComparativeHistory


def main():
    dashboard = ComparativeDashboard().step(
        inputs={},
        persist=False,
    )

    with tempfile.TemporaryDirectory(
        prefix="oce_au9_corruption_"
    ) as tmp:
        root = Path(tmp)
        history = ComparativeHistory(root=root)

        result = history.step(
            inputs={
                "comparative_dashboard": dashboard,
            },
            persist=True,
        )

        history_path = Path(
            result["canonical_paths"]["history"]
        )

        records = [
            json.loads(line)
            for line in history_path.read_text(
                encoding="utf-8"
            ).splitlines()
            if line.strip()
        ]

        assert len(records) == 1

        records[0]["snapshot_hash"] = "0" * 64

        history_path.write_text(
            "\n".join(
                json.dumps(
                    record,
                    sort_keys=True,
                    separators=(",", ":"),
                )
                for record in records
            ) + "\n",
            encoding="utf-8",
        )

        corrupted = [
            json.loads(line)
            for line in history_path.read_text(
                encoding="utf-8"
            ).splitlines()
            if line.strip()
        ]

        chain = history._validate_chain(corrupted)

        assert chain["chain_valid"] is False
        assert chain["chain_errors"]

    print("AU9_CORRUPTION_DETECTION_OK")


if __name__ == "__main__":
    main()
