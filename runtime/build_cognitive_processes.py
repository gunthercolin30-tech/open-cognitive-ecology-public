# runtime/build_cognitive_processes.py

from processes.memory_consolidation_process import (
    MemoryConsolidationProcess,
)
from processes.salience_propagation_process import (
    SaliencePropagationProcess,
)
from processes.spontaneous_reactivation_process import (
    SpontaneousReactivationProcess,
)
from processes.attractor_formation_process import (
    AttractorFormationProcess,
)
from processes.competitive_tension_process import (
    CompetitiveTensionProcess,
)
from processes.tension_redistribution_process import (
    TensionRedistributionProcess,
)
from processes.temporal_ecology_process import (
    TemporalEcologyProcess,
)
from processes.spatial_dynamics_process import (
    SpatialDynamicsProcess,
)
from processes.climatic_ecology_process import (
    ClimaticEcologyProcess,
)
from processes.regional_constraint_process import (
    RegionalConstraintProcess,
)
from processes.political_ecology_process import (
    PoliticalEcologyProcess,
)
from processes.legal_ecology_process import (
    LegalEcologyProcess,
)


def build_cognitive_processes(
    graph,
    propagation_engine,
):
    """
    Build cognitive and graph-bound ecologies.

    Covered operational ecologies:
    - cognitive
    - temporal
    - spatial
    - climatic
    - constraints
    - political
    - legal
    """

    # =====================================================
    # COGNITIVE ECOLOGY
    # =====================================================

    memory_process = (
        MemoryConsolidationProcess(
            graph
        )
    )

    salience_process = (
        SaliencePropagationProcess(
            graph,
            propagation_engine,
        )
    )

    reactivation_process = (
        SpontaneousReactivationProcess(
            graph,
            propagation_engine,
        )
    )

    attractor_process = (
        AttractorFormationProcess(
            graph
        )
    )

    competition_process = (
        CompetitiveTensionProcess(
            graph
        )
    )

    tension_redistribution_process = (
        TensionRedistributionProcess(
            graph
        )
    )

    # =====================================================
    # GRAPH-BOUND ECOLOGIES
    # =====================================================

    temporal_ecology_process = (
        TemporalEcologyProcess(
            graph
        )
    )

    spatial_dynamics_process = (
        SpatialDynamicsProcess(
            graph
        )
    )

    climatic_ecology_process = (
        ClimaticEcologyProcess(
            graph
        )
    )

    regional_constraint_process = (
        RegionalConstraintProcess(
            graph
        )
    )

    political_ecology_process = (
        PoliticalEcologyProcess(
            graph
        )
    )

    legal_ecology_process = (
        LegalEcologyProcess(
            graph
        )
    )

    return {
        "memory_process": (
            memory_process
        ),
        "salience_process": (
            salience_process
        ),
        "reactivation_process": (
            reactivation_process
        ),
        "attractor_process": (
            attractor_process
        ),
        "competition_process": (
            competition_process
        ),
        "tension_redistribution_process": (
            tension_redistribution_process
        ),
        "temporal_ecology_process": (
            temporal_ecology_process
        ),
        "spatial_dynamics_process": (
            spatial_dynamics_process
        ),
        "climatic_ecology_process": (
            climatic_ecology_process
        ),
        "regional_constraint_process": (
            regional_constraint_process
        ),
        "political_ecology_process": (
            political_ecology_process
        ),
        "legal_ecology_process": (
            legal_ecology_process
        ),
    }