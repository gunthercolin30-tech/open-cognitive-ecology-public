import json

from ontology.comparative_dashboard import ComparativeDashboard


def main():
    r = ComparativeDashboard().step(
        inputs={},
        persist=False,
    )

    exported = json.loads(
        r["exports"]["json"]
    )

    assert exported["step"] == "AU8"
    assert exported["primitive"] == "comparative_dashboard"

    assert exported["dashboard_hash"] == r["dashboard_hash"]

    assert exported["dashboard_summary"] == (
        r["dashboard_summary"]
    )

    assert exported["module_statuses"] == (
        r["module_statuses"]
    )

    assert "timestamp_utc" not in exported
    assert "exports" not in exported
    assert "export_integrity" not in exported

    print("AU8_JSON_EXPORT_CONTRACT_OK")


if __name__ == "__main__":
    main()
