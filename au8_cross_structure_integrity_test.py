from ontology.comparative_dashboard import ComparativeDashboard


def extract_ids(value):
    if isinstance(value, dict):
        return {str(key) for key in value}

    if isinstance(value, list):
        ids = set()

        for item in value:
            if isinstance(item, str):
                ids.add(item)
                continue

            if not isinstance(item, dict):
                continue

            for key in (
                "architecture_id",
                "profile_id",
                "id",
                "name",
            ):
                if key in item:
                    ids.add(str(item[key]))
                    break

        return ids

    return set()


def extract_medoid_ids(value):
    if isinstance(value, dict):
        return {
            str(item)
            for item in value.values()
            if item is not None
        }

    return extract_ids(value)


def main():
    r = ComparativeDashboard().step(
        inputs={},
        persist=False,
    )

    registry_ids = extract_ids(
        r["architecture_registry"]
    )

    profile_ids = extract_ids(
        r["rf_profiles"]
    )

    assignments = r["cluster_assignments"]

    if isinstance(assignments, dict):
        assignment_ids = {
            str(key)
            for key in assignments
        }
    else:
        assignment_ids = extract_ids(assignments)

    medoid_ids = extract_medoid_ids(
        r["medoids"]
    )

    outlier_ids = extract_ids(
        r["outliers"]
    )

    assert registry_ids
    assert profile_ids
    assert assignment_ids

    assert registry_ids == profile_ids
    assert registry_ids == assignment_ids

    assert medoid_ids <= registry_ids
    assert outlier_ids <= registry_ids

    assert r["dashboard_summary"]["architecture_count"] == len(
        registry_ids
    )
    assert r["dashboard_summary"]["profile_count"] == len(
        profile_ids
    )

    assert 0.0 <= float(
        r["coverage"]["taxonomy"]
    ) <= 1.0

    assert 0.0 <= float(
        r["coverage"]["profiles_mean"]
    ) <= 1.0

    print("AU8_CROSS_STRUCTURE_INTEGRITY_OK")


if __name__ == "__main__":
    main()
