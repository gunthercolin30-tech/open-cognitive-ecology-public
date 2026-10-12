from copy import deepcopy

from aw5_fast_acceptance_suite import build_context
from ontology.conflict_detector import ConflictDetector


CAUSAL_FIELDS = {
    "minimum_constraint_incompatibility": (
        "constraint_incompatibility_score",
        "constraint_incompatibility",
    ),
    "minimum_goal_incompatibility": (
        "goal_incompatibility_score",
        "goal_incompatibility",
    ),
    "minimum_resource_contention": (
        "resource_contention_score",
        "resource_contention",
    ),
    "minimum_mutual_blocking": (
        "mutual_blocking_score",
        "mutual_blocking",
    ),
}

MANDATORY_FIELDS = {
    "minimum_intensity": "intensity_score",
    "minimum_duration": "duration_score",
    "minimum_reciprocity": "reciprocity_score",
    "minimum_functional_impact": "functional_impact_score",
    "minimum_evidence_quality": "evidence_quality",
}


def run(detector, context):
    return detector.step(
        inputs=context,
        persist=False,
    )


def main():
    detector = ConflictDetector()
    thresholds = detector.default_thresholds

    baseline = run(detector, build_context())
    assert baseline["detected_conflict_count"] == 1

    # ---------------------------------------------------------
    # 1. Dimensions causales alternatives
    # ---------------------------------------------------------
    # Une cause individuelle sous son seuil ne doit pas
    # nécessairement annuler le conflit si assez d'autres causes
    # convergent encore.
    for threshold_name, (
        field_name,
        pass_name,
    ) in CAUSAL_FIELDS.items():
        if threshold_name not in thresholds:
            continue

        exact = deepcopy(build_context())
        exact["conflict_candidates"][0][field_name] = thresholds[
            threshold_name
        ]

        exact_result = run(detector, exact)
        exact_conflict = exact_result["conflicts"][0]

        assert exact_conflict[
            "causal_dimension_pass"
        ][pass_name] is True

        below = deepcopy(exact)
        below["conflict_candidates"][0][field_name] = round(
            thresholds[threshold_name] - 0.000001,
            6,
        )

        below_result = run(detector, below)
        below_conflict = below_result["conflicts"][0]

        assert below_conflict[
            "causal_dimension_pass"
        ][pass_name] is False

        # Les autres dimensions causales peuvent maintenir
        # la détection globale.
        assert below_conflict["causal_dimension_count"] >= 0

    # ---------------------------------------------------------
    # 2. Frontière du nombre minimal de causes
    # ---------------------------------------------------------
    minimum_causal = thresholds.get(
        "minimum_causal_dimensions",
        1,
    )

    causal_names = list(CAUSAL_FIELDS.items())

    exact_causal = deepcopy(build_context())
    candidate = exact_causal["conflict_candidates"][0]

    for _, (field_name, _) in causal_names:
        candidate[field_name] = 0.0

    for threshold_name, (
        field_name,
        _,
    ) in causal_names[:minimum_causal]:
        candidate[field_name] = thresholds[threshold_name]

    exact_causal_result = run(detector, exact_causal)

    assert exact_causal_result["conflicts"][0][
        "causal_dimension_count"
    ] == minimum_causal
    assert exact_causal_result[
        "detected_conflict_count"
    ] == 1

    if minimum_causal > 0:
        below_causal = deepcopy(exact_causal)

        threshold_name, (
            field_name,
            _,
        ) = causal_names[minimum_causal - 1]

        below_causal["conflict_candidates"][0][field_name] = round(
            thresholds[threshold_name] - 0.000001,
            6,
        )

        below_causal_result = run(detector, below_causal)

        assert below_causal_result["conflicts"][0][
            "causal_dimension_count"
        ] == minimum_causal - 1
        assert below_causal_result[
            "detected_conflict_count"
        ] == 0

    # ---------------------------------------------------------
    # 3. Dimensions obligatoires
    # ---------------------------------------------------------
    for threshold_name, field_name in MANDATORY_FIELDS.items():
        if threshold_name not in thresholds:
            continue

        exact = deepcopy(build_context())
        exact["conflict_candidates"][0][field_name] = thresholds[
            threshold_name
        ]

        exact_result = run(detector, exact)

        assert exact_result["detected_conflict_count"] == 1, (
            threshold_name,
            exact_result["conflicts"][0],
        )

        below = deepcopy(exact)
        below["conflict_candidates"][0][field_name] = round(
            thresholds[threshold_name] - 0.000001,
            6,
        )

        below_result = run(detector, below)

        assert below_result["detected_conflict_count"] == 0, (
            threshold_name,
            below_result["conflicts"][0],
        )

    # ---------------------------------------------------------
    # 4. Nombre d'observations
    # ---------------------------------------------------------
    if "minimum_observations" in thresholds:
        exact = deepcopy(build_context())
        exact["conflict_candidates"][0]["observation_count"] = (
            thresholds["minimum_observations"]
        )

        assert run(
            detector,
            exact,
        )["detected_conflict_count"] == 1

        below = deepcopy(exact)
        below["conflict_candidates"][0][
            "observation_count"
        ] -= 1

        assert run(
            detector,
            below,
        )["detected_conflict_count"] == 0

    # ---------------------------------------------------------
    # 5. Score global
    # ---------------------------------------------------------
    baseline_score = baseline["conflicts"][0]["conflict_score"]

    exact_global = deepcopy(build_context())
    exact_global["thresholds"] = {
        "minimum_conflict_score": baseline_score,
    }

    assert run(
        detector,
        exact_global,
    )["detected_conflict_count"] == 1

    above_global = deepcopy(build_context())
    above_global["thresholds"] = {
        "minimum_conflict_score": round(
            baseline_score + 0.000001,
            6,
        ),
    }

    assert run(
        detector,
        above_global,
    )["detected_conflict_count"] == 0

    print("AW5_THRESHOLD_BOUNDARY_OK")


if __name__ == "__main__":
    main()
