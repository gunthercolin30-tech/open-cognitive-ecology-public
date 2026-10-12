from pathlib import Path

from ontology.comparative_dashboard import ComparativeDashboard


def main():
    result = ComparativeDashboard().step(
        inputs={},
        persist=True,
    )

    assert result["comparative_dashboard_status"] == (
        "COMPARATIVE_DASHBOARD_READY"
    )
    assert result["persisted"] is True

    expected = {"json", "markdown", "html"}
    assert set(result["output_paths"]) == expected

    for export_type, raw_path in result["output_paths"].items():
        path = Path(raw_path)
        assert path.is_file(), (export_type, path)
        assert path.stat().st_size > 0, (export_type, path)

    html_path = Path(result["output_paths"]["html"])
    html_text = html_path.read_text(encoding="utf-8")

    assert html_text.startswith("<!doctype html>")
    assert "</html>" in html_text
    assert "Functional comparative science only" in html_text

    print("AU8_PERSISTENCE_AND_EXPORTS_OK")


if __name__ == "__main__":
    main()
