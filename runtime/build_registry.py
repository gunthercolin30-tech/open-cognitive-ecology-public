# runtime/build_registry.py


def build_operational_registry(
    processes,
):
    """
    Build the canonical registry of the 17 operational
    ecologies.
    """

    return {
        # 1. Cognitive ecology
        "cognitive": {
            "memory_process": (
                processes["memory_process"]
            ),
            "salience_process": (
                processes["salience_process"]
            ),
            "reactivation_process": (
                processes[
                    "reactivation_process"
                ]
            ),
            "attractor_process": (
                processes["attractor_process"]
            ),
            "competition_process": (
                processes[
                    "competition_process"
                ]
            ),
            "tension_redistribution_process": (
                processes[
                    "tension_redistribution_process"
                ]
            ),
        },

        # 2–17 Operational ecologies
        "temporal": (
            processes[
                "temporal_ecology_process"
            ]
        ),
        "spatial": (
            processes[
                "spatial_dynamics_process"
            ]
        ),
        "climatic": (
            processes[
                "climatic_ecology_process"
            ]
        ),
        "constraints": (
            processes[
                "regional_constraint_process"
            ]
        ),
        "political": (
            processes[
                "political_ecology_process"
            ]
        ),
        "legal": (
            processes[
                "legal_ecology_process"
            ]
        ),
        "cultural": (
            processes[
                "cultural_ecology_process"
            ]
        ),
        "economic": (
            processes[
                "economic_ecology_process"
            ]
        ),
        "linguistic": (
            processes[
                "linguistic_ecology_process"
            ]
        ),
        "technological": (
            processes[
                "technological_ecology_process"
            ]
        ),
        "scientific": (
            processes[
                "scientific_ecology_process"
            ]
        ),
        "educational": (
            processes[
                "educational_ecology_process"
            ]
        ),
        "media": (
            processes[
                "media_ecology_process"
            ]
        ),
        "health": (
            processes[
                "health_ecology_process"
            ]
        ),
        "demographic": (
            processes[
                "demographic_ecology_process"
            ]
        ),
        "energy": (
            processes[
                "energy_ecology_process"
            ]
        ),
    }