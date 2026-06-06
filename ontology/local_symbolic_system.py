PRIMITIVE = "local_symbolic_system"
DESCRIPTION = "Local symbolic system."
DEPENDENCIES = []

from ontology.structural_primitives import (
    StructuralPrimitivesMixin,
)
from ontology.symbolic_generation import (
    SymbolicGenerationMixin,
)
from ontology.semantic_propagation import (
    SemanticPropagationMixin,
)
from ontology.grammar_dynamics import (
    GrammarDynamicsMixin,
)
from ontology.dialect_stabilization import (
    DialectStabilizationMixin,
)
from ontology.symbolic_fragmentation import (
    SymbolicFragmentationMixin,
)
from ontology.semantic_collapse import (
    SemanticCollapseMixin,
)
from ontology.symbolic_utilities import (
    SymbolicUtilitiesMixin,
)
from ontology.ecological_decay import (
    EcologicalDecayMixin,
)
from ontology.distributed_symbolic_ecology import (
    DistributedSymbolicEcology,
)
from ontology.semantic_field import (
    SemanticField,
)

# =========================================================
# ONTOLOGICAL PRIMITIVES
# =========================================================
from ontology.non_closure import (
    NonClosurePrimitive,
)
from ontology.constraint_fields import (
    ConstraintFieldsPrimitive,
)
from ontology.non_representability import (
    NonRepresentabilityPrimitive,
)


