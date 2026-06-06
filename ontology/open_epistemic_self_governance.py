from statistics import mean

PRIMITIVE = "open_epistemic_self_governance"

DESCRIPTION = (
    "Open epistemic self governance."
)

DEPENDENCIES = [
    "reflexive_model_revision_ecology",
    "collective_deliberation_engine",
    "constitutional_alignment_field",
    "constitutional_alert_system",
    "collective_intelligence",
    "perspectival_knowledge",
    "distributed_knowledge_access",
    "epistemic_infrastructure",
    "civilizational_memory",
    "distributed_civilizational_memory",
    "civilizational_memory_archive",
    "civilizational_dialogue_memory",
    "anti_closure_metaconstraint",
]


class OpenEpistemicSelfGovernance:

    def _bounded(self, value):

        return max(
            0.0,
            min(
                1.0,
                float(value),
            ),
        )

    def step(
        self,
        epistemic_pluralism=0.5,
        institutional_openness=0.5,
        consensus_pressure=0.2,
        dogmatism_risk=0.2,
        closure_pressure=0.1,
    ):

        epistemic_pluralism = (
            self._bounded(
                epistemic_pluralism
            )
        )

        institutional_openness = (
            self._bounded(
                institutional_openness
            )
        )

        consensus_pressure = (
            self._bounded(
                consensus_pressure
            )
        )

        dogmatism_risk = (
            self._bounded(
                dogmatism_risk
            )
        )

        closure_pressure = (
            self._bounded(
                closure_pressure
            )
        )

        anti_dogmatism_capacity = (
            self._bounded(
                (
                    epistemic_pluralism
                    + institutional_openness
                    + (
                        1.0
                        - consensus_pressure
                    )
                    + (
                        1.0
                        - dogmatism_risk
                    )
                    + (
                        1.0
                        - closure_pressure
                    )
                ) / 5.0
            )
        )

        epistemic_hegemony_risk = (
            self._bounded(
                (
                    consensus_pressure
                    + dogmatism_risk
                    + closure_pressure
                    + (
                        1.0
                        - epistemic_pluralism
                    )
                ) / 4.0
            )
        )

        open_governance_index = (
            self._bounded(
                mean(
                    [
                        anti_dogmatism_capacity,
                        (
                            1.0
                            - epistemic_hegemony_risk
                        ),
                        institutional_openness,
                    ]
                )
            )
        )

        governance_viable = (
            open_governance_index >= 0.60
            and epistemic_hegemony_risk <= 0.70
        )

        return {
            "epistemic_pluralism":
                round(
                    epistemic_pluralism,
                    4,
                ),
            "institutional_openness":
                round(
                    institutional_openness,
                    4,
                ),
            "anti_dogmatism_capacity":
                round(
                    anti_dogmatism_capacity,
                    4,
                ),
            "epistemic_hegemony_risk":
                round(
                    epistemic_hegemony_risk,
                    4,
                ),
            "open_governance_index":
                round(
                    open_governance_index,
                    4,
                ),
            "governance_viable":
                governance_viable,
        }
