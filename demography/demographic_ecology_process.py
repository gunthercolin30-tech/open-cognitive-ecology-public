# demography/demographic_ecology_process.py

from agents.agent import PersistentAgent


class DemographicEcologyProcess:
    """
    Global demographic ecology.

    This process coordinates:
    - age structure
    - population pressure
    - births
    - deaths
    - replacement
    - generational turnover

    No fixed population equilibrium.
    No immortal population.
    No globally optimal demographic structure.
    """

    def __init__(self):
        # Global indicators
        self.population_size = 0
        self.alive_count = 0
        self.dead_count = 0
        self.birth_count = 0
        self.death_count = 0

        self.average_age = 0.0
        self.average_fertility = 0.0
        self.average_mortality_risk = 0.0
        self.average_birth_potential = 0.0

        self.young_ratio = 0.0
        self.reproductive_ratio = 0.0
        self.elder_ratio = 0.0

        self.population_pressure = 0.0
        self.generation_turnover = 0.0

        self._newborn_index = 0

    # =========================================================
    # MAIN UPDATE
    # =========================================================

    def update(self, population):
        """
        Update the global demographic ecology.

        Supported inputs:
        - graph object exposing `.nodes`
        - mutable list of PersistentAgent objects

        All original demographic functionality is preserved:
        - statistics
        - births
        - deaths
        - population pressure
        - generational turnover
        """

        # -----------------------------------------------------
        # INPUT NORMALIZATION
        # -----------------------------------------------------

        is_graph_mode = hasattr(population, "nodes")

        if is_graph_mode:
            graph = population
            agents = list(graph.nodes)
        else:
            graph = None
            agents = list(population)

        if not agents:
            self._reset()
            return

        self.population_size = len(agents)

        # -----------------------------------------------------
        # COMPUTE GLOBAL STATISTICS
        # -----------------------------------------------------

        alive_agents = [
            agent
            for agent in agents
            if agent.demographic_component.is_alive
        ]

        self.alive_count = len(alive_agents)
        self.dead_count = (
            self.population_size - self.alive_count
        )

        if self.alive_count > 0:
            self.average_age = (
                sum(
                    agent.age
                    for agent in alive_agents
                )
                / self.alive_count
            )

            self.average_fertility = (
                sum(
                    agent.fertility
                    for agent in alive_agents
                )
                / self.alive_count
            )

            self.average_mortality_risk = (
                sum(
                    agent.mortality_risk
                    for agent in alive_agents
                )
                / self.alive_count
            )

            self.average_birth_potential = (
                sum(
                    agent.birth_potential
                    for agent in alive_agents
                )
                / self.alive_count
            )
        else:
            self.average_age = 0.0
            self.average_fertility = 0.0
            self.average_mortality_risk = 0.0
            self.average_birth_potential = 0.0

        # -----------------------------------------------------
        # AGE STRUCTURE
        # -----------------------------------------------------

        young_count = 0
        reproductive_count = 0
        elder_count = 0

        for agent in alive_agents:
            if agent.age < 15.0:
                young_count += 1
            elif agent.is_reproductive:
                reproductive_count += 1
            else:
                elder_count += 1

        if self.alive_count > 0:
            self.young_ratio = (
                young_count / self.alive_count
            )
            self.reproductive_ratio = (
                reproductive_count
                / self.alive_count
            )
            self.elder_ratio = (
                elder_count / self.alive_count
            )
        else:
            self.young_ratio = 0.0
            self.reproductive_ratio = 0.0
            self.elder_ratio = 0.0

        # -----------------------------------------------------
        # POPULATION PRESSURE
        # -----------------------------------------------------

        target_reproductive_ratio = 0.40

        self.population_pressure = min(
            1.0,
            max(
                0.0,
                0.5
                + (
                    target_reproductive_ratio
                    - self.reproductive_ratio
                ),
            ),
        )

        for agent in agents:
            (
                agent.demographic_component
                .set_population_pressure(
                    self.population_pressure
                )
            )

        # -----------------------------------------------------
        # BIRTHS
        # -----------------------------------------------------

        newborns = []

        self.birth_count = 0

        for agent in alive_agents:
            if (
                agent.demographic_component
                .can_give_birth()
            ):
                newborn = self._create_newborn()
                newborns.append(newborn)
                self.birth_count += 1

        # In graph mode, newborns are inserted into the graph.
        # In list mode, newborns are appended to the shared
        # mutable agents list.
        if is_graph_mode:
            for newborn in newborns:
                graph.add_node(newborn)
        else:
            agents.extend(newborns)

            # Propagate changes back to the original mutable list.
            if hasattr(population, "extend"):
                population.extend(newborns)

        # -----------------------------------------------------
        # DEATHS
        # -----------------------------------------------------

        dead_agents = [
            agent
            for agent in agents
            if not agent.demographic_component.is_alive
        ]

        self.death_count = len(dead_agents)

        if is_graph_mode:
            for agent in dead_agents:
                if agent in graph:
                    graph.remove_node(agent)
        else:
            for agent in dead_agents:
                if agent in agents:
                    agents.remove(agent)

            # Propagate removals back to the original list.
            if hasattr(population, "__setitem__"):
                population[:] = agents

        # -----------------------------------------------------
        # GENERATION TURNOVER
        # -----------------------------------------------------

        if self.population_size > 0:
            self.generation_turnover = (
                (
                    self.birth_count
                    + self.death_count
                )
                / self.population_size
            )
        else:
            self.generation_turnover = 0.0

        # -----------------------------------------------------
        # FINAL COUNTS
        # -----------------------------------------------------

        if is_graph_mode:
            self.population_size = len(graph.nodes)
        else:
            self.population_size = len(agents)

        self.alive_count = self.population_size
        self.dead_count = 0

    # =========================================================
    # NEWBORN CREATION
    # =========================================================

    def _create_newborn(self):
        """
        Create a new agent initialized as a newborn.
        """

        self._newborn_index += 1

        newborn = PersistentAgent(
            name=f"newborn_{self._newborn_index}"
        )

        newborn.demographic_component.reset_as_newborn()

        return newborn

    # =========================================================
    # RESET
    # =========================================================

    def _reset(self):
        """
        Reset all indicators when the population is empty.
        """

        self.population_size = 0
        self.alive_count = 0
        self.dead_count = 0
        self.birth_count = 0
        self.death_count = 0

        self.average_age = 0.0
        self.average_fertility = 0.0
        self.average_mortality_risk = 0.0
        self.average_birth_potential = 0.0

        self.young_ratio = 0.0
        self.reproductive_ratio = 0.0
        self.elder_ratio = 0.0

        self.population_pressure = 0.0
        self.generation_turnover = 0.0