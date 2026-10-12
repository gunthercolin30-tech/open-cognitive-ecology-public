from __future__ import annotations

from oif.application.shell_service import (
    OIF2ReadOnlyApplicationService,
    ProviderSpec,
)


def broken_provider() -> dict[str, object]:
    raise FileNotFoundError("simulated source absence")


def main() -> int:
    service = OIF2ReadOnlyApplicationService(
        providers=(
            ProviderSpec("missing-source", "system", broken_provider),
        ),
    )
    snapshot = service.snapshot()
    assert snapshot["status"] == "degraded"
    assert snapshot["read_only"] is True
    assert len(snapshot["degraded_providers"]) == 1
    assert snapshot["cards"][0]["payload"]["status"] == "unavailable"

    try:
        OIF2ReadOnlyApplicationService(
            providers=(
                ProviderSpec("duplicate", "science", lambda: {}),
                ProviderSpec("duplicate", "system", lambda: {}),
            ),
        )
    except ValueError:
        pass
    else:
        raise AssertionError("duplicate providers must fail closed")

    try:
        OIF2ReadOnlyApplicationService(
            providers=(ProviderSpec("bad-zone", "unknown", lambda: {}),),
        ).snapshot()
    except ValueError:
        pass
    else:
        raise AssertionError("unknown zones must fail closed")

    print("OIF2_2_READ_ONLY_SHELL_DEGRADATION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
