from ontology.comparative_dashboard import ComparativeDashboard


def main():
    marker = "<script>alert('AU8')</script>"

    r = ComparativeDashboard().step(
        inputs={
            "comparative_blueprint": {
                "comparative_blueprint_status": marker,
            },
        },
        persist=False,
    )

    html_text = r["exports"]["html"]

    assert marker not in html_text
    assert "&lt;script&gt;" in html_text
    assert "&lt;/script&gt;" in html_text

    assert (
        "COMPARATIVE_DASHBOARD_INCOMPLETE"
        == r["comparative_dashboard_status"]
    )

    print("AU8_HTML_ESCAPING_OK")


if __name__ == "__main__":
    main()
