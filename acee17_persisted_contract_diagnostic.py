import json
from pathlib import Path
from pprint import pprint


def main():
    path = Path(
        "acee_runtime/ACEE17_acee_dashboard/"
        "latest_dashboard.json"
    )

    payload = json.loads(
        path.read_text(encoding="utf-8")
    )

    pprint({
        "path": str(path.resolve()),
        "status": payload.get("status"),
        "persist_requested": payload.get("persist_requested"),
        "persisted": payload.get("persisted"),
        "artifacts": payload.get("artifacts"),
        "exports_json": (
            payload.get("exports", {}).get("json")
        ),
        "cycle_count": payload.get("cycle_count"),
    })


if __name__ == "__main__":
    main()
