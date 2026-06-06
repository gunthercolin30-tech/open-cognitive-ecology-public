# runtime/register_processes.py


def register_processes(
    scheduler,
    processes,
):
    """
    Register all processes that can be executed directly
    by the scheduler.
    """

    # =====================================================
    # COGNITIVE CORE
    # =====================================================

    scheduler.register(
        processes["memory_process"]
    )
    scheduler.register(
        processes["salience_process"]
    )
    scheduler.register(
        processes["reactivation_process"]
    )
    scheduler.register(
        processes["attractor_process"]
    )
    scheduler.register(
        processes["competition_process"]
    )
    scheduler.register(
        processes[
            "tension_redistribution_process"
        ]
    )

    # =====================================================
    # GRAPH-BOUND ECOLOGIES
    # =====================================================

    scheduler.register(
        processes[
            "temporal_ecology_process"
        ]
    )
    scheduler.register(
        processes[
            "spatial_dynamics_process"
        ]
    )
    scheduler.register(
        processes[
            "climatic_ecology_process"
        ]
    )
    scheduler.register(
        processes[
            "regional_constraint_process"
        ]
    )
    scheduler.register(
        processes[
            "political_ecology_process"
        ]
    )
    scheduler.register(
        processes[
            "legal_ecology_process"
        ]
    )

    # =====================================================
    # DISTRIBUTED ECOLOGIES
    # =====================================================

    scheduler.register(
        processes[
            "economic_ecology_process"
        ]
    )
    scheduler.register(
        processes[
            "cultural_ecology_process"
        ]
    )
    scheduler.register(
        processes[
            "linguistic_ecology_process"
        ]
    )
    scheduler.register(
        processes[
            "technological_ecology_process"
        ]
    )
    scheduler.register(
        processes[
            "scientific_ecology_process"
        ]
    )
    scheduler.register(
        processes[
            "educational_ecology_process"
        ]
    )
    scheduler.register(
        processes[
            "media_ecology_process"
        ]
    )

    # =====================================================
    # NOTE
    # =====================================================
    # Agent-based ecologies (health, demographic,
    # energy) are executed explicitly in run_loop.py.