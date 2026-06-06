# runtime/build_agent_ecologies.py

from health.health_ecology_process import (
    HealthEcologyProcess,
)

from demography.demographic_ecology_process import (
    DemographicEcologyProcess,
)

from ecologies.energy.energy_ecology_process import (
    EnergyEcologyProcess,
)


def build_agent_ecologies():
    """
    Build agent-based ecologies.

    Covered operational ecologies:
    - health
    - demographic
    - energy
    """

    health_ecology_process = (
        HealthEcologyProcess()
    )

    demographic_ecology_process = (
        DemographicEcologyProcess()
    )

    energy_ecology_process = (
        EnergyEcologyProcess(
            base_environment_energy=1.0,
            global_resource_factor=1.0,
            scarcity_amplification=1.2,
        )
    )

    return {
        "health_ecology_process": (
            health_ecology_process
        ),
        "demographic_ecology_process": (
            demographic_ecology_process
        ),
        "energy_ecology_process": (
            energy_ecology_process
        ),
    }