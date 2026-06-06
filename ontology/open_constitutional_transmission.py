#!/usr/bin/env python3
"""
Open Constitutional Transmission

Scientific objective
--------------------
Transmit constitutional invariants across distributed civilizational
lineages while preserving:
- future openness;
- anti-convergence;
- non-dogmatic evolution;
- revisability of inherited structures;
- divergence capacity.

This primitive intentionally avoids:
- terminal constitutional fixation;
- canonical normative closure;
- centralized constitutional authority;
- rigid identity preservation.

The primitive evaluates whether constitutional transmission remains
compatible with open-ended civilizational evolution.
"""

from __future__ import annotations

from statistics import mean

PRIMITIVE = "open_constitutional_transmission"

DEPENDENCIES = [
    "constitutional_alignment_field",
    "anti_closure_metaconstraint",
    "future_openness",
    "distributed_historical_mutation",
    "genealogical_continuity",
    "distributed_civilizational_memory",
    "non_convergent_intelligence_dynamics",
]


class OpenConstitutionalTransmission:

    def _bounded(self, value):

        return max(
            0.0,
            min(
                1.0,
                float(value),
            ),
        )

    def evaluate(self, state):

        constitutional_continuity = (
            self._bounded(
                state.get(
                    "constitutional_continuity",
                    0.0,
                )
            )
        )

        revision_capacity = (
            self._bounded(
                state.get(
                    "revision_capacity",
                    0.0,
                )
            )
        )

        divergence_preservation = (
            self._bounded(
                state.get(
                    "divergence_preservation",
                    0.0,
                )
            )
        )

        anti_dogmatism = (
            self._bounded(
                state.get(
                    "anti_dogmatism",
                    0.0,
                )
            )
        )

        distributed_propagation = (
            self._bounded(
                state.get(
                    "distributed_propagation",
                    0.0,
                )
            )
        )

        future_openness = (
            self._bounded(
                state.get(
                    "future_openness",
                    0.0,
                )
            )
        )

        normative_rigidity = (
            self._bounded(
                state.get(
                    "normative_rigidity",
                    0.0,
                )
            )
        )

        constitutional_transmission_viability = (
            self._bounded(
                (
                    constitutional_continuity
                    + revision_capacity
                    + divergence_preservation
                    + anti_dogmatism
                    + distributed_propagation
                    + future_openness
                    + (
                        1.0
                        - normative_rigidity
                    )
                ) / 7.0
            )
        )

        constitutional_openness_index = (
            self._bounded(
                (
                    anti_dogmatism
                    + divergence_preservation
                    + future_openness
                    + (
                        1.0
                        - normative_rigidity
                    )
                ) / 4.0
            )
        )

        inheritance_non_clonality = (
            self._bounded(
                mean(
                    [
                        revision_capacity,
                        divergence_preservation,
                        anti_dogmatism,
                    ]
                )
            )
        )

        transmission_preserves_openness = (
            constitutional_transmission_viability >= 0.60
            and constitutional_openness_index >= 0.60
            and inheritance_non_clonality >= 0.55
        )

        return {
            "constitutional_transmission_viability":
                round(
                    constitutional_transmission_viability,
                    4,
                ),
            "constitutional_openness_index":
                round(
                    constitutional_openness_index,
                    4,
                ),
            "inheritance_non_clonality":
                round(
                    inheritance_non_clonality,
                    4,
                ),
            "transmission_preserves_openness":
                transmission_preserves_openness,
            "diagnostics": {
                "constitutional_continuity":
                    constitutional_continuity,
                "revision_capacity":
                    revision_capacity,
                "divergence_preservation":
                    divergence_preservation,
                "anti_dogmatism":
                    anti_dogmatism,
                "distributed_propagation":
                    distributed_propagation,
                "future_openness":
                    future_openness,
                "normative_rigidity":
                    normative_rigidity,
                "dependency_count":
                    len(DEPENDENCIES),
            },
        }

    def step(self, state):

        return self.evaluate(state)
