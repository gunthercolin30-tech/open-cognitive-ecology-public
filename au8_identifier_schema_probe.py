from pprint import pprint

from ontology.comparative_dashboard import ComparativeDashboard


def main():
    result = ComparativeDashboard().step(
        inputs={},
        persist=False,
    )

    print("ARCHITECTURE_REGISTRY:")
    pprint(result["architecture_registry"])

    print("\nRF_PROFILES:")
    pprint(result["rf_profiles"])

    print("\nCLUSTER_ASSIGNMENTS:")
    pprint(result["cluster_assignments"])

    print("\nMEDOIDS:")
    pprint(result["medoids"])

    print("\nOUTLIERS:")
    pprint(result["outliers"])


if __name__ == "__main__":
    main()
