#!/usr/bin/env python3
from __future__ import annotations

import time
from pathlib import Path

from ontology import rf_star_definition_engine as module
from ontology.rf_star_definition_engine import RFStarDefinitionEngine

NAMES = tuple(module._CANONICAL_LATEST_JSON_PATHS)


def forbidden(*args, **kwargs):
    raise AssertionError("repository-wide glob/rglob must not be called")


def main() -> None:
    original_glob = Path.glob
    original_rglob = Path.rglob
    Path.glob = forbidden
    Path.rglob = forbidden
    try:
        module._LATEST_JSON_CACHE.clear()
        module._LATEST_JSON_MISS_CACHE.clear()

        started = time.monotonic()
        for name in NAMES:
            result = module._latest_json(name)
            assert isinstance(result, dict)
        first_elapsed = time.monotonic() - started

        started = time.monotonic()
        for name in NAMES:
            result = module._latest_json(name)
            assert isinstance(result, dict)
        cached_elapsed = time.monotonic() - started

        result = RFStarDefinitionEngine().step(
            inputs={"synthetic": True},
            persist=False,
        )
    finally:
        Path.glob = original_glob
        Path.rglob = original_rglob

    assert result["step"] == "AP2"
    assert result["rf_star_defined"] is True
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_undetermined"] is True
    assert result["functional_conclusion_only"] is True
    assert first_elapsed < 2.0, first_elapsed
    assert cached_elapsed < 0.1, cached_elapsed

    print(
        "AP2_LATEST_JSON_RESOLUTION_FAST_ACCEPTANCE_OK "
        f"first={first_elapsed:.6f}s cached={cached_elapsed:.6f}s"
    )


if __name__ == "__main__":
    main()
