PRIMITIVE = "trajectory_criticality"
DESCRIPTION = "Trajectory criticality."
DEPENDENCIES = []

"""Critical thresholds in trajectory dynamics under constraints."""

CONCEPT = "trajectory_criticality"

DESCRIPTION = (
    "Describes critical conditions under which small parameter changes can "
    "induce qualitative transformations in trajectory dynamics."
)


class TrajectoryCriticality:
    """Auto-generated activation class for trajectory_criticality."""

    PRIMITIVE = "trajectory_criticality"

    def diagnostics(self):
        return {
            "primitive": self.PRIMITIVE,
            "status": "active",
        }

