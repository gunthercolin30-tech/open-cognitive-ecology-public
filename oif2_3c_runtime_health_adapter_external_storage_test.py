from __future__ import annotations

import json
import tempfile
from pathlib import Path

from oif.adapters.runtime_health_adapter import RuntimeHealthAdapter


def main() -> int:
    with tempfile.TemporaryDirectory(
        prefix="oif2_3c_external_storage_"
    ) as tmp:
        base = Path(tmp)
        root = base / "repository"
        external = base / "external_continuity"
        root.mkdir()
        external.mkdir()

        runtime_target = external / "runtime_service"
        runtime_target.mkdir()
        state = runtime_target / "service_state.json"
        state.write_text(
            json.dumps({
                "primitive": "AUTONOMOUS_RUNTIME_SERVICE",
                "status": "running",
            }),
            encoding="utf-8",
        )

        (root / "runtime_service").symlink_to(
            runtime_target,
            target_is_directory=True,
        )

        payload = RuntimeHealthAdapter(root=root).read()
        section = payload["sections"]["runtime_service"]

        assert section["availability"] == "available"
        assert section["status"] == "ready"
        assert section["relative_path"] == (
            "runtime_service/service_state.json"
        )
        assert section["resolved_external_storage"] is True
        assert payload["external_storage_supported"] is True
        assert payload["direct_source_symlinks_rejected"] is True

        direct_root = base / "direct_source_repository"
        direct_root.mkdir()
        direct_runtime = direct_root / "runtime_service"
        direct_runtime.mkdir()
        (direct_runtime / "service_state.json").symlink_to(state)

        direct_payload = RuntimeHealthAdapter(root=direct_root).read()
        direct_section = direct_payload["sections"]["runtime_service"]
        assert direct_section["availability"] == "invalid"
        assert direct_section["error_type"] == (
            "DirectSourceSymlinkRejected"
        )

    print("OIF2_3C_EXTERNAL_STORAGE_PATH_POLICY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
