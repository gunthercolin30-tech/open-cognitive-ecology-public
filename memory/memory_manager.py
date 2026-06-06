import uuid

from memory.models import (
    MemoryNode,
)


class MemoryManager:
    """
    Memory manager with structural consolidation dynamics.

    This implementation integrates core concepts from the constraint-based
    theoretical framework as permanent attractors of memory organization.

    Main principles:
    - Non-closure: prevents convergence toward a fully closed memory state.
    - Constraint fields: modulate consolidation intensity.
    - Non-representability: preserves residual instability.
    - Constraint-induced existence: stable memories emerge only under constraints.
    - Trajectories without globality: local stabilization without global closure.
    - Unstable configuration principle: highly stable memories remain partially open.
    """

    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.memories = {}

        # Core theoretical attractors.
        # These concepts receive enhanced stabilization and influence all memory
        # dynamics as organizing poles.
        self.core_attractors = {
            "non-closure",
            "non closure",
            "non-clôture",
            "constraint field",
            "constraint fields",
            "champ de contraintes",
            "champs de contraintes",
            "dynamics of constraints",
            "constraint dynamics",
            "non-representability",
            "non representability",
            "non-représentabilité",
            "constraint-induced domain",
            "constraint induced domain",
            "domaine induit par contraintes",
            "existence as a constraint-induced domain",
            "trajectories without globality",
            "trajectoire sans globalité",
            "trajectoires sans globalité",
            "unstable configuration principle",
            "principe de configuration instable",
            "formal foundations of constraint-based systems",
            "fondations formelles des systèmes sous contraintes",
            "impossibility of global closure",
            "impossibility of the global closure",
            "impossibilité de la clôture globale",
        }

        # Parameters controlling the structural memory dynamics.
        self.attractor_bonus = 0.05
        self.constraint_gain = 0.03
        self.non_closure_floor = 0.10
        self.max_salience = 10.0
        self.max_energy = 10.0

    async def add_memory(
        self,
        content,
        tags=None,
    ):
        memory = MemoryNode(
            id=str(uuid.uuid4()),
            content=content,
            tags=tags or [],
        )

        content_lower = content.lower()

        # Contradictions are structurally salient.
        if "contradiction" in content_lower:
            memory.tension = 1.0
            memory.salience = 2.0

        # Core theoretical attractors are preferentially consolidated.
        if self._is_core_attractor(memory):
            memory.salience = max(memory.salience, 3.0)
            memory.energy = max(memory.energy, 2.0)
            memory.tension = max(memory.tension, 0.3)

        self.memories[memory.id] = memory

        await self.event_bus.emit(
            "MEMORY_CREATED",
            memory,
        )

        print(
            "[memory-created]",
            memory.content,
        )

        return memory

    async def tick(self):
        """
        Update all memories.

        Dynamics:
        - natural dissipation;
        - tension-driven reinforcement;
        - constraint-driven consolidation;
        - non-closure floor;
        - bounded growth.
        """
        for memory in self.memories.values():
            # Natural dissipation.
            memory.salience *= 0.995
            memory.energy *= 0.999

            # Contradictions and tensions remain cognitively active.
            if memory.tension > 0:
                memory.salience += memory.tension * 0.01

            # Constraint field effect.
            constraint_strength = self._compute_constraint_strength(memory)
            memory.salience += constraint_strength * self.constraint_gain
            memory.energy += constraint_strength * 0.005

            # Structural attractors receive additional reinforcement.
            if self._is_core_attractor(memory):
                memory.salience += self.attractor_bonus
                memory.energy += 0.01

            # Non-closure:
            # even weak memories preserve a minimal residual presence.
            if memory.salience < self.non_closure_floor:
                memory.salience = self.non_closure_floor

            # Unstable configuration principle:
            # highly stabilized memories retain a small residual tension.
            if memory.salience > 2.0:
                memory.tension = max(memory.tension, 0.02)

            # Prevent unbounded accumulation.
            memory.salience = min(memory.salience, self.max_salience)
            memory.energy = min(memory.energy, self.max_energy)

    def get_memories(self):
        return list(self.memories.values())

    # ---------------------------------------------------------------------
    # Structural dynamics
    # ---------------------------------------------------------------------

    def _is_core_attractor(self, memory):
        """
        Determine whether a memory contains one of the core concepts
        of the theoretical corpus.
        """
        content = (memory.content or "").lower()

        if any(keyword in content for keyword in self.core_attractors):
            return True

        for tag in getattr(memory, "tags", []):
            if str(tag).lower() in self.core_attractors:
                return True

        return False

    def _compute_constraint_strength(self, memory):
        """
        Estimate local structural constraint intensity.

        Constraint intensity increases with:
        - tension;
        - number of tags;
        - attractor status.

        This produces local stabilization without requiring a global model.
        """
        strength = 0.0

        # Tension indicates unresolved incompatibilities.
        strength += getattr(memory, "tension", 0.0)

        # Richly connected memories are more structurally constrained.
        strength += len(getattr(memory, "tags", [])) * 0.05

        # Core theoretical concepts act as persistent organizing poles.
        if self._is_core_attractor(memory):
            strength += 1.0

        return strength