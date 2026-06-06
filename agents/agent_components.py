# agents/agent_components.py

from agents.components.phenomenology_component import (
    PhenomenologyComponent,
)
from agents.components.civilization_component import (
    CivilizationComponent,
)
from agents.components.mobility_component import (
    MobilityComponent,
)
from agents.components.political_component import (
    PoliticalComponent,
)
from agents.components.technological_component import (
    TechnologicalComponent,
)
from agents.components.scientific_component import (
    ScientificComponent,
)
from agents.components.educational_component import (
    EducationalComponent,
)
from agents.components.media_component import (
    MediaComponent,
)
from agents.components.health_component import (
    HealthComponent,
)
from agents.components.demographic_component import (
    DemographicComponent,
)
from agents.components.energy_component import (
    EnergyComponent,
)

from law.distributed_legal_ecology import (
    DistributedLegalEcology,
)
from cultural.distributed_cultural_ecology import (
    DistributedCulturalEcology,
)
from language.local_language_regime import (
    LocalLanguageRegime,
)
from language.distributed_language_ecology import (
    DistributedLanguageEcology,
)


def initialize_components(agent, name):
    """
    Initialize all components and distributed ecologies
    attached to a PersistentAgent.
    """

    # =====================================================
    # CORE COMPONENTS
    # =====================================================

    agent.phenomenology = (
        PhenomenologyComponent()
    )

    agent.civilization = (
        CivilizationComponent()
    )

    agent.mobility = (
        MobilityComponent()
    )

    agent.politics = (
        PoliticalComponent()
    )

    agent.technological_component = (
        TechnologicalComponent()
    )

    agent.scientific_component = (
        ScientificComponent()
    )

    agent.educational_component = (
        EducationalComponent()
    )

    agent.media_component = (
        MediaComponent()
    )

    agent.health_component = (
        HealthComponent()
    )

    agent.demographic_component = (
        DemographicComponent()
    )

    agent.energy_component = (
        EnergyComponent()
    )

    # =====================================================
    # DISTRIBUTED LEGAL ECOLOGY
    # =====================================================

    agent.legal_ecology = (
        DistributedLegalEcology()
    )

    # =====================================================
    # DISTRIBUTED CULTURAL ECOLOGY
    # =====================================================

    agent.cultural_ecology = (
        DistributedCulturalEcology()
    )

    # =====================================================
    # LOCAL LANGUAGE REGIME
    # =====================================================

    agent.language_regime = (
        LocalLanguageRegime(
            name=name
        )
    )

    # =====================================================
    # DISTRIBUTED LANGUAGE ECOLOGY
    # =====================================================

    agent.language_ecology = (
        DistributedLanguageEcology()
    )