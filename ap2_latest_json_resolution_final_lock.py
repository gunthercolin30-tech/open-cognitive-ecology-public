#!/usr/bin/env python3
from __future__ import annotations

import inspect
from pathlib import Path

from ontology import rf_star_definition_engine as module
from ontology.rf_star_definition_engine import RFStarDefinitionEngine


def main() -> None:
    source = inspect.getsource(module._latest_json)
    assert "ROOT.glob" not in source
    assert "ROOT.rglob" not in source
    assert "**/latest_" not in source
    assert module._CANONICAL_LATEST_JSON_PATHS

    original_glob = Path.glob
    original_rglob = Path.rglob

    def forbidden(*args, **kwargs):
        raise AssertionError("glob/rglob forbidden in AP2 final lock")

    Path.glob = forbidden
    Path.rglob = forbidden
    try:
        result = RFStarDefinitionEngine().step(
            inputs={"synthetic": True},
            persist=False,
        )
    finally:
        Path.glob = original_glob
        Path.rglob = original_rglob

    assert result["rf_star_definition_status"] == "RF_STAR_DEFINED"
    assert result["rf_star_defined"] is True
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_undetermined"] is True
    assert result["functional_conclusion_only"] is True

    print("AP2_LATEST_JSON_RESOLUTION_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
