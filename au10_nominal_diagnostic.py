from pprint import pprint

from ontology.comparative_science_certifier import (
    ComparativeScienceCertifier,
)


def main():
    certifier = ComparativeScienceCertifier()
    sources = certifier._build_sources()
    result = certifier.step(
        inputs=sources,
        persist=False,
    )

    print("AU10_STATUS:")
    print(result["comparative_science_certification_status"])

    print("\nFAILED_CHECKS:")
    failed = {
        key: value
        for key, value in result["certification_checks"].items()
        if value is not True
    }
    pprint(failed)

    print("\nCERTIFICATION_CHECKS:")
    pprint(result["certification_checks"])

    print("\nMODULE_STATUSES:")
    pprint(result["module_statuses"])

    print("\nMODULE_COMPLETENESS:")
    pprint(result["module_completeness"])

    dashboard = sources["comparative_dashboard"]
    history = sources["comparative_history"]

    print("\nTHRESHOLDS:")
    pprint({
        "coverage_score": result["coverage_score"],
        "coverage_required": 0.30,
        "data_quality_score": result["data_quality_score"],
        "data_quality_required": 0.30,
    })

    print("\nDASHBOARD_HASH:")
    print(dashboard.get("dashboard_hash"))

    print("\nHISTORY_DASHBOARD_HASH:")
    print(history.get("dashboard_hash"))

    print("\nHISTORY_SNAPSHOT_HASH:")
    print(history.get("snapshot_hash"))

    print("\nHISTORY_RECORD_HASH:")
    print(history.get("record_hash"))

    print("\nCHAIN_INTEGRITY:")
    pprint(history.get("chain_integrity"))

    print("\nHISTORY_CHANGE_SET:")
    pprint(history.get("change_set"))

    print("\nEXPORT_INTEGRITY:")
    pprint(dashboard.get("export_integrity"))

    print("\nAUDITABILITY:")
    pprint(dashboard.get("auditability"))

    print("\nGUARD_COMPLIANCE:")
    pprint(result["guard_compliance"])


if __name__ == "__main__":
    main()
