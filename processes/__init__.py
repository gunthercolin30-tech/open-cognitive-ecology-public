# processes/__init__.py

from processes.memory_consolidation_process import (
    MemoryConsolidationProcess
)

from processes.salience_propagation_process import (
    SaliencePropagationProcess
)

from processes.spontaneous_reactivation_process import (
    SpontaneousReactivationProcess
)

from processes.attractor_formation_process import (
    AttractorFormationProcess
)

from processes.competitive_tension_process import (
    CompetitiveTensionProcess
)

from processes.bifurcation_process import (
    BifurcationProcess
)

from processes.legal_ecology_process import (
    LegalEcologyProcess
)

__all__ = [
    "MemoryConsolidationProcess",
    "SaliencePropagationProcess",
    "SpontaneousReactivationProcess",
    "AttractorFormationProcess",
    "CompetitiveTensionProcess",
    "BifurcationProcess",
    "LegalEcologyProcess",
]