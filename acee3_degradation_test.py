\
from pathlib import Path
from ontology.acee_bridge_adapter import AceeBridgeAdapter


def main() -> None:
    adapter = AceeBridgeAdapter(root=Path("/nonexistent"))
    missing = adapter.step(inputs={}, persist=False)
    assert missing["adapter_status"] == "ACEE_BRIDGE_ADAPTER_DEGRADED"
    assert missing["adapter_ready"] is False
    assert "missing_source_module" in missing["degraded_reasons"]
    assert "source_result_not_mapping" in missing["degraded_reasons"]

    unknown = adapter.step(
        inputs={"source_module": "unknown_engine", "source_result": {"status": "mystery"}},
        persist=False,
    )
    assert "unsupported_source_module" in unknown["degraded_reasons"]
    assert unknown["status"] == "unknown"
    assert unknown["functional_conclusion_only"] is True
    print("ACEE3_DEGRADATION_OK")


if __name__ == "__main__":
    main()
