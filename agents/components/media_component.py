# agents/components/media_component.py

import random


class MediaComponent:
    """
    Local media dynamics.

    This component models:
    - information production
    - source credibility
    - audience attention
    - message amplification
    - misinformation
    - media polarization
    - virality
    - trust erosion

    No universal truth channel.
    No centralized broadcaster.
    No stable information regime.
    """

    def __init__(self):
        # =====================================================
        # PRODUCTION CAPACITY
        # =====================================================

        self.information_production = random.uniform(
            0.2,
            1.0,
        )

        self.source_credibility = random.uniform(
            0.2,
            1.0,
        )

        self.audience_attention = random.uniform(
            0.2,
            1.0,
        )

        self.message_amplification = random.uniform(
            0.1,
            1.0,
        )

        # =====================================================
        # MEDIA STATE
        # =====================================================

        self.misinformation = random.uniform(
            0.0,
            0.5,
        )

        self.media_polarization = random.uniform(
            0.0,
            0.6,
        )

        self.virality = random.uniform(
            0.0,
            0.5,
        )

        self.trust_erosion = random.uniform(
            0.0,
            0.3,
        )

        # =====================================================
        # HISTORY
        # =====================================================

        self.media_history = []

    # =========================================================
    # CORE DYNAMICS
    # =========================================================

    def update_media_dynamics(self):
        """
        Update local media state.
        """

        # Virality depends on production, attention,
        # amplification, and credibility.
        target_virality = (
            self.information_production
            * self.audience_attention
            * self.message_amplification
            * (
                0.5
                + 0.5
                * self.source_credibility
            )
        )

        self.virality += (
            0.05
            * (
                target_virality
                - self.virality
            )
        )

        # Misinformation fluctuates
        self.misinformation += random.uniform(
            -0.01,
            0.01,
        )

        # Polarization increases with misinformation
        self.media_polarization += (
            0.02
            * (
                self.misinformation
                - self.media_polarization
            )
        )

        # Trust erosion follows misinformation
        self.trust_erosion += (
            0.02
            * (
                self.misinformation
                - self.trust_erosion
            )
        )

        # Attention fluctuates
        self.audience_attention += random.uniform(
            -0.01,
            0.01,
        )

        # Amplification fluctuates
        self.message_amplification += random.uniform(
            -0.01,
            0.01,
        )

        # Credibility slowly changes
        self.source_credibility += random.uniform(
            -0.005,
            0.005,
        )

        # =====================================================
        # CLAMP VALUES
        # =====================================================

        self.source_credibility = max(
            0.0,
            min(1.0, self.source_credibility),
        )

        self.audience_attention = max(
            0.0,
            min(1.0, self.audience_attention),
        )

        self.message_amplification = max(
            0.0,
            min(1.0, self.message_amplification),
        )

        self.misinformation = max(
            0.0,
            min(1.0, self.misinformation),
        )

        self.media_polarization = max(
            0.0,
            min(1.0, self.media_polarization),
        )

        self.virality = max(
            0.0,
            min(1.0, self.virality),
        )

        self.trust_erosion = max(
            0.0,
            min(1.0, self.trust_erosion),
        )

        # =====================================================
        # HISTORY
        # =====================================================

        self.media_history.append(
            {
                "virality": self.virality,
                "credibility": (
                    self.source_credibility
                ),
                "misinformation": (
                    self.misinformation
                ),
                "polarization": (
                    self.media_polarization
                ),
                "trust_erosion": (
                    self.trust_erosion
                ),
            }
        )

        if len(self.media_history) > 200:
            self.media_history.pop(0)