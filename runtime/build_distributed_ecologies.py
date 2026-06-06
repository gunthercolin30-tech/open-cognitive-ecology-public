# runtime/build_distributed_ecologies.py

from economy.economic_ecology_process import (
    EconomicEcologyProcess,
)

from cultural.cultural_ecology_process import (
    CulturalEcologyProcess,
)

from language.linguistic_ecology_process import (
    LinguisticEcologyProcess,
)

from technology.technological_ecology_process import (
    TechnologicalEcologyProcess,
)

from science.scientific_ecology_process import (
    ScientificEcologyProcess,
)

from education.educational_ecology_process import (
    EducationalEcologyProcess,
)

from media.media_ecology_process import (
    MediaEcologyProcess,
)


def build_distributed_ecologies():
    """
    Build distributed ecologies.

    Covered operational ecologies:
    - economic
    - cultural
    - linguistic
    - technological
    - scientific
    - educational
    - media
    """

    economic_ecology_process = (
        EconomicEcologyProcess(
            regime_count=4
        )
    )

    cultural_ecology_process = (
        CulturalEcologyProcess(
            culture_count=4
        )
    )

    linguistic_ecology_process = (
        LinguisticEcologyProcess()
    )

    technological_ecology_process = (
        TechnologicalEcologyProcess()
    )

    scientific_ecology_process = (
        ScientificEcologyProcess()
    )

    educational_ecology_process = (
        EducationalEcologyProcess()
    )

    media_ecology_process = (
        MediaEcologyProcess()
    )

    return {
        "economic_ecology_process": (
            economic_ecology_process
        ),
        "cultural_ecology_process": (
            cultural_ecology_process
        ),
        "linguistic_ecology_process": (
            linguistic_ecology_process
        ),
        "technological_ecology_process": (
            technological_ecology_process
        ),
        "scientific_ecology_process": (
            scientific_ecology_process
        ),
        "educational_ecology_process": (
            educational_ecology_process
        ),
        "media_ecology_process": (
            media_ecology_process
        ),
    }