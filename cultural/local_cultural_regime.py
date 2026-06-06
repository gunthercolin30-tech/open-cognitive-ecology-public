# cultural/local_cultural_regime.py

import random


class LocalCulturalRegime:
    """
    Local cultural dynamics.

    This module models:

    - traditions and inherited practices
    - collective narratives
    - symbolic transmission
    - imitation and innovation
    - cultural memory
    - fragmentation and cultural disappearance

    Fundamental constraints:

    - no universal culture
    - no global narrative
    - only local and partially incompatible regimes
    - dissipative and historically unstable structures
    """

    def __init__(
        self,
        name="culture",
    ):
        self.name = name

        # =====================================================
        # CORE CULTURAL STATE
        # =====================================================

        self.tradition_strength = random.uniform(0.4, 0.9)
        self.narrative_coherence = random.uniform(0.3, 0.9)
        self.symbolic_transmission = random.uniform(0.3, 0.9)
        self.imitation_tendency = random.uniform(0.2, 0.8)
        self.innovation_tendency = random.uniform(0.1, 0.7)
        self.cultural_memory = random.uniform(0.4, 1.0)

        # =====================================================
        # FRAGMENTATION DYNAMICS
        # =====================================================

        self.fragmentation = random.uniform(0.0, 0.3)
        self.cultural_erosion = 0.0
        self.disappearance_risk = 0.0

        # =====================================================
        # HISTORICAL TRAJECTORY
        # =====================================================

        self.age = 0
        self.alive = True

    # =========================================================
    # INTERNAL DYNAMICS
    # =========================================================

    def step(self):
        """
        Advance the local cultural regime by one historical step.
        """

        if not self.alive:
            return

        self.age += 1

        # Tradition naturally decays but may be reinforced by memory.
        self.tradition_strength += (
            0.03 * (self.cultural_memory - 0.5)
            + random.uniform(-0.02, 0.02)
        )

        # Narrative coherence depends on symbolic transmission.
        self.narrative_coherence += (
            0.04 * (self.symbolic_transmission - 0.5)
            - 0.03 * self.fragmentation
            + random.uniform(-0.02, 0.02)
        )

        # Symbolic transmission depends on tradition and coherence.
        self.symbolic_transmission += (
            0.03 * (self.tradition_strength - 0.5)
            + 0.03 * (self.narrative_coherence - 0.5)
            + random.uniform(-0.02, 0.02)
        )

        # Imitation and innovation compete.
        self.imitation_tendency += random.uniform(-0.02, 0.02)
        self.innovation_tendency += random.uniform(-0.02, 0.02)

        # Memory is reinforced by successful transmission.
        self.cultural_memory += (
            0.04 * (self.symbolic_transmission - 0.5)
            - 0.02 * self.fragmentation
            + random.uniform(-0.02, 0.02)
        )

        # Fragmentation grows when coherence weakens.
        self.fragmentation += (
            0.05 * (0.5 - self.narrative_coherence)
            + 0.03 * self.innovation_tendency
            + random.uniform(-0.02, 0.02)
        )

        # Cultural erosion accumulates.
        self.cultural_erosion += max(
            0.0,
            0.03 * self.fragmentation
            + 0.03 * (0.5 - self.cultural_memory),
        )

        # Risk of disappearance.
        self.disappearance_risk = (
            0.35 * self.fragmentation
            + 0.35 * self.cultural_erosion
            + 0.30 * max(0.0, 0.4 - self.cultural_memory)
        )

        # Clamp all bounded variables.
        self._clamp()

        # Possible disappearance.
        if self.disappearance_risk > 0.95:
            if random.random() < 0.05:
                self.alive = False

    # =========================================================
    # UTILITIES
    # =========================================================

    def _clamp(self):
        self.tradition_strength = self._clip(
            self.tradition_strength
        )
        self.narrative_coherence = self._clip(
            self.narrative_coherence
        )
        self.symbolic_transmission = self._clip(
            self.symbolic_transmission
        )
        self.imitation_tendency = self._clip(
            self.imitation_tendency
        )
        self.innovation_tendency = self._clip(
            self.innovation_tendency
        )
        self.cultural_memory = self._clip(
            self.cultural_memory
        )
        self.fragmentation = self._clip(
            self.fragmentation
        )
        self.cultural_erosion = self._clip(
            self.cultural_erosion
        )
        self.disappearance_risk = self._clip(
            self.disappearance_risk
        )

    @staticmethod
    def _clip(value):
        return max(0.0, min(1.0, value))

    # =========================================================
    # EXTERNAL INTERFACE
    # =========================================================

    def get_state(self):
        return {
            "name": self.name,
            "age": self.age,
            "alive": self.alive,
            "tradition_strength": self.tradition_strength,
            "narrative_coherence": self.narrative_coherence,
            "symbolic_transmission": self.symbolic_transmission,
            "imitation_tendency": self.imitation_tendency,
            "innovation_tendency": self.innovation_tendency,
            "cultural_memory": self.cultural_memory,
            "fragmentation": self.fragmentation,
            "cultural_erosion": self.cultural_erosion,
            "disappearance_risk": self.disappearance_risk,
        }

    def debug_print(self):
        print(
            "[LOCAL_CULTURAL_REGIME]",
            self.name,
            f"tradition={self.tradition_strength:.2f}",
            f"narrative={self.narrative_coherence:.2f}",
            f"transmission={self.symbolic_transmission:.2f}",
            f"memory={self.cultural_memory:.2f}",
            f"fragmentation={self.fragmentation:.2f}",
            f"erosion={self.cultural_erosion:.2f}",
            f"risk={self.disappearance_risk:.2f}",
            f"alive={self.alive}",
        )