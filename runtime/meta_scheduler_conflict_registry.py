META_SCHEDULER_CONFLICT_REGISTRY = {

    (
        "fragmented_resilience_scheduler",
        "historical_divergence_scheduler",
    ): {
        "conflict_type":
            "temporal_fragmentation",

        "resolution_policy":
            "persistent_divergence",

        "forced_unification":
            False,
    },

    (
        "autonomous_runtime_scheduler",
        "fragmented_resilience_scheduler",
    ): {
        "conflict_type":
            "local_autonomy_conflict",

        "resolution_policy":
            "local_negotiation",

        "forced_unification":
            False,
    },

    (
        "historical_divergence_scheduler",
        "asynchronous_pluralistic_scheduler",
    ): {
        "conflict_type":
            "branching_coordination",

        "resolution_policy":
            "partial_interoperability",

        "forced_unification":
            False,
    },
}
