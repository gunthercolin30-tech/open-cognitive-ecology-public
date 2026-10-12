from ontology.comparative_dashboard import ComparativeDashboard


def main():
    r = ComparativeDashboard().step(
        inputs={},
        persist=False,
    )

    markdown = r["exports"]["markdown"]

    assert markdown.startswith(
        "# AU8 Comparative RF Dashboard"
    )

    assert "## Summary" in markdown
    assert "## Module status" in markdown

    assert (
        "Functional comparative science only"
        in markdown
    )

    assert r["dashboard_hash"] in markdown

    for module_name in r["module_statuses"]:
        assert module_name in markdown

    assert "consciousness_proven = True" not in markdown
    assert "phenomenology_proven = True" not in markdown

    print("AU8_MARKDOWN_INTEGRITY_OK")


if __name__ == "__main__":
    main()
