
from ontology.trajectory_resilience import (
    TrajectoryResilience
)

from ontology.civilizational_resilience import (
    CivilizationalResilience
)

from ontology.social_ecological_resilience import (
    SocialEcologicalResilience
)

from ontology.distributed_civilizational_viability import (
    DistributedCivilizationalViability
)

from ontology.reflexive_civilizational_ecology import (
    ReflexiveCivilizationalEcology
)

from ontology.intergenerational_symbolic_reconstruction import (
    IntergenerationalSymbolicReconstruction
)


class RefinedLongDurationCivilizationalResilience:

    def __init__(self):

        self.trajectory = (
            TrajectoryResilience()
        )

        self.civilizational = (
            CivilizationalResilience()
        )

        self.social_ecological = (
            SocialEcologicalResilience()
        )

        self.viability = (
            DistributedCivilizationalViability()
        )

        self.reflexive_ecology = (
            ReflexiveCivilizationalEcology()
        )

        self.reconstruction = (
            IntergenerationalSymbolicReconstruction()
        )

    def evaluate_meta_resilience(
        self,
        redundancy_level,
        institutional_stability,
        restoration_speed,
        adaptive_capacity,
        ecological_resilience,
        adaptive_governance,
        viability_index,
        corridor_preservation,
        oscillatory_stability,
        historical_breathability,
        convergence_pressure,
        regenerative_capacity,
        symbolic_fragmentation,
        semantic_reconciliation,
        attractor_recovery,
        fatigue_accumulation,
        recovery_cycles
    ):

        civil = self.civilizational.evaluate({
            "redundancy_level": redundancy_level,
            "institutional_stability":
                institutional_stability,
            "restoration_speed":
                restoration_speed,
            "adaptive_capacity":
                adaptive_capacity
        })

        socio = self.social_ecological.evaluate({
            "ecological_resilience":
                ecological_resilience,
            "institutional_resilience":
                institutional_stability,
            "adaptive_governance":
                adaptive_governance
        })

        reflexive = (
            self.reflexive_ecology
            .evaluate_reflexive_ecology(
                viability_index=viability_index,
                corridor_preservation=
                    corridor_preservation,
                oscillatory_stability=
                    oscillatory_stability,
                historical_breathability=
                    historical_breathability,
                convergence_pressure=
                    convergence_pressure,
                regenerative_capacity=
                    regenerative_capacity,
                ecological_load=
                    fatigue_accumulation
            )
        )

        reconstruction = (
            self.reconstruction
            .evaluate_reconstruction(
                symbolic_fragmentation=
                    symbolic_fragmentation,
                historical_continuity=
                    institutional_stability,
                semantic_reconciliation=
                    semantic_reconciliation,
                attractor_recovery=
                    attractor_recovery,
                memory_persistence=
                    viability_index,
                corridor_reconnection=
                    corridor_preservation,
                divergence_tolerance=
                    oscillatory_stability
            )
        )

        fatigue_resistance = (
            1.0 - fatigue_accumulation
        )

        cycle_resilience = min(
            1.0,
            recovery_cycles / 10.0
        )

        meta_resilience = (
            (
                civil[
                    "civilizational_resilience_index"
                ] * 0.20
            ) +
            (
                socio[
                    "social_ecological_resilience_index"
                ] * 0.20
            ) +
            (
                reflexive[
                    "reflexive_ecological_stability"
                ] * 0.20
            ) +
            (
                reconstruction[
                    "intergenerational_reconstruction_index"
                ] * 0.20
            ) +
            (
                fatigue_resistance * 0.10
            ) +
            (
                cycle_resilience * 0.10
            )
        )

        meta_resilience = max(
            0.0,
            min(1.0, meta_resilience)
        )

        if meta_resilience >= 0.75:
            state = (
                "meta_resilient_civilization"
            )
        elif meta_resilience >= 0.45:
            state = (
                "fragile_meta_resilience"
            )
        else:
            state = (
                "civilizational_exhaustion_regime"
            )

        return {
            "meta_resilience_index":
                round(meta_resilience, 4),

            "civilizational_resilience_index":
                round(
                    civil[
                        "civilizational_resilience_index"
                    ],
                    4
                ),

            "social_ecological_resilience_index":
                round(
                    socio[
                        "social_ecological_resilience_index"
                    ],
                    4
                ),

            "reflexive_ecological_stability":
                round(
                    reflexive[
                        "reflexive_ecological_stability"
                    ],
                    4
                ),

            "intergenerational_reconstruction_index":
                round(
                    reconstruction[
                        "intergenerational_reconstruction_index"
                    ],
                    4
                ),

            "fatigue_resistance":
                round(fatigue_resistance, 4),

            "cycle_resilience":
                round(cycle_resilience, 4),

            "meta_resilience_state": state
        }
