# processes/political_ecology_process.py

import math
import random

from politics.local_institution import LocalInstitution
from politics.symbolic_currency import SymbolicCurrency
from politics.distributed_coordination_system import (
    DistributedCoordinationSystem,
)


class PoliticalEcologyProcess:
    """
    Distributed political ecology.

    No central government.
    No global economy.
    No universal legitimacy.
    No stable sovereignty.

    This process orchestrates:
    - local institutions
    - symbolic currencies
    - distributed coordination systems
    - alliances and exclusions
    - institutional and monetary collapses
    - coalition emergence
    - political incompatibilities
    """

    def __init__(
        self,
        graph,
        institution_count=6,
        coordination_system_count=4,
    ):
        # =====================================================
        # GRAPH REFERENCE
        # =====================================================

        self.graph = graph

        # =====================================================
        # POLITICAL STRUCTURES
        # =====================================================

        self.institutions = []
        self.currencies = []
        self.coordination_systems = []

        # =====================================================
        # CREATE LOCAL INSTITUTIONS
        # =====================================================

        for i in range(institution_count):
            center = (
                random.uniform(-30.0, 30.0),
                random.uniform(-30.0, 30.0),
            )

            institution = LocalInstitution(
                name=f"institution_{i}",
                center=center,
            )

            currency = SymbolicCurrency(
                name=f"currency_{i}",
                institution=institution,
            )

            self.institutions.append(institution)
            self.currencies.append(currency)

        # =====================================================
        # CREATE COORDINATION SYSTEMS
        # =====================================================

        for i in range(coordination_system_count):
            center = (
                random.uniform(-30.0, 30.0),
                random.uniform(-30.0, 30.0),
            )

            system = DistributedCoordinationSystem(
                name=f"coordination_{i}",
                center=center,
            )

            self.coordination_systems.append(system)

        # =====================================================
        # HISTORY
        # =====================================================

        self.history = []

    # =========================================================
    # SCHEDULER ENTRY POINT
    # =========================================================

    async def run(self):
        """
        Scheduler entry point.

        Graph nodes are treated as distributed agents.
        Missing attributes expected by political and
        symbolic subsystems are initialized.
        """

        agents = list(self.graph.nodes.values())

        for agent in agents:
            self._initialize_agent_defaults(agent)

        self.evolve(agents=agents)

    # =========================================================
    # AGENT INITIALIZATION
    # =========================================================

    def _initialize_agent_defaults(
        self,
        agent,
    ):
        """
        Initialize all attributes potentially used by
        institutions, currencies, and coordination systems.
        """

        defaults = {
            # Spatial coordinates
            "x": random.uniform(-5.0, 5.0),
            "y": random.uniform(-5.0, 5.0),

            # Civilizational and symbolic attributes
            "civilizational_signature": random.uniform(0.0, 1.0),
            "fragmentation": random.uniform(0.0, 1.0),
            "local_coherence": random.uniform(0.0, 1.0),
            "cultural_resonance": random.uniform(0.0, 1.0),
            "symbolic_load": 0.0,
            "mythological_pressure": 0.0,
            "compatibility_tension": 0.0,
            "cultural_stability": 1.0,

            # Constraint-related attributes
            "incompatibility_field": random.uniform(0.0, 0.2),

            # Political projection fields
            "institutional_intensity": 0.0,
            "symbolic_currency": 0.0,
            "coordination_intensity": 0.0,
            "political_tension": 0.0,
            "political_affiliation": "none",
        }

        for attribute, value in defaults.items():
            if not hasattr(agent, attribute):
                setattr(agent, attribute, value)

    # =========================================================
    # MAIN EVOLUTION
    # =========================================================

    def evolve(
        self,
        agents=None,
    ):
        if agents is None:
            agents = []

        # =====================================================
        # INSTITUTIONS
        # =====================================================

        for institution in self.institutions:
            nearby_agents = self._find_nearby_agents(
                institution.center,
                institution.influence_radius,
                agents,
            )

            nearby_institutions = self._find_nearby_institutions(
                institution
            )

            institution.evolve(
                nearby_institutions=nearby_institutions,
                nearby_agents=nearby_agents,
            )

        # =====================================================
        # CURRENCIES
        # =====================================================

        for currency in self.currencies:
            institution = currency.institution

            nearby_agents = self._find_nearby_agents(
                institution.center,
                institution.influence_radius,
                agents,
            )

            nearby_currencies = self._find_nearby_currencies(
                currency
            )

            currency.evolve(
                nearby_currencies=nearby_currencies,
                nearby_agents=nearby_agents,
            )

        # =====================================================
        # COORDINATION SYSTEMS
        # =====================================================

        for system in self.coordination_systems:
            nearby_agents = self._find_nearby_agents(
                system.center,
                system.influence_radius,
                agents,
            )

            nearby_institutions = (
                self._find_nearby_institutions_by_position(
                    system.center,
                    system.influence_radius,
                )
            )

            nearby_systems = (
                self._find_nearby_coordination_systems(
                    system
                )
            )

            system.evolve(
                nearby_agents=nearby_agents,
                nearby_institutions=nearby_institutions,
                nearby_systems=nearby_systems,
            )

        # =====================================================
        # PROJECT TO AGENTS
        # =====================================================

        self._update_agent_political_fields(
            agents
        )

        # =====================================================
        # STRUCTURAL DYNAMICS
        # =====================================================

        self._exchange_symbolic_currency()
        self._update_coalitions()
        self._dissipate_fragile_structures()

        # =====================================================
        # HISTORY
        # =====================================================

        self._record_history()

    # =========================================================
    # AGENT POLITICAL COUPLING
    # =========================================================

    def _update_agent_political_fields(
        self,
        agents,
    ):
        for agent in agents:
            nearby_institutions = (
                self._find_nearby_institutions_by_position(
                    (agent.x, agent.y),
                    12.0,
                )
            )

            nearby_systems = []

            for system in self.coordination_systems:
                dx = system.center[0] - agent.x
                dy = system.center[1] - agent.y

                distance = math.sqrt(dx * dx + dy * dy)

                if distance <= system.influence_radius:
                    nearby_systems.append(system)

            nearby_currencies = []

            for currency in self.currencies:
                institution = currency.institution

                dx = institution.center[0] - agent.x
                dy = institution.center[1] - agent.y

                distance = math.sqrt(dx * dx + dy * dy)

                if distance <= institution.influence_radius:
                    nearby_currencies.append(currency)

            institutional_intensity = self._average(
                [
                    getattr(
                        institution,
                        "legitimacy",
                        0.0,
                    )
                    for institution in nearby_institutions
                ]
            )

            symbolic_currency = self._average(
                [
                    getattr(
                        currency,
                        "symbolic_value",
                        0.0,
                    )
                    for currency in nearby_currencies
                ]
            )

            coordination_intensity = self._average(
                [
                    getattr(
                        system,
                        "coordination_strength",
                        0.0,
                    )
                    for system in nearby_systems
                ]
            )

            political_tension = min(
                1.0,
                abs(
                    institutional_intensity
                    - coordination_intensity
                )
                + getattr(
                    agent,
                    "incompatibility_field",
                    0.0,
                ) * 0.5,
            )

            if (
                coordination_intensity
                > institutional_intensity
                and coordination_intensity > 0.45
            ):
                affiliation = "coalitional"

            elif symbolic_currency > 0.60:
                affiliation = "mercantile"

            elif institutional_intensity > 0.55:
                affiliation = "institutional"

            elif political_tension > 0.55:
                affiliation = "dissident"

            else:
                affiliation = "none"

            agent.institutional_intensity = institutional_intensity
            agent.symbolic_currency = symbolic_currency
            agent.coordination_intensity = coordination_intensity
            agent.political_tension = political_tension
            agent.political_affiliation = affiliation

    # =========================================================
    # STRUCTURAL DYNAMICS
    # =========================================================

    def _exchange_symbolic_currency(self):
        for currency in self.currencies:
            currency.symbolic_value += random.uniform(
                -0.03,
                0.03,
            )

            currency.symbolic_value = max(
                0.0,
                min(
                    1.5,
                    currency.symbolic_value,
                ),
            )

    def _update_coalitions(self):
        for system in self.coordination_systems:
            nearby = (
                self._find_nearby_coordination_systems(
                    system
                )
            )

            if not nearby:
                continue

            neighbor_strength = self._average(
                [
                    getattr(
                        neighbor,
                        "coordination_strength",
                        0.0,
                    )
                    for neighbor in nearby
                ]
            )

            system.coordination_strength += (
                (
                    neighbor_strength
                    - system.coordination_strength
                )
                * 0.05
            )

            system.coordination_strength = max(
                0.0,
                min(
                    1.5,
                    system.coordination_strength,
                ),
            )

    def _dissipate_fragile_structures(self):
        for institution in self.institutions:
            if institution.legitimacy < 0.05:
                institution.legitimacy += random.uniform(
                    0.0,
                    0.03,
                )

        for system in self.coordination_systems:
            if system.coordination_strength < 0.05:
                system.coordination_strength += (
                    random.uniform(
                        0.0,
                        0.03,
                    )
                )

    # =========================================================
    # DETECTION UTILITIES
    # =========================================================

    def _find_nearby_agents(
        self,
        center,
        radius,
        agents,
    ):
        nearby = []

        for agent in agents:
            dx = center[0] - agent.x
            dy = center[1] - agent.y

            distance = math.sqrt(dx * dx + dy * dy)

            if distance <= radius:
                nearby.append(agent)

        return nearby

    def _find_nearby_institutions(
        self,
        source_institution,
    ):
        nearby = []

        for institution in self.institutions:
            if institution is source_institution:
                continue

            dx = (
                institution.center[0]
                - source_institution.center[0]
            )
            dy = (
                institution.center[1]
                - source_institution.center[1]
            )

            distance = math.sqrt(dx * dx + dy * dy)

            if distance <= 15.0:
                nearby.append(institution)

        return nearby

    def _find_nearby_institutions_by_position(
        self,
        center,
        radius,
    ):
        nearby = []

        for institution in self.institutions:
            dx = institution.center[0] - center[0]
            dy = institution.center[1] - center[1]

            distance = math.sqrt(dx * dx + dy * dy)

            if distance <= radius:
                nearby.append(institution)

        return nearby

    def _find_nearby_currencies(
        self,
        source_currency,
    ):
        nearby = []

        source_center = (
            source_currency.institution.center
        )

        for currency in self.currencies:
            if currency is source_currency:
                continue

            center = currency.institution.center

            dx = center[0] - source_center[0]
            dy = center[1] - source_center[1]

            distance = math.sqrt(dx * dx + dy * dy)

            if distance <= 15.0:
                nearby.append(currency)

        return nearby

    def _find_nearby_coordination_systems(
        self,
        source_system,
    ):
        nearby = []

        for system in self.coordination_systems:
            if system is source_system:
                continue

            dx = (
                system.center[0]
                - source_system.center[0]
            )
            dy = (
                system.center[1]
                - source_system.center[1]
            )

            distance = math.sqrt(dx * dx + dy * dy)

            if distance <= 20.0:
                nearby.append(system)

        return nearby

    # =========================================================
    # HISTORY
    # =========================================================

    def _record_history(self):
        snapshot = {
            "institutions": len(
                self.institutions
            ),
            "currencies": len(
                self.currencies
            ),
            "coordination_systems": len(
                self.coordination_systems
            ),
            "avg_legitimacy": self._average(
                [
                    i.legitimacy
                    for i in self.institutions
                ]
            ),
            "avg_currency_value": self._average(
                [
                    c.symbolic_value
                    for c in self.currencies
                ]
            ),
            "avg_coordination_strength": self._average(
                [
                    s.coordination_strength
                    for s in self.coordination_systems
                ]
            ),
        }

        self.history.append(snapshot)

        if len(self.history) > 300:
            self.history.pop(0)

    # =========================================================
    # UTILITIES
    # =========================================================

    def _average(
        self,
        values,
    ):
        if not values:
            return 0.0

        return sum(values) / len(values)