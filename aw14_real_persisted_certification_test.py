from pathlib import Path

from aw14_context import build_context
from ontology.ecological_certifier import EcologicalCertifier


def main() -> None:
    result = EcologicalCertifier().step(
        inputs=build_context(),
        persist=True,
    )

    assert result["certification_status"] == "RF_ECOLOGY_COMPLETE"
    assert result["ecology_complete"] is True
    assert result["persisted"] is True
    assert len(result["certification_hash"]) == 64

    latest = Path(result["latest_path"])
    history = Path(result["history_path"])

    assert latest.is_file()
    assert history.is_file()
    assert latest.stat().st_size > 0
    assert history.stat().st_size > 0

    print("AW14_REAL_PERSISTED_CERTIFICATION_OK")
    print(f"latest={latest}")
    print(f"history={history}")
    print(f"certification_hash={result['certification_hash']}")


if __name__ == "__main__":
    main()
