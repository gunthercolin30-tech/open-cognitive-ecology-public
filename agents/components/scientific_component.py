# agents/components/scientific_component.py

import random


class ScientificComponent:
    """
    Local scientific dynamics.

    This component models:
    - hypothesis generation
    - experimental validation
    - knowledge accumulation
    - controversies
    - paradigm competition
    - conceptual shifts

    No universal truth.
    No final theory.
    No globally stabilized science.
    """

    def __init__(self):
        # =====================================================
        # SCIENTIFIC STATE VARIABLES
        # =====================================================

        # Capacity to generate novel hypotheses.
        self.hypothesis_generation_rate = random.uniform(
            0.2,
            0.8,
        )

        # Reliability of local experiments.
        self.experimental_rigor = random.uniform(
            0.2,
            0.9,
        )

        # Amount of locally stabilized knowledge.
        self.knowledge_stock = random.uniform(
            0.0,
            1.0,
        )

        # Intensity of unresolved scientific disagreement.
        self.controversy_level = random.uniform(
            0.0,
            1.0,
        )

        # Degree of adherence to the current dominant paradigm.
        self.paradigm_alignment = random.uniform(
            0.0,
            1.0,
        )

        # Pressure toward conceptual transformation.
        self.conceptual_shift_pressure = random.uniform(
            0.0,
            1.0,
        )

        # Scientific legitimacy within the surrounding ecology.
        self.scientific_legitimacy = random.uniform(
            0.2,
            0.8,
        )

        # Rate of local anomaly accumulation.
        self.anomaly_load = random.uniform(
            0.0,
            0.5,
        )

        # Resistance to paradigm change.
        self.paradigm_inertia = random.uniform(
            0.1,
            0.9,
        )

        # Degree of scientific fragmentation.
        self.scientific_fragmentation = random.uniform(
            0.0,
            0.5,
        )

    def update_scientific_dynamics(self):
        """
        Update local scientific dynamics.
        """

        # =====================================================
        # HYPOTHESIS GENERATION
        # =====================================================

        hypothesis_flux = (
            self.hypothesis_generation_rate
            * random.uniform(0.8, 1.2)
        )

        # =====================================================
        # EXPERIMENTAL VALIDATION
        # =====================================================

        validation_strength = (
            self.experimental_rigor
            * random.uniform(0.8, 1.2)
        )

        # =====================================================
        # ANOMALY ACCUMULATION
        # =====================================================

        anomaly_increase = (
            hypothesis_flux
            * (1.0 - validation_strength)
            * 0.1
        )

        self.anomaly_load += anomaly_increase

        # =====================================================
        # KNOWLEDGE ACCUMULATION
        # =====================================================

        knowledge_gain = (
            hypothesis_flux
            * validation_strength
            * (1.0 - self.controversy_level)
            * 0.05
        )

        self.knowledge_stock += knowledge_gain

        # =====================================================
        # CONTROVERSIES
        # =====================================================

        controversy_change = (
            self.anomaly_load
            * 0.05
            + random.uniform(-0.02, 0.02)
        )

        self.controversy_level += controversy_change

        # =====================================================
        # CONCEPTUAL SHIFT PRESSURE
        # =====================================================

        self.conceptual_shift_pressure += (
            self.anomaly_load * 0.03
            + self.controversy_level * 0.02
            - self.paradigm_inertia * 0.02
        )

        # =====================================================
        # PARADIGM REALIGNMENT
        # =====================================================

        if self.conceptual_shift_pressure > 1.0:
            shift_strength = (
                self.conceptual_shift_pressure
                - self.paradigm_inertia
            )

            if shift_strength > 0.0:
                self.paradigm_alignment -= (
                    shift_strength * 0.2
                )

                self.knowledge_stock *= 0.9
                self.anomaly_load *= 0.3
                self.controversy_level *= 0.7
                self.conceptual_shift_pressure *= 0.4

        # =====================================================
        # SCIENTIFIC LEGITIMACY
        # =====================================================

        self.scientific_legitimacy += (
            knowledge_gain * 0.2
            - self.controversy_level * 0.02
        )

        # =====================================================
        # FRAGMENTATION
        # =====================================================

        self.scientific_fragmentation += (
            self.controversy_level * 0.01
            - self.paradigm_alignment * 0.005
        )

        # =====================================================
        # PARAMETER DRIFT
        # =====================================================

        self.hypothesis_generation_rate += random.uniform(
            -0.02,
            0.02,
        )

        self.experimental_rigor += random.uniform(
            -0.01,
            0.01,
        )

        # =====================================================
        # CLAMP VALUES
        # =====================================================

        self.hypothesis_generation_rate = max(
            0.0,
            min(1.0, self.hypothesis_generation_rate),
        )

        self.experimental_rigor = max(
            0.0,
            min(1.0, self.experimental_rigor),
        )

        self.knowledge_stock = max(
            0.0,
            min(10.0, self.knowledge_stock),
        )

        self.controversy_level = max(
            0.0,
            min(1.0, self.controversy_level),
        )

        self.paradigm_alignment = max(
            0.0,
            min(1.0, self.paradigm_alignment),
        )

        self.conceptual_shift_pressure = max(
            0.0,
            min(2.0, self.conceptual_shift_pressure),
        )

        self.scientific_legitimacy = max(
            0.0,
            min(1.0, self.scientific_legitimacy),
        )

        self.anomaly_load = max(
            0.0,
            min(2.0, self.anomaly_load),
        )

        self.paradigm_inertia = max(
            0.0,
            min(1.0, self.paradigm_inertia),
        )

        self.scientific_fragmentation = max(
            0.0,
            min(1.0, self.scientific_fragmentation),
        )