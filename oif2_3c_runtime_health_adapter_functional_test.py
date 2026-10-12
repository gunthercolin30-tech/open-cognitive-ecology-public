from __future__ import annotations

import json
import tempfile
from pathlib import Path

from oif.adapters.runtime_health_adapter import RuntimeHealthAdapter


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="oif2_3c_functional_") as tmp:
        root = Path(tmp)
        write(
            root / "runtime_service/service_state.json",
            {
                "primitive": "AUTONOMOUS_RUNTIME_SERVICE",
                "status": "running",
                "iterations": 4,
            },
        )
        write(
            root / "runtime_supervision/long_duration_runtime_state.json",
            {
                "supervision_cycles": 7,
                "restart_events": 0,
                "last_uptime_score": 0.99,
                "status": "operational",
            },
        )
        write(
            root / "physical_ecology/latest_hardware_health_monitor.json",
            {
                "primitive": "autonomous_hardware_health_monitor",
                "schema_version": "Q2.autonomous_hardware_health_monitor.v1",
                "health_classification": "healthy",
                "hardware_health_index": 0.95,
                "success": True,
            },
        )

        payload = RuntimeHealthAdapter(root=root).read()
        assert payload["adapter_schema_version"] == (
            "oif2.runtime-health-adapter.v1"
        )
        assert payload["status"] == "ready"
        assert payload["available_source_count"] == 3
        assert payload["invalid_source_count"] == 0
        assert payload["read_only"] is True
        assert payload["translation_only"] is True
        assert payload["producer_execution"] is False
        assert payload["synthetic_cross_source_score"] is False
        assert payload["sections"]["runtime_service"]["status"] == "ready"
        assert payload["sections"]["hardware_health"]["status"] == "ready"
        assert payload["consciousness_proven"] is False
        assert payload["functional_conclusion_only"] is True

    print("OIF2_3C_RUNTIME_HEALTH_ADAPTER_FUNCTIONAL_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
