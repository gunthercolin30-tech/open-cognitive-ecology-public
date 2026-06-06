# visualization/trajectory_renderer.py


class TrajectoryRenderer:
    """
    Manage and render local trajectory memories.

    Each perceptual field maintains only a finite and
    historically unstable memory of observed positions.
    No global trajectory exists.
    """

    def __init__(
        self,
        max_trajectory_length=60,
    ):
        self.local_trajectories = {}
        self.max_trajectory_length = (
            max_trajectory_length
        )

    # =========================================================
    # MEMORY UPDATE
    # =========================================================

    def update(
        self,
        field_index,
        perceived_nodes,
    ):
        """
        Update local trajectory memories.
        """

        if (
            field_index
            not in self.local_trajectories
        ):
            self.local_trajectories[
                field_index
            ] = {}

        local_memory = (
            self.local_trajectories[
                field_index
            ]
        )

        visible_ids = set()

        for node_id, perception in (
            perceived_nodes.items()
        ):
            visible_ids.add(node_id)

            if (
                node_id
                not in local_memory
            ):
                local_memory[node_id] = []

            local_memory[node_id].append(
                (
                    perception["x"],
                    perception["y"],
                    perception["memory"],
                )
            )

            if (
                len(local_memory[node_id])
                > self.max_trajectory_length
            ):
                local_memory[node_id].pop(0)

        forgotten = []

        for node_id, trajectory in (
            local_memory.items()
        ):
            if (
                node_id
                not in visible_ids
            ):
                if len(trajectory) > 0:
                    trajectory.pop(0)

            if len(trajectory) < 2:
                forgotten.append(node_id)

        for node_id in forgotten:
            del local_memory[node_id]

    # =========================================================
    # RENDER
    # =========================================================

    def draw(
        self,
        field_index,
        ax,
        color_function,
    ):
        """
        Draw locally remembered trajectories.
        """

        if (
            field_index
            not in self.local_trajectories
        ):
            return

        local_memory = (
            self.local_trajectories[
                field_index
            ]
        )

        for node_id, trajectory in (
            local_memory.items()
        ):
            if len(trajectory) < 2:
                continue

            color = color_function(node_id)

            for i in range(
                1,
                len(trajectory)
            ):
                x1, y1, m1 = trajectory[i - 1]
                x2, y2, m2 = trajectory[i]

                alpha = (
                    0.01
                    + (
                        i
                        / len(trajectory)
                    ) * 0.10
                )

                alpha *= (
                    (m1 + m2) * 0.5
                )

                ax.plot(
                    [x1, x2],
                    [y1, y2],
                    color=color,
                    alpha=alpha,
                    linewidth=0.6,
                )