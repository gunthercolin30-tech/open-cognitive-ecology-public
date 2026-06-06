# agents/components/political_component.py

import random


class PoliticalComponent:
    """
    Local political and symbolic-economic dynamics.

    This component encapsulates:
    - institutional affiliations
    - local loyalties
    - perceived legitimacy
    - symbolic wealth
    - coordination dependence
    - political fragmentation
    - institutional exclusions
    - political collapses

    It also exposes juridical placeholders for:
    - local norms
    - legitimacy regimes
    - jurisprudential accumulation
    - normative conflicts
    - legal stabilization and collapse

    No global sovereignty.
    No universal citizenship.
    No stable political identity.
    No universal legal order.
    """

    def __init__(self):

        # =====================================================
        # INSTITUTIONAL RELATIONS
        # =====================================================

        self.institutional_affiliations = set()

        self.institutional_loyalty = random.uniform(
            0.0,
            1.0,
        )

        self.perceived_legitimacy = random.uniform(
            0.2,
            1.0,
        )

        self.institutional_exclusions = set()

        # =====================================================
        # SYMBOLIC ECONOMY
        # =====================================================

        self.symbolic_wealth = random.uniform(
            0.0,
            1.0,
        )

        self.economic_preferences = {}

        self.wealth_volatility = random.uniform(
            0.0,
            0.2,
        )

        # =====================================================
        # COORDINATION DYNAMICS
        # =====================================================

        self.coordination_dependence = random.uniform(
            0.0,
            1.0,
        )

        self.political_fragmentation = 0.0

        self.political_fatigue = 0.0

        self.institutional_pressure = 0.0

        self.legitimacy_crisis = 0.0

        # =====================================================
        # RUNTIME POLITICAL FIELDS
        # =====================================================

        self.institutional_intensity = 0.0

        self.symbolic_currency = 0.0

        self.coordination_intensity = 0.0

        self.political_tension = 0.0

        self.political_affiliation = "none"

        # =====================================================
        # LOCAL COALITIONS
        # =====================================================

        self.coalition_affinities = {}

        self.active_coalitions = set()

        self.coalition_stability = 0.0

        # =====================================================
        # JURIDICAL PLACEHOLDERS
        # =====================================================

        self.local_norms = {}

        self.normative_commitment = random.uniform(
            0.0,
            1.0,
        )

        self.legal_legitimacy = random.uniform(
            0.2,
            1.0,
        )

        self.normative_conflict = 0.0

        self.jurisprudential_density = 0.0

        self.legal_fragmentation = 0.0

        self.legal_stability = random.uniform(
            0.2,
            1.0,
        )

        self.normative_exclusions = set()

        # =====================================================
        # HISTORY
        # =====================================================

        self.political_history = []

        self.legal_history = []

    # =========================================================
    # INTERNAL DYNAMICS
    # =========================================================

    def evolve(
        self,
    ):

        # =====================================================
        # POLITICAL DECAY
        # =====================================================

        self.political_fragmentation *= 0.996
        self.political_fatigue *= 0.997
        self.institutional_pressure *= 0.996
        self.legitimacy_crisis *= 0.996

        self.political_tension *= 0.997
        self.coalition_stability *= 0.998

        # =====================================================
        # LEGITIMACY DYNAMICS
        # =====================================================

        self.perceived_legitimacy += (
            random.uniform(
                -0.01,
                0.008,
            )
        )

        self.perceived_legitimacy -= (
            self.legitimacy_crisis
            * 0.002
        )

        self.perceived_legitimacy = max(
            0.0,
            min(
                2.0,
                self.perceived_legitimacy,
            )
        )

        # =====================================================
        # SYMBOLIC WEALTH DYNAMICS
        # =====================================================

        wealth_variation = random.uniform(
            -0.02,
            0.02,
        )

        wealth_variation *= (
            1.0
            + self.wealth_volatility
        )

        wealth_variation += (
            self.perceived_legitimacy
            * 0.002
        )

        wealth_variation -= (
            self.political_fragmentation
            * 0.003
        )

        self.symbolic_wealth += wealth_variation

        self.symbolic_wealth = max(
            0.0,
            min(
                10.0,
                self.symbolic_wealth,
            )
        )

        # =====================================================
        # LOYALTY DYNAMICS
        # =====================================================

        self.institutional_loyalty += (
            random.uniform(
                -0.01,
                0.01,
            )
        )

        self.institutional_loyalty += (
            self.perceived_legitimacy
            * 0.001
        )

        self.institutional_loyalty = max(
            0.0,
            min(
                2.0,
                self.institutional_loyalty,
            )
        )

        # =====================================================
        # JURIDICAL DYNAMICS
        # =====================================================

        self.normative_conflict *= 0.997
        self.legal_fragmentation *= 0.997
        self.jurisprudential_density *= 0.999

        self.legal_legitimacy += (
            random.uniform(
                -0.008,
                0.008,
            )
        )

        self.legal_legitimacy -= (
            self.normative_conflict
            * 0.002
        )

        self.legal_legitimacy = max(
            0.0,
            min(
                2.0,
                self.legal_legitimacy,
            )
        )

        self.legal_stability += (
            self.legal_legitimacy
            * 0.001
        )

        self.legal_stability -= (
            self.legal_fragmentation
            * 0.002
        )

        self.legal_stability = max(
            0.0,
            min(
                2.0,
                self.legal_stability,
            )
        )

        # =====================================================
        # COLLAPSE RISK
        # =====================================================

        collapse_risk = (
            self.political_fragmentation
            * 0.01
            + self.legitimacy_crisis
            * 0.01
            + self.political_fatigue
            * 0.005
            + self.normative_conflict
            * 0.005
            + self.legal_fragmentation
            * 0.005
        )

        if (
            random.random()
            < collapse_risk
        ):
            self.trigger_political_collapse()

        # =====================================================
        # HISTORY
        # =====================================================

        self._record_local_history()

    # =========================================================
    # INSTITUTIONAL INTERACTION
    # =========================================================

    def register_institutional_influence(
        self,
        institution,
        influence_strength=1.0,
    ):

        self.institutional_affiliations.add(
            id(institution)
        )

        self.perceived_legitimacy += (
            0.01 * influence_strength
        )

        self.symbolic_wealth += (
            0.005 * influence_strength
        )

        self.institutional_pressure += (
            0.002 * influence_strength
        )

    # =========================================================
    # CURRENCY INTERACTION
    # =========================================================

    def register_currency_interaction(
        self,
        currency,
        exchange_strength=1.0,
    ):

        self.symbolic_wealth += (
            0.01 * exchange_strength
        )

        self.economic_preferences[
            id(currency)
        ] = (
            self.economic_preferences.get(
                id(currency),
                0.0,
            )
            + exchange_strength
        )

    # =========================================================
    # COORDINATION INTERACTION
    # =========================================================

    def register_coordination(
        self,
        system,
        coordination_strength=1.0,
    ):

        self.coordination_dependence += (
            0.005
            * coordination_strength
        )

        self.political_fragmentation *= (
            0.995
        )

        self.institutional_loyalty += (
            0.002
            * coordination_strength
        )

        self.coalition_stability += (
            0.003
            * coordination_strength
        )

    # =========================================================
    # NORMATIVE INTERACTION
    # =========================================================

    def register_normative_interaction(
        self,
        normative_strength=1.0,
        compatibility=1.0,
    ):

        self.jurisprudential_density += (
            0.01 * normative_strength
        )

        self.legal_legitimacy += (
            0.004
            * normative_strength
            * compatibility
        )

        self.normative_conflict += (
            0.01
            * normative_strength
            * (1.0 - compatibility)
        )

        self.legal_fragmentation += (
            0.005
            * (1.0 - compatibility)
        )

    # =========================================================
    # COLLAPSE
    # =========================================================

    def trigger_political_collapse(
        self,
    ):

        self.political_fragmentation += (
            random.uniform(
                0.2,
                0.6,
            )
        )

        self.political_fatigue += (
            random.uniform(
                0.1,
                0.3,
            )
        )

        self.legitimacy_crisis += (
            random.uniform(
                0.1,
                0.4,
            )
        )

        self.normative_conflict += (
            random.uniform(
                0.05,
                0.25,
            )
        )

        self.legal_fragmentation += (
            random.uniform(
                0.05,
                0.25,
            )
        )

        self.symbolic_wealth *= (
            random.uniform(
                0.5,
                0.9,
            )
        )

        self.perceived_legitimacy *= (
            random.uniform(
                0.4,
                0.8,
            )
        )

        self.legal_legitimacy *= (
            random.uniform(
                0.4,
                0.8,
            )
        )

        self.institutional_affiliations.clear()
        self.active_coalitions.clear()
        self.normative_exclusions.clear()

    # =========================================================
    # HISTORY
    # =========================================================

    def _record_local_history(
        self,
    ):

        self.political_history.append(
            {
                "wealth": self.symbolic_wealth,
                "legitimacy": (
                    self.perceived_legitimacy
                ),
                "fragmentation": (
                    self.political_fragmentation
                ),
                "tension": (
                    self.political_tension
                ),
                "affiliation": (
                    self.political_affiliation
                ),
            }
        )

        if (
            len(self.political_history)
            > 120
        ):
            self.political_history.pop(0)

        self.legal_history.append(
            {
                "legal_legitimacy": (
                    self.legal_legitimacy
                ),
                "normative_conflict": (
                    self.normative_conflict
                ),
                "legal_fragmentation": (
                    self.legal_fragmentation
                ),
                "legal_stability": (
                    self.legal_stability
                ),
            }
        )

        if len(self.legal_history) > 120:
            self.legal_history.pop(0)