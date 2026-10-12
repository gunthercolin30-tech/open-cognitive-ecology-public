import json
from pathlib import Path


def main():
    path = Path(
        "acee_runtime/ACEE17_acee_dashboard/"
        "latest_dashboard.json"
    )

    payload = json.loads(
        path.read_text(encoding="utf-8")
    )

    assert payload["persist_requested"] is True
    assert payload["persisted"] is True

    json_path = Path(
        payload["artifacts"]["json_path"]
    ).resolve()

    html_path = Path(
        payload["artifacts"]["html_path"]
    ).resolve()

    assert json_path == path.resolve()
    assert html_path == path.with_name(
        "latest_dashboard.html"
    ).resolve()

    assert payload["exports"]["json"] is None

    print("ACEE17_PERSISTED_CONTRACT_OK")


if __name__ == "__main__":
    main()
