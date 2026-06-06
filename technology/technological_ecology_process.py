# technology/technological_ecology_process.py

from technology.distributed_technological_ecology import (
    DistributedTechnologicalEcology,
)


class TechnologicalEcologyProcess:
    """
    Process integrating distributed technological ecology
    into the main cognitive cycle.
    """

    def __init__(self):
        # =====================================================
        # DISTRIBUTED TECHNOLOGY
        # =====================================================

        self.distributed_technological_ecology = (
            DistributedTechnologicalEcology()
        )

    # =========================================================
    # STEP
    # =========================================================

    def step(
        self,
        agents,
    ):
        """
        Execute one technological ecology step.
        """

        self.distributed_technological_ecology.update(
            agents
        )