from __future__ import annotations

from oif.application.shell_service import (
    OIF2ReadOnlyApplicationService,
    ProviderSpec,
)


def main() -> int:
    service = OIF2ReadOnlyApplicationService(
        providers=(
            ProviderSpec(
                name="validation-summary",
                zone="science",
                provider=lambda: {
                    "status": "ok",
                    "error_count": 0,
                    "functional_conclusion_only": True,
                },
            ),
        ),
    )
    snapshot = service.snapshot()
    assert snapshot["status"] == "ready"
    assert snapshot["read_only"] is True
    assert snapshot["renderer_replaceable"] is True
    assert snapshot["direct_persistence_from_renderer"] is False
    assert snapshot["shell_execution_from_renderer"] is False
    assert snapshot["provider_count"] == 1
    assert snapshot["cards"][0]["zone"] == "science"
    assert snapshot["cards"][0]["payload"]["error_count"] == 0
    assert snapshot["epistemic_invariants"]["consciousness_proven"] is False
    assert snapshot["epistemic_invariants"]["functional_conclusion_only"] is True
    print("OIF2_2_READ_ONLY_SHELL_FUNCTIONAL_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
