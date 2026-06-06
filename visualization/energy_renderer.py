# visualization/energy_renderer.py

class EnergyRenderer:
    """
    Renderer for the Energy Ecology.

    Visualizes:
    - Energy distribution across agents
    - Fatigue field (systemic exhaustion)
    - Resource accessibility pressure
    - Global energy stress
    - Depletion dynamics

    Supports two complementary interfaces:
    - render(energy_state, agents): textual system-level report
    - draw(node, x, y, ax): graphical overlay for matplotlib
    """

    def __init__(self):
        self.history = []

    # =========================================================
    # MAIN ENTRY POINT
    # =========================================================

    def render(self, energy_state, agents):
        """
        Render energy ecology at system scale + agent scale.
        """

        if energy_state is None:
            energy_state = {}

        self.history.append(energy_state)

        self._render_global(energy_state)
        self._render_agents(agents)
        self._render_summary_field(energy_state)

    # =========================================================
    # GRAPHICAL OVERLAY
    # =========================================================

    def draw(self, node, x, y, ax):
        """
        Draw an energy halo around a node.

        Visual encoding:
        - circle radius increases with energy reserve
        - transparency increases with available energy
        - depleted agents receive a red marker
        - high fatigue adds an orange contour
        """

        energy = getattr(
            node,
            "energy_component",
            None,
        )

        if energy is None:
            return

        energy_reserve = getattr(
            energy,
            "energy_reserve",
            0.0,
        )

        fatigue = getattr(
            energy,
            "fatigue",
            0.0,
        )

        depleted = getattr(
            energy,
            "is_energy_depleted",
            False,
        )

        # Normalize values
        energy_reserve = max(
            0.0,
            min(energy_reserve, 1.0),
        )

        fatigue = max(
            0.0,
            min(fatigue, 1.0),
        )

        # -----------------------------------------------------
        # MAIN ENERGY HALO
        # -----------------------------------------------------

        radius = 0.45 + 0.75 * energy_reserve
        alpha = 0.05 + 0.20 * energy_reserve

        halo = ax.add_patch(
            __import__(
                "matplotlib.patches",
                fromlist=["Circle"],
            ).Circle(
                (x, y),
                radius=radius,
                fill=False,
                linewidth=2.0,
                edgecolor="#FFD700",  # gold
                alpha=alpha,
            )
        )

        # Avoid linter warnings about unused object
        _ = halo

        # -----------------------------------------------------
        # FATIGUE CONTOUR
        # -----------------------------------------------------

        if fatigue > 0.25:
            ax.add_patch(
                __import__(
                    "matplotlib.patches",
                    fromlist=["Circle"],
                ).Circle(
                    (x, y),
                    radius=radius + 0.12,
                    fill=False,
                    linewidth=1.2,
                    edgecolor="#FF8C00",  # orange
                    alpha=0.05 + 0.25 * fatigue,
                )
            )

        # -----------------------------------------------------
        # DEPLETION MARKER
        # -----------------------------------------------------

        if depleted:
            ax.scatter(
                [x],
                [y],
                s=18,
                c="#CC0000",
                alpha=0.8,
                zorder=20,
            )

    # =========================================================
    # GLOBAL VIEW
    # =========================================================

    def _render_global(self, state):

        print("\n[ENERGY ECOLOGY FIELD]")

        print(
            f"total_energy={state.get('total_energy', 0):.3f}"
        )

        print(
            f"average_fatigue={state.get('average_fatigue', 0):.3f}"
        )

        print(
            f"depleted_ratio={state.get('depleted_agents_ratio', 0):.3f}"
        )

        print(
            f"system_stress={state.get('system_stress', 0):.3f}"
        )

        # Derived interpretation layer
        stress = state.get("system_stress", 0)

        if stress < 0.2:
            regime = "LOW_PRESSURE"
        elif stress < 0.5:
            regime = "MODERATE_PRESSURE"
        elif stress < 0.8:
            regime = "HIGH_PRESSURE"
        else:
            regime = "CRITICAL_DEPLETION"

        print(f"energy_regime={regime}")

    # =========================================================
    # AGENT VIEW
    # =========================================================

    def _render_agents(self, agents):

        print("\n[AGENT ENERGY STATES]")

        for agent in agents:

            energy = getattr(
                agent,
                "energy_component",
                None,
            )

            if energy is None:
                continue

            print(
                f"{agent.state.get('name', '?')} | "
                f"E={getattr(energy, 'energy_reserve', 0.0):.2f} | "
                f"F={getattr(energy, 'fatigue', 0.0):.2f} | "
                f"X={getattr(energy, 'exhaustion', 0.0):.2f} | "
                f"A={'ALIVE' if getattr(energy, 'is_alive', True) else 'DEAD'} | "
                f"DEP={getattr(energy, 'is_energy_depleted', False)}"
            )

    # =========================================================
    # FIELD ABSTRACTION
    # =========================================================

    def _render_summary_field(self, state):
        """
        Produces a compact field-like representation
        usable by cognitive_field_visualizer.
        """

        field_intensity = state.get(
            "system_stress",
            0.0,
        )

        depletion = state.get(
            "depleted_agents_ratio",
            0.0,
        )

        # Synthetic field projection
        energy_field = field_intensity * (
            1.0 + depletion
        )

        print("\n[ENERGY FIELD PROJECTION]")
        print(
            f"field_intensity={energy_field:.3f}"
        )

        if energy_field < 0.2:
            print("field_state=EXPANSIVE")
        elif energy_field < 0.5:
            print("field_state=CONTRACTING")
        else:
            print("field_state=COLLAPSING")