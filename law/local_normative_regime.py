# law/local_normative_regime.py

import random


class LocalNormativeRegime:
    """
    Local normative regime.

    This module models:
    - local norms
    - normative legitimacy
    - emergent jurisprudence
    - compatibility conflicts
    - legal stabilization and collapse

    Constraints:
    - no central legal authority
    - no universal law
    - no global normative ontology
    - only local and historically unstable regimes
    """

    def __init__(self, regime_id=None):
        self.regime_id = regime_id or f"normative_{random.randint(1000, 9999)}"

        # =====================================================
        # CORE NORMATIVE STRUCTURE
        # =====================================================

        # Set of locally valid norms
        self.local_norms = []

        # Strength of internal normative coherence
        self.normative_coherence = random.uniform(0.3, 0.9)

        # Perceived legitimacy of the regime
        self.normative_legitimacy = random.uniform(0.3, 0.9)

        # Emergent jurisprudential sedimentation
        self.jurisprudence_density = random.uniform(0.0, 0.5)

        # Degree of compatibility with neighboring regimes
        self.compatibility_index = random.uniform(0.2, 0.8)

        # Internal contradiction level
        self.internal_conflict = random.uniform(0.0, 0.4)

        # Historical stability
        self.stability = random.uniform(0.3, 0.9)

        # Dissipative erosion
        self.erosion = random.uniform(0.0, 0.2)

        # Collapse risk
        self.collapse_risk = random.uniform(0.0, 0.3)

        # Regime status
        self.status = "active"

        # Historical age
        self.age = 0

        # =====================================================
        # HISTORICAL MEMORY
        # =====================================================

        self.collapse_count = 0
        self.reformation_count = 0

        # =====================================================
        # INITIAL NORM GENERATION
        # =====================================================

        self._generate_initial_norms()

    # =========================================================
    # INITIALIZATION
    # =========================================================

    def _generate_initial_norms(self):
        base_norms = [
            "exchange",
            "property",
            "inheritance",
            "repair",
            "obligation",
            "protection",
            "exclusion",
            "arbitration",
            "compensation",
            "reciprocity",
        ]

        random.shuffle(base_norms)

        n = random.randint(3, 7)

        self.local_norms = base_norms[:n]

    # =========================================================
    # MAIN EVOLUTION
    # =========================================================

    def update(self):
        if self.status != "active":
            self._attempt_reformation()
            return

        self.age += 1

        self._evolve_legitimacy()
        self._evolve_jurisprudence()
        self._evolve_conflicts()
        self._evolve_stability()
        self._check_collapse()

    # =========================================================
    # LOCAL DYNAMICS
    # =========================================================

    def _evolve_legitimacy(self):
        delta = (
            0.03 * self.normative_coherence
            + 0.02 * self.jurisprudence_density
            - 0.04 * self.internal_conflict
            - 0.03 * self.erosion
            + random.uniform(-0.02, 0.02)
        )

        self.normative_legitimacy += delta
        self.normative_legitimacy = max(
            0.0,
            min(1.0, self.normative_legitimacy)
        )

    def _evolve_jurisprudence(self):
        delta = (
            0.02 * self.normative_legitimacy
            - 0.02 * self.erosion
            + random.uniform(-0.01, 0.02)
        )

        self.jurisprudence_density += delta
        self.jurisprudence_density = max(
            0.0,
            min(1.0, self.jurisprudence_density)
        )

    def _evolve_conflicts(self):
        delta = (
            0.04 * (1.0 - self.compatibility_index)
            + random.uniform(-0.02, 0.03)
        )

        self.internal_conflict += delta
        self.internal_conflict = max(
            0.0,
            min(1.0, self.internal_conflict)
        )

    def _evolve_stability(self):
        delta = (
            0.03 * self.normative_legitimacy
            + 0.03 * self.jurisprudence_density
            - 0.05 * self.internal_conflict
            - 0.03 * self.erosion
            + random.uniform(-0.02, 0.02)
        )

        self.stability += delta
        self.stability = max(0.0, min(1.0, self.stability))

        self.erosion += random.uniform(-0.01, 0.02)
        self.erosion = max(0.0, min(1.0, self.erosion))

        self.collapse_risk = (
            0.35 * (1.0 - self.stability)
            + 0.30 * self.internal_conflict
            + 0.20 * self.erosion
            + 0.15 * (1.0 - self.normative_legitimacy)
        )

        self.collapse_risk = max(
            0.0,
            min(1.0, self.collapse_risk)
        )

    # =========================================================
    # COLLAPSE / REFORMATION
    # =========================================================

    def _check_collapse(self):
        if self.collapse_risk > random.uniform(0.0, 1.0):
            self.status = "collapsed"
            self.collapse_count += 1

    def _attempt_reformation(self):
        probability = 0.02 + 0.10 * (1.0 - self.erosion)

        if random.random() < probability:
            self._reform()

    def _reform(self):
        self.status = "active"
        self.reformation_count += 1
        self.age = 0

        self.normative_coherence = random.uniform(0.2, 0.8)
        self.normative_legitimacy = random.uniform(0.2, 0.7)
        self.jurisprudence_density *= 0.5
        self.internal_conflict = random.uniform(0.1, 0.5)
        self.stability = random.uniform(0.2, 0.7)
        self.collapse_risk = random.uniform(0.0, 0.3)

        self._generate_initial_norms()

    # =========================================================
    # INTER-REGIME INTERACTIONS
    # =========================================================

    def interact_with(self, other_regime):
        """
        Local normative interaction without universal reconciliation.
        """
        if self.status != "active":
            return

        if other_regime.status != "active":
            return

        overlap = len(
            set(self.local_norms).intersection(
                set(other_regime.local_norms)
            )
        )

        total = max(
            1,
            len(set(self.local_norms).union(set(other_regime.local_norms)))
        )

        compatibility = overlap / total

        self.compatibility_index = (
            0.8 * self.compatibility_index
            + 0.2 * compatibility
        )

        self.compatibility_index = max(
            0.0,
            min(1.0, self.compatibility_index)
        )

    # =========================================================
    # OBSERVATION
    # =========================================================

    def get_state(self):
        return {
            "regime_id": self.regime_id,
            "status": self.status,
            "age": self.age,
            "norm_count": len(self.local_norms),
            "normative_coherence": self.normative_coherence,
            "normative_legitimacy": self.normative_legitimacy,
            "jurisprudence_density": self.jurisprudence_density,
            "compatibility_index": self.compatibility_index,
            "internal_conflict": self.internal_conflict,
            "stability": self.stability,
            "erosion": self.erosion,
            "collapse_risk": self.collapse_risk,
            "collapse_count": self.collapse_count,
            "reformation_count": self.reformation_count,
        }