from ontology.external_commit_traceability_hook import ExternalCommitTraceabilityHook


def main():
    hook = ExternalCommitTraceabilityHook().step({
        "external_influence_id": "AUTOEXT-R14-COMMIT",
        "source_id": "OpenRouter",
        "external_revision_id": "EXTREV-R14-COMMIT",
        "commit_id": "COMMIT-R14-COMMIT",
        "patch_scope": ["tests/test_external_commit_traceability.py"],
        "commit_rationale": "Strict traceability test for governed external influence.",
        "rollback_plan": ["revert COMMIT-R14-COMMIT"],
        "audit_reference": "DECISION-R14-COMMIT",
        "direct_write": False,
    }, persist=False)

    assert hook["success"] is True
    assert hook["external_influence_id"] == "AUTOEXT-R14-COMMIT"
    assert hook["commit_id"] == "COMMIT-R14-COMMIT"
    assert hook["direct_write_allowed"] is False
    assert hook["traceability_decision"] in {
        "traceability_complete",
        "traceability_partial",
        "traceability_missing",
    }
    assert hook["commit_traceability_score"] >= 0.0

    print("R14_COMMIT_TRACEABILITY_TEST_OK")


if __name__ == "__main__":
    main()
