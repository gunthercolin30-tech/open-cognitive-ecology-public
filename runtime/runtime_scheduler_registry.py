SCHEDULER_REGISTRY = {

    "asynchronous_pluralistic_scheduler": {
        "temporal_policy":
            "asynchronous",

        "coordination_mode":
            "distributed",

        "global_consensus":
            False,

        "priority":
            "pluralistic_divergence",
    },

    "fragmented_resilience_scheduler": {
        "temporal_policy":
            "fragmented",

        "coordination_mode":
            "partitioned",

        "global_consensus":
            False,

        "priority":
            "resilience_after_fragmentation",
    },

    "historical_divergence_scheduler": {
        "temporal_policy":
            "multi_history",

        "coordination_mode":
            "branching",

        "global_consensus":
            False,

        "priority":
            "historical_pluralism",
    },

    "autonomous_runtime_scheduler": {
        "temporal_policy":
            "autonomous",

        "coordination_mode":
            "local_runtime",

        "global_consensus":
            False,

        "priority":
            "runtime_independence",
    },
}
