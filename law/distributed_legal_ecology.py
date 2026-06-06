# law/distributed_legal_ecology.py

from law.local_normative_regime import LocalNormativeRegime


class DistributedLegalEcology:
    """
    Distributed legal ecology.

    This module models a population of local normative regimes evolving
    without any central legal authority, universal law, or globally
    consistent normative ontology.

    Each regime:
    - generates local norms,
    - accumulates jurisprudence,
    - interacts with partially incompatible regimes,
    - stabilizes temporarily,
    - may collapse and reform.
    """

    def __init__(self, regime_count=6):
        # =====================================================
        # LOCAL NORMATIVE REGIMES
        # =====================================================

        self.regimes = []

        for i in range(regime_count):
            regime = LocalNormativeRegime(
                regime_id=f"normative_{i}"
            )
            self.regimes.append(regime)

        # =====================================================
        # ECOLOGICAL HISTORY
        # =====================================================

        self.cycle = 0

    # =========================================================
    # MAIN EVOLUTION
    # =========================================================

    def update(self):
        """
        Update the distributed legal ecology.

        Process:
        1. Local pairwise interactions.
        2. Local regime updates.
        3. Advance ecological cycle.
        """
        self._perform_interactions()

        for regime in self.regimes:
            regime.update()

        self.cycle += 1

    # =========================================================
    # INTERACTIONS
    # =========================================================

    def _perform_interactions(self):
        """
        Each regime interacts with its next neighbor in a circular topology.
        """
        if len(self.regimes) < 2:
            return

        n = len(self.regimes)

        for i in range(n):
            current = self.regimes[i]
            neighbor = self.regimes[(i + 1) % n]

            current.interact_with(neighbor)

    # =========================================================
    # AGGREGATED OBSERVATION
    # =========================================================

    def get_state(self):
        """
        Return aggregate indicators for the legal ecology.
        """
        if not self.regimes:
            return {
                "cycle": self.cycle,
                "regime_count": 0,
                "active_regimes": 0,
                "collapsed_regimes": 0,
                "average_legitimacy": 0.0,
                "average_stability": 0.0,
                "average_jurisprudence": 0.0,
                "average_conflict": 0.0,
                "average_compatibility": 0.0,
                "total_collapses": 0,
                "total_reformations": 0,
            }

        active = 0
        collapsed = 0

        legitimacy_sum = 0.0
        stability_sum = 0.0
        jurisprudence_sum = 0.0
        conflict_sum = 0.0
        compatibility_sum = 0.0

        total_collapses = 0
        total_reformations = 0

        for regime in self.regimes:
            state = regime.get_state()

            if state["status"] == "active":
                active += 1
            else:
                collapsed += 1

            legitimacy_sum += state["normative_legitimacy"]
            stability_sum += state["stability"]
            jurisprudence_sum += state["jurisprudence_density"]
            conflict_sum += state["internal_conflict"]
            compatibility_sum += state["compatibility_index"]

            total_collapses += state["collapse_count"]
            total_reformations += state["reformation_count"]

        count = len(self.regimes)

        return {
            "cycle": self.cycle,
            "regime_count": count,
            "active_regimes": active,
            "collapsed_regimes": collapsed,
            "average_legitimacy": legitimacy_sum / count,
            "average_stability": stability_sum / count,
            "average_jurisprudence": jurisprudence_sum / count,
            "average_conflict": conflict_sum / count,
            "average_compatibility": compatibility_sum / count,
            "total_collapses": total_collapses,
            "total_reformations": total_reformations,
        }

    # =========================================================
    # DETAILED OBSERVATION
    # =========================================================

    def get_regime_states(self):
        """
        Return detailed state for every local normative regime.
        """
        return [
            regime.get_state()
            for regime in self.regimes
        ]