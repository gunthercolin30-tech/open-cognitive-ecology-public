from ontology.external_decision_record_extension import ExternalDecisionRecordExtension


def main():
    decision = ExternalDecisionRecordExtension().step({
        "query_id": "EXTQ-R14-DECISION-GATE",
        "external_influence_id": "AUTOEXT-R14-DECISION-GATE",
        "source_id": "OpenRouter",
        "decision_type": "external_influence_decision",
        "decision_rationale": "External influence requires explicit governed traceability.",
        "traceability_reference": "AUTOEXT-R14-DECISION-GATE",
        "human_approval": "required",
    }, persist=False)

    assert decision["success"] is True
    assert decision["external_influence_id"] == "AUTOEXT-R14-DECISION-GATE"
    assert decision["external_decision_id"].startswith("EXTERNAL-DECISION-")
    assert decision["decision_record_status"] in {
        "decision_record_ready",
        "decision_record_partial",
        "decision_record_missing",
    }
    assert decision["direct_write_allowed"] is False

    print("R14_DECISION_GATE_TEST_OK")


if __name__ == "__main__":
    main()
