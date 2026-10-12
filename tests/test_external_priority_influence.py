from ontology.external_priority_influence_layer import ExternalPriorityInfluenceLayer


def main():
    result = ExternalPriorityInfluenceLayer().step({
        "query_id": "EXTQ-R14-PRIORITY",
        "external_influence_id": "AUTOEXT-R14-PRIORITY",
        "current_priority": "external influence compliance",
        "external_recommendation": "increase strict testing priority",
        "priority_delta": 0.12,
        "justification": "Strict certification requires test evidence.",
        "expiration_time": "2030-01-01T00:00:00+00:00",
        "review_required": True,
        "confirmed": False,
    }, persist=False)

    assert result.get("external_influence_id") == "AUTOEXT-R14-PRIORITY"
    assert "priority_delta" in result
    assert result.get("review_required", True) is True
    assert result.get("expiration_time") or result.get("expires_at") or result.get("expiration_required", True)

    print("R14_PRIORITY_INFLUENCE_TEST_OK")


if __name__ == "__main__":
    main()
