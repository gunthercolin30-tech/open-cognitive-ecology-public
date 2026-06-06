# agents/components/educational_component.py

import random


class EducationalComponent:
    """
    Local educational dynamics.

    This component models:
    - learning capacity
    - teaching capacity
    - accumulated education
    - forgetting
    - pedagogical innovation
    - educational inequality
    - institutional attachment
    - educational prestige

    No universal curriculum.
    No centralized school system.
    No final knowledge state.
    """

    def __init__(self):
        # =====================================================
        # LEARNING CAPACITIES
        # =====================================================

        self.learning_capacity = random.uniform(
            0.3,
            1.0,
        )

        self.teaching_capacity = random.uniform(
            0.2,
            1.0,
        )

        # =====================================================
        # EDUCATIONAL STATE
        # =====================================================

        self.education_level = random.uniform(
            0.1,
            0.6,
        )

        self.educational_prestige = random.uniform(
            0.1,
            0.5,
        )

        self.pedagogical_innovation = random.uniform(
            0.0,
            0.4,
        )

        self.forgetting_rate = random.uniform(
            0.001,
            0.02,
        )

        self.educational_inequality = random.uniform(
            0.0,
            0.5,
        )

        self.institutional_attachment = random.uniform(
            0.0,
            1.0,
        )

        # =====================================================
        # HISTORY
        # =====================================================

        self.educational_history = []

    # =========================================================
    # CORE DYNAMICS
    # =========================================================

    def update_educational_dynamics(self):
        """
        Update local educational state.
        """

        # Learning accumulation
        gain = (
            self.learning_capacity
            * (0.01 + 0.03 * self.pedagogical_innovation)
            * (1.0 - self.educational_inequality)
        )

        self.education_level += gain

        # Forgetting
        self.education_level *= (
            1.0 - self.forgetting_rate
        )

        # Prestige follows educational level
        self.educational_prestige += (
            0.02
            * (
                self.education_level
                - self.educational_prestige
            )
        )

        # Pedagogical innovation evolves
        self.pedagogical_innovation += random.uniform(
            -0.01,
            0.01,
        )

        # Educational inequality fluctuates
        self.educational_inequality += random.uniform(
            -0.01,
            0.01,
        )

        # Institutional attachment evolves slowly
        self.institutional_attachment += random.uniform(
            -0.005,
            0.005,
        )

        # =====================================================
        # CLAMP VALUES
        # =====================================================

        self.education_level = max(
            0.0,
            min(10.0, self.education_level),
        )

        self.educational_prestige = max(
            0.0,
            min(10.0, self.educational_prestige),
        )

        self.pedagogical_innovation = max(
            0.0,
            min(1.0, self.pedagogical_innovation),
        )

        self.educational_inequality = max(
            0.0,
            min(1.0, self.educational_inequality),
        )

        self.institutional_attachment = max(
            0.0,
            min(1.0, self.institutional_attachment),
        )

        # =====================================================
        # HISTORY
        # =====================================================

        self.educational_history.append(
            {
                "education_level": (
                    self.education_level
                ),
                "educational_prestige": (
                    self.educational_prestige
                ),
                "pedagogical_innovation": (
                    self.pedagogical_innovation
                ),
                "educational_inequality": (
                    self.educational_inequality
                ),
            }
        )

        if len(self.educational_history) > 200:
            self.educational_history.pop(0)