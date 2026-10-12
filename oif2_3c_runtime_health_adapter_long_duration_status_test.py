from __future__ import annotations

import json
import tempfile
from pathlib import Path

from oif.adapters.runtime_health_adapter import RuntimeHealthAdapter


def write_state(root: Path, payload: dict) -> None:
    path = root / "runtime_supervision/long_duration_runtime_state.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def main() -> int:
    with tempfile.TemporaryDirectory(
        prefix="oif2_3c_long_duration_status_"
    ) as tmp:
        root = Path(tmp)
        adapter = RuntimeHealthAdapter(root=root)

        write_state(
            root,
            {
                "last_execution_utc": "2026-07-16T09:31:19+00:00",
                "last_long_duration_viability": 0.99,
                "last_uptime_score": 0.99,
                "restart_events": 0,
                "supervision_cycles": 5041,
            },
        )
        ready = adapter.read()["sections"]["long_duration_runtime"]
        assert ready["availability"] == "available"
        assert ready["status"] == "ready"

        write_state(
            root,
            {
                "last_long_duration_viability": 0.70,
                "last_uptime_score": 0.72,
                "restart_events": 4,
                "supervision_cycles": 40,
            },
        )
        degraded = adapter.read()["sections"]["long_duration_runtime"]
        assert degraded["status"] == "degraded"

        write_state(
            root,
            {
                "last_long_duration_viability": 0.84,
                "last_uptime_score": 0.86,
                "restart_events": 1,
                "supervision_cycles": 40,
            },
        )
        intermediate = adapter.read()["sections"]["long_duration_runtime"]
        assert intermediate["status"] == "unknown"

        write_state(
            root,
            {
                "last_uptime_score": 0.99,
                "restart_events": 0,
                "supervision_cycles": 40,
            },
        )
        incomplete = adapter.read()["sections"]["long_duration_runtime"]
        assert incomplete["status"] == "unknown"

    print("OIF2_3C_LONG_DURATION_STATUS_CONTRACT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
