from __future__ import annotations

import tempfile
from pathlib import Path

from oif.adapters.runtime_health_adapter import RuntimeHealthAdapter


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="oif2_3c_degradation_") as tmp:
        root = Path(tmp)
        invalid = (
            root
            / "runtime_service/service_state.json"
        )
        invalid.parent.mkdir(parents=True, exist_ok=True)
        invalid.write_text('{"status": NaN}', encoding="utf-8")

        payload = RuntimeHealthAdapter(root=root).read()
        assert payload["status"] == "degraded"
        assert payload["available_source_count"] == 0
        assert payload["invalid_source_count"] == 1
        assert (
            payload["sections"]["runtime_service"]["availability"]
            == "invalid"
        )
        assert (
            payload["sections"]["long_duration_runtime"]["availability"]
            == "missing"
        )
        assert (
            payload["sections"]["hardware_health"]["availability"]
            == "missing"
        )

    print("OIF2_3C_RUNTIME_HEALTH_ADAPTER_DEGRADATION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