class LocalSymbolicSystem(
    StructuralPrimitivesMixin,
    SymbolicGenerationMixin,
    SemanticPropagationMixin,
    GrammarDynamicsMixin,
    DialectStabilizationMixin,
    SymbolicFragmentationMixin,
    SemanticCollapseMixin,
    SymbolicUtilitiesMixin,
    EcologicalDecayMixin,
):

    def __init__(self):

        self.local_lexicons = {}
        self.semantic_fields = {}
        self.grammatical_attractors = {}
        self.symbolic_regions = {}
        self.dialect_clusters = {}
        self.semantic_collapses = []

        self.semantic_decay = 0.997
        self.symbolic_mutation_rate = 0.01
        self.grammar_instability = 0.003
        self.semantic_fragmentation_rate = 0.002
        self.collapse_threshold = 1.2

        self.structural_seed_probability = 0.02
        self.non_closure_floor = 0.05
        self.constraint_field_gain = 0.01
        self.representation_residual_floor = 0.05
        self.representation_instability_gain = 1.0

        # =====================================================
        # ONTOLOGICAL PRIMITIVES
        # =====================================================
        self.non_closure = NonClosurePrimitive(
            minimum_openness=self.non_closure_floor,
        )

        self.constraint_fields = (
            ConstraintFieldsPrimitive(
                field_strength=(
                    1.0 + self.constraint_field_gain
                )
            )
        )

        self.non_representability = (
            NonRepresentabilityPrimitive(
                residual_floor=(
                    self.representation_residual_floor
                ),
                instability_gain=(
                    self.representation_instability_gain
                ),
            )
        )

        # Diagnostics exposed to the rest of the architecture.
        self.last_constraint_state = {}
        self.last_non_closure_state = {}
        self.last_non_representability_state = {}
        self.last_symbolic_activation = 1.0

        self._initialize_structural_primitives()

        self.distributed_ecology = (
            DistributedSymbolicEcology()
        )

        self.semantic_field = SemanticField()

    # =========================================================
    # AGENT INITIALIZATION
    # =========================================================

    def _initialize_agent_symbolic_state(
        self,
        agent,
    ):

        if not hasattr(
            agent,
            "symbolic_patterns",
        ):
            agent.symbolic_patterns = {}

        if not hasattr(
            agent,
            "local_mythologies",
        ):
            agent.local_mythologies = set()

        if not hasattr(
            agent,
            "symbolic_drift",
        ):
            agent.symbolic_drift = 0.0

        if not hasattr(
            agent,
            "mythological_pressure",
        ):
            agent.mythological_pressure = 0.0

        if not hasattr(
            agent,
            "local_coherence",
        ):
            agent.local_coherence = 0.0

        if not hasattr(
            agent,
            "transmission_drive",
        ):
            agent.transmission_drive = 0.0

        if not hasattr(
            agent,
            "semiotic_instability",
        ):
            agent.semiotic_instability = 0.0

        if not hasattr(
            agent,
            "cultural_stability",
        ):
            agent.cultural_stability = 0.0

        if not hasattr(
            agent,
            "cultural_fragmentation",
        ):
            agent.cultural_fragmentation = 0.0

        if not hasattr(
            agent,
            "civilizational_signature",
        ):
            agent.civilizational_signature = 0.0

        if not hasattr(
            agent,
            "representation_residual",
        ):
            agent.representation_residual = 0.0

        if not hasattr(
            agent,
            "innovation_pressure",
        ):
            agent.innovation_pressure = 0.0

        if not hasattr(
            agent,
            "representational_stability",
        ):
            agent.representational_stability = 1.0

    def _initialize_agents(
        self,
        agents,
    ):

        for agent in agents:
            self._initialize_agent_symbolic_state(
                agent
            )

    # =========================================================
    # ONTOLOGICAL MODULATION
    # =========================================================

    def _apply_ontological_primitives(
        self,
        agents,
    ):
        """
        Apply CONSTRAINT_FIELDS and NON_CLOSURE to the
        symbolic system before the main symbolic cycle.

        The resulting scalar can be used by other modules
        through `self.last_symbolic_activation`.
        """

        if not agents:
            self.last_constraint_state = {
                "local_intensity": 0.0,
                "admissibility": 1.0,
                "modulated_activation": 1.0,
            }
            self.last_non_closure_state = {
                "saturation": 0.0,
                "openness": 1.0,
                "closure_risk": 0.0,
                "should_perturb": False,
                "perturbation": 0.0,
            }
            self.last_non_representability_state = {
                "complexity_gap": 0.0,
                "residual": 0.0,
                "opacity": 0.0,
                "innovation_pressure": 0.0,
                "representational_stability": 1.0,
                "modulated_activation": 1.0,
            }
            self.last_symbolic_activation = 1.0
            return

        # ---------------------------------------------
        # Aggregate symbolic indicators
        # ---------------------------------------------
        n = float(len(agents))

        local_coherence = (
            sum(
                getattr(
                    agent,
                    "local_coherence",
                    0.0,
                )
                for agent in agents
            )
            / n
        )

        transmission_drive = (
            sum(
                getattr(
                    agent,
                    "transmission_drive",
                    0.0,
                )
                for agent in agents
            )
            / n
        )

        semiotic_instability = (
            sum(
                getattr(
                    agent,
                    "semiotic_instability",
                    0.0,
                )
                for agent in agents
            )
            / n
        )

        cultural_fragmentation = (
            sum(
                getattr(
                    agent,
                    "cultural_fragmentation",
                    0.0,
                )
                for agent in agents
            )
            / n
        )

        cultural_stability = (
            sum(
                getattr(
                    agent,
                    "cultural_stability",
                    0.0,
                )
                for agent in agents
            )
            / n
        )

        world_complexity = (
            1.0
            + transmission_drive
            + semiotic_instability
            + cultural_fragmentation
        )

        model_complexity = (
            1.0
            + local_coherence
            + cultural_stability
        )

        compression_ratio = 1.0

        self.last_non_representability_state = (
            self.non_representability.step(
                model_complexity=model_complexity,
                world_complexity=world_complexity,
                compression_ratio=compression_ratio,
            )
        )

        representational_activation = (
            self.last_non_representability_state[
                "modulated_activation"
            ]
        )

        # ---------------------------------------------
        # Constraint field modulation
        # ---------------------------------------------
        constraint_density = local_coherence
        environmental_pressure = transmission_drive
        coupling = 1.0 - semiotic_instability

        self.last_constraint_state = (
            self.constraint_fields.step(
                activation=1.0,
                constraint_density=constraint_density,
                environmental_pressure=(
                    environmental_pressure
                ),
                coupling=coupling,
            )
        )

        modulated_activation = (
            self.last_constraint_state[
                "modulated_activation"
            ]
        )

        # ---------------------------------------------
        # Non-closure modulation
        # ---------------------------------------------
        redundancy = local_coherence
        predictability = cultural_stability
        coherence = 1.0 - cultural_fragmentation

        self.last_non_closure_state = (
            self.non_closure.step(
                coherence=coherence,
                redundancy=redundancy,
                predictability=predictability,
            )
        )

        openness = self.last_non_closure_state[
            "openness"
        ]
        perturbation = (
            self.last_non_closure_state[
                "perturbation"
            ]
        )

        # ---------------------------------------------
        # Final symbolic activation
        # ---------------------------------------------
        final_activation = (
            representational_activation
            * modulated_activation
            * openness
            + perturbation
        )

        self.last_symbolic_activation = (
            final_activation
        )

        # Optional propagation to agents.
        for agent in agents:
            agent.symbolic_activation = (
                final_activation
            )
            agent.constraint_admissibility = (
                self.last_constraint_state[
                    "admissibility"
                ]
            )
            agent.non_closure_openness = (
                openness
            )
            agent.closure_risk = (
                self.last_non_closure_state[
                    "closure_risk"
                ]
            )
            agent.representation_residual = (
                self.last_non_representability_state[
                    "residual"
                ]
            )
            agent.innovation_pressure = (
                self.last_non_representability_state[
                    "innovation_pressure"
                ]
            )
            agent.representational_stability = (
                self.last_non_representability_state[
                    "representational_stability"
                ]
            )

    # =========================================================
    # MAIN EVOLUTION
    # =========================================================

    def evolve(
        self,
        agents,
    ):

        if not agents:
            return

        self._initialize_agents(
            agents
        )

        # Apply ontological primitives before the
        # symbolic generation and propagation cycle.
        self._apply_ontological_primitives(
            agents
        )

        self._seed_structural_primitives(
            agents
        )

        self._generate_local_symbols(
            agents
        )

        self._propagate_semantic_fields(
            agents
        )

        self._mutate_grammars(
            agents
        )

        self._stabilize_local_dialects(
            agents
        )

        self._fragment_symbolic_regions(
            agents
        )

        self._trigger_semantic_collapses(
            agents
        )

        self._decay_symbolic_ecology()

        self.distributed_ecology.evolve(
            self,
            agents,
        )

        self.semantic_field.update(
            self
        )