SCHEDULER_INTERACTION_REGISTRY = {

    "asynchronous_pluralistic_scheduler": {
        "compatible_with": [
            "historical_divergence_scheduler",
            "autonomous_runtime_scheduler",
        ],

        "interaction_mode":
            "partial_coordination",
    },

    "fragmented_resilience_scheduler": {
        "compatible_with": [
            "autonomous_runtime_scheduler",
        ],

        "interaction_mode":
            "partition_resilience",
    },

    "historical_divergence_scheduler": {
        "compatible_with": [
            "asynchronous_pluralistic_scheduler",
        ],

        "interaction_mode":
            "historical_branching",
    },

    "autonomous_runtime_scheduler": {
        "compatible_with": [
            "fragmented_resilience_scheduler",
            "asynchronous_pluralistic_scheduler",
        ],

        "interaction_mode":
            "local_autonomy",
    },
}
