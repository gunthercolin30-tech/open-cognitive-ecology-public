# cultural/cultural_ecology_process.py

from cultural.distributed_cultural_ecology import (
    DistributedCulturalEcology,
)


class CulturalEcologyProcess:
    """
    Scheduler-compatible wrapper for the distributed
    cultural ecology.

    This process models:

    - local traditions
    - collective narratives
    - symbolic transmission
    - imitation and innovation
    - cultural memory
    - fragmentation and disappearance

    There is:
    - no universal culture
    - no global narrative
    - no final synthesis
    """

    def __init__(
        self,
        culture_count=4,
    ):
        self.cultural_ecology = (
            DistributedCulturalEcology(
                culture_count=culture_count
            )
        )

    def update(
        self,
        graph=None,
    ):
        """
        Advance the distributed cultural ecology.

        The graph argument is accepted for interface
        compatibility with other scheduler processes.
        """

        self.cultural_ecology.step()

        self.cultural_ecology.debug_print()

    def get_state(self):
        """
        Return aggregate cultural indicators.
        """

        return {
            "cultural_alive_count": (
                self.cultural_ecology.get_alive_count()
            ),
            "cultural_fragmentation": (
                self.cultural_ecology.get_average_fragmentation()
            ),
            "cultural_memory": (
                self.cultural_ecology.get_average_memory()
            ),
        }