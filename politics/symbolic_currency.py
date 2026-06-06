# politics/symbolic_currency.py

import random
import math


class SymbolicCurrency:

    """
    Distributed symbolic economy.

    No universal market.
    No stable exchange system.
    No objective value.
    No global convertibility.

    Symbolic currencies emerge locally from:
    - mythological legitimacy
    - institutional attraction
    - cultural resonance
    - narrative scarcity
    - ecological compatibility

    Currency systems remain:
    - unstable
    - partially transmissible
    - locally interpreted
    - phenomenologically constrained
    - civilizationally incompatible
    """

    def __init__(
        self,
        name,
        institution=None,
    ):

        self.name = name

        self.institution = institution

        # =====================================================
        # SYMBOLIC CORE
        # =====================================================

        self.currency_signature = (
            random.uniform(
                -1.0,
                1.0,
            )
        )

        self.symbolic_value = random.uniform(
            0.3,
            1.2,
        )

        self.legitimacy = random.uniform(
            0.2,
            1.0,
        )

        self.volatility = random.uniform(
            0.0,
            0.5,
        )

        self.scarcity = random.uniform(
            0.1,
            1.0,
        )

        self.fragmentation = 0.0

        self.convertibility_tension = (
            0.0
        )

        self.semantic_instability = (
            0.0
        )

        # =====================================================
        # ECOLOGICAL DYNAMICS
        # =====================================================

        self.local_acceptance = random.uniform(
            0.2,
            1.0,
        )

        self.institutional_dependency = (
            random.uniform(
                0.2,
                1.0,
            )
        )

        self.mythological_charge = (
            random.uniform(
                0.0,
                1.0,
            )
        )

        self.exchange_pressure = 0.0

        self.collapse_exposure = 0.0

        # =====================================================
        # SYMBOLIC NETWORKS
        # =====================================================

        self.accepted_regions = set()

        self.rejected_regions = set()

        self.exchange_relations = {}

        self.incompatible_currencies = (
            set()
        )

        # =====================================================
        # HISTORICAL MEMORY
        # =====================================================

        self.value_history = []

        self.legitimacy_history = []

        self.exchange_history = []

        self.collapse_history = []

        self.semantic_mutations = []

        # =====================================================
        # TEMPORAL DYNAMICS
        # =====================================================

        self.temporal_drift = random.uniform(
            0.0,
            1.0,
        )

        self.mutation_rate = random.uniform(
            0.001,
            0.02,
        )

        self.inflation_pressure = 0.0

        self.deflation_pressure = 0.0

    # =========================================================
    # EVOLUTION
    # =========================================================

    def evolve(
        self,
        nearby_currencies=None,
        nearby_agents=None,
    ):

        self._update_internal_dynamics()

        self._mutate_semantic_structure()

        self._update_local_acceptance(
            nearby_agents
        )

        self._update_exchange_relations(
            nearby_currencies
        )

        self._generate_symbolic_events()

    # =========================================================
    # INTERNAL DYNAMICS
    # =========================================================

    def _update_internal_dynamics(
        self,
    ):

        self.exchange_pressure *= (
            0.996
        )

        self.fragmentation *= (
            0.997
        )

        self.semantic_instability *= (
            0.996
        )

        self.collapse_exposure *= (
            0.996
        )

        self.inflation_pressure *= (
            0.997
        )

        self.deflation_pressure *= (
            0.997
        )

        # =====================================================
        # VALUE EVOLUTION
        # =====================================================

        fluctuation = random.uniform(
            -0.03,
            0.03,
        )

        fluctuation *= (
            1.0
            + self.volatility
        )

        fluctuation += (
            self.mythological_charge
            * 0.01
        )

        fluctuation -= (
            self.fragmentation
            * 0.01
        )

        self.symbolic_value += fluctuation

        self.symbolic_value = max(
            0.01,
            min(
                5.0,
                self.symbolic_value,
            )
        )

        # =====================================================
        # LEGITIMACY EVOLUTION
        # =====================================================

        self.legitimacy += (
            random.uniform(
                -0.01,
                0.01,
            )
        )

        self.legitimacy += (
            self.local_acceptance
            * 0.002
        )

        self.legitimacy -= (
            self.semantic_instability
            * 0.003
        )

        self.legitimacy = max(
            0.0,
            min(
                2.0,
                self.legitimacy,
            )
        )

        # =====================================================
        # HISTORICAL STORAGE
        # =====================================================

        self.value_history.append(
            self.symbolic_value
        )

        self.legitimacy_history.append(
            self.legitimacy
        )

        if len(self.value_history) > 200:
            self.value_history.pop(0)

        if (
            len(self.legitimacy_history)
            > 200
        ):
            self.legitimacy_history.pop(0)

        # =====================================================
        # COLLAPSE RISK
        # =====================================================

        collapse_risk = (

            self.fragmentation
            * 0.01

            + self.semantic_instability
            * 0.01

            + self.convertibility_tension
            * 0.005
        )

        if (
            random.random()
            < collapse_risk
        ):

            self._trigger_currency_collapse()

    # =========================================================
    # SEMANTIC MUTATION
    # =========================================================

    def _mutate_semantic_structure(
        self,
    ):

        self.currency_signature += (
            random.uniform(
                -0.01,
                0.01,
            )
            * self.mutation_rate
        )

        self.semantic_instability += (
            random.uniform(
                -0.005,
                0.015,
            )
        )

        mutation_event = {
            "signature": (
                self.currency_signature
            ),
            "instability": (
                self.semantic_instability
            ),
            "cycle": len(
                self.semantic_mutations
            ),
        }

        if (
            random.random()
            < 0.01
        ):

            self.semantic_mutations.append(
                mutation_event
            )

            if (
                len(self.semantic_mutations)
                > 120
            ):
                self.semantic_mutations.pop(
                    0
                )

    # =========================================================
    # LOCAL ACCEPTANCE
    # =========================================================

    def _update_local_acceptance(
        self,
        nearby_agents,
    ):

        if not nearby_agents:
            return

        acceptance_variation = 0.0

        for agent in nearby_agents:

            compatibility = 1.0 - abs(

                agent.civilizational_signature

                - self.currency_signature
            )

            compatibility = max(
                0.0,
                compatibility,
            )

            acceptance_variation += (
                compatibility
                * 0.001
            )

            agent.cultural_stability += (
                compatibility
                * 0.0005
            )

            agent.symbolic_drift += (
                self.semantic_instability
                * 0.0005
            )

        self.local_acceptance += (
            acceptance_variation
        )

        self.local_acceptance = max(
            0.0,
            min(
                2.0,
                self.local_acceptance,
            )
        )

    # =========================================================
    # EXCHANGE RELATIONS
    # =========================================================

    def _update_exchange_relations(
        self,
        nearby_currencies,
    ):

        if not nearby_currencies:
            return

        for currency in nearby_currencies:

            if currency is self:
                continue

            compatibility = 1.0 - abs(

                currency.currency_signature

                - self.currency_signature
            )

            compatibility = max(
                0.0,
                compatibility,
            )

            exchange_probability = (

                compatibility
                * 0.02

                + self.legitimacy
                * 0.005
            )

            if (
                random.random()
                < exchange_probability
            ):

                self.exchange_relations[
                    id(currency)
                ] = compatibility

            incompatibility = (
                1.0
                - compatibility
            )

            if (
                incompatibility
                > 0.8
            ):

                self.incompatible_currencies.add(
                    id(currency)
                )

                self.convertibility_tension += (
                    incompatibility
                    * 0.01
                )

    # =========================================================
    # SYMBOLIC EVENTS
    # =========================================================

    def _generate_symbolic_events(
        self,
    ):

        probability = (

            0.002

            + self.volatility
            * 0.01

            + self.semantic_instability
            * 0.005
        )

        if (
            random.random()
            < probability
        ):

            event = {
                "value": (
                    self.symbolic_value
                ),
                "legitimacy": (
                    self.legitimacy
                ),
                "fragmentation": (
                    self.fragmentation
                ),
                "signature": (
                    self.currency_signature
                ),
            }

            self.exchange_history.append(
                event
            )

            if (
                len(self.exchange_history)
                > 120
            ):
                self.exchange_history.pop(0)

    # =========================================================
    # COLLAPSE
    # =========================================================

    def _trigger_currency_collapse(
        self,
    ):

        self.fragmentation += (
            random.uniform(
                0.2,
                0.6,
            )
        )

        self.semantic_instability += (
            random.uniform(
                0.1,
                0.4,
            )
        )

        self.collapse_exposure += (
            random.uniform(
                0.1,
                0.5,
            )
        )

        self.symbolic_value *= (
            random.uniform(
                0.2,
                0.7,
            )
        )

        self.legitimacy *= (
            random.uniform(
                0.3,
                0.8,
            )
        )

        collapse_event = {
            "value": (
                self.symbolic_value
            ),
            "legitimacy": (
                self.legitimacy
            ),
            "fragmentation": (
                self.fragmentation
            ),
            "collapse": True,
        }

        self.collapse_history.append(
            collapse_event
        )

        if (
            len(self.collapse_history)
            > 120
        ):
            self.collapse_history.pop(0)