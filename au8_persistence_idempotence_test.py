import hashlib
from pathlib import Path

from ontology.comparative_dashboard import ComparativeDashboard


def sha256(path):
    return hashlib.sha256(
        Path(path).read_bytes()
    ).hexdigest()


def main():
    dashboard = ComparativeDashboard()

    first = dashboard.step(
        inputs={},
        persist=True,
    )

    first_paths = dict(first["output_paths"])
    first_hashes = {
        name: sha256(path)
        for name, path in first_paths.items()
    }

    second = dashboard.step(
        inputs={},
        persist=True,
    )

    second_paths = dict(second["output_paths"])
    second_hashes = {
        name: sha256(path)
        for name, path in second_paths.items()
    }

    assert first_paths == second_paths
    assert first["dashboard_hash"] == second["dashboard_hash"]
    assert first_hashes == second_hashes

    print("AU8_PERSISTENCE_IDEMPOTENCE_OK")


if __name__ == "__main__":
    main()
