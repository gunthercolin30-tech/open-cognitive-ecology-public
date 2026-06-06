# runtime/build_system.py

from runtime.build_core import (
    build_core,
)

from runtime.build_cognitive_processes import (
    build_cognitive_processes,
)

from runtime.build_distributed_ecologies import (
    build_distributed_ecologies,
)

from runtime.build_agent_ecologies import (
    build_agent_ecologies,
)

from runtime.register_processes import (
    register_processes,
)

from runtime.build_registry import (
    build_operational_registry,
)


def build_system():
    """
    Construct the complete Open Cognitive Ecology
    runtime.
    """

    # =====================================================
    # CORE INFRASTRUCTURE
    # =====================================================

    core = build_core()

    # =====================================================
    # PROCESS CONSTRUCTION
    # =====================================================

    cognitive_processes = (
        build_cognitive_processes(
            core["graph"],
            core["propagation_engine"],
        )
    )

    distributed_ecologies = (
        build_distributed_ecologies()
    )

    agent_ecologies = (
        build_agent_ecologies()
    )

    # =====================================================
    # MERGE ALL PROCESSES
    # =====================================================

    processes = {
        **cognitive_processes,
        **distributed_ecologies,
        **agent_ecologies,
    }

    # =====================================================
    # SCHEDULER REGISTRATION
    # =====================================================

    register_processes(
        core["scheduler"],
        processes,
    )

    # =====================================================
    # EXECUTION GROUPS
    # =====================================================

    graph_based_ecologies = [
        processes[
            "economic_ecology_process"
        ],
        processes[
            "cultural_ecology_process"
        ],
        processes[
            "linguistic_ecology_process"
        ],
        processes[
            "technological_ecology_process"
        ],
        processes[
            "scientific_ecology_process"
        ],
        processes[
            "educational_ecology_process"
        ],
        processes[
            "media_ecology_process"
        ],
    ]

    agent_based_ecologies = [
        processes[
            "health_ecology_process"
        ],
        processes[
            "demographic_ecology_process"
        ],
        processes[
            "energy_ecology_process"
        ],
    ]

    # =====================================================
    # CANONICAL ECOLOGY REGISTRY
    # =====================================================

    operational_ecologies = (
        build_operational_registry(
            processes
        )
    )

    # =====================================================
    # FINAL SYSTEM DICTIONARY
    # =====================================================

    return {
        **core,
        **processes,
        "graph_based_ecologies": (
            graph_based_ecologies
        ),
        "agent_based_ecologies": (
            agent_based_ecologies
        ),
        "operational_ecologies": (
            operational_ecologies
        ),
    }