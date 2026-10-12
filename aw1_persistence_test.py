\
import json
import tempfile
from pathlib import Path

from ontology.multi_rf_registry import MultiRFRegistry


def main() -> None:
    inputs = {
        "rf_records": [
            {
                "rf_id": "RF-PERSIST-A",
                "status": "ACTIVE",
                "origin": "synthetic",
                "synthetic": True,
            },
            {
                "rf_id": "RF-PERSIST-B",
                "status": "ACTIVE",
                "origin": "synthetic",
                "synthetic": True,
            },
        ]
    }

    with tempfile.TemporaryDirectory(prefix="oce_aw1_persist_") as tmp:
        registry = MultiRFRegistry(root=Path(tmp))
        first = registry.step(inputs=inputs, persist=True)
        second = registry.step(inputs=inputs, persist=True)

        assert first["persisted"] is True
        assert second["persisted"] is True
        assert first["registry_hash"] == second["registry_hash"]
        assert first["contract_hash"] == second["contract_hash"]

        path = Path(second["output_path"])
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["registry_hash"] == second["registry_hash"]

        restored = registry.step(
            inputs={"load_existing": True},
            persist=False,
        )
        assert restored["registry_hash"] == second["registry_hash"]
        assert restored["registry"] == second["registry"]

    print("AW1_PERSISTENCE_AND_RESTART_OK")


if __name__ == "__main__":
    main()
