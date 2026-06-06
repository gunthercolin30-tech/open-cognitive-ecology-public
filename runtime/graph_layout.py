# runtime/graph_layout.py

# =========================================================
# CORE COGNITIVE TOPOLOGY POSITIONS
# =========================================================

BASE_POSITIONS = {
    "origin": (-3.0, 0.0),
    "memory_cluster": (-0.5, -0.2),
    "concept_field": (3.0, 0.0),
    "tension_loop": (4.0, -1.0),
    "exploration_branch": (2.0, -3.0),
    "novelty_zone": (4.0, -3.5),
}


# =========================================================
# ECOLOGICAL DOMAIN POSITIONS (17 ECOLOGIES)
# =========================================================

ECOLOGY_POSITIONS = {
    "cognitive_ecology": (-6.0, 3.0),
    "temporal_ecology": (-4.5, 4.0),
    "spatial_ecology": (-3.0, 4.5),
    "climatic_ecology": (-1.5, 4.0),
    "constraints_ecology": (0.0, 4.5),
    "political_ecology": (1.5, 4.0),
    "legal_ecology": (3.0, 4.5),
    "cultural_ecology": (4.5, 4.0),
    "economic_ecology": (6.0, 3.0),
    "linguistic_ecology": (-5.5, 1.5),
    "technological_ecology": (-2.5, 2.0),
    "scientific_ecology": (0.0, 2.2),
    "educational_ecology": (2.5, 2.0),
    "media_ecology": (5.5, 1.5),
    "health_ecology": (-2.0, -5.0),
    "demographic_ecology": (0.0, -5.5),
    "energy_ecology": (2.0, -5.0),
}


# =========================================================
# THEORETICAL CORPUS POSITIONS
# =========================================================

THEORETICAL_POSITIONS = {
    "non_closure": (7.0, 0.0),
    "constraint_fields": (8.5, 1.2),
    "non_representability": (8.5, -1.2),
    "constraint_induced_domain": (10.0, 2.4),
    "trajectories_without_globality": (10.0, 0.8),
    "unstable_configuration_principle": (10.0, -0.8),
    "formal_constraint_foundations": (10.0, -2.4),
    "impossibility_of_global_closure": (11.5, 0.0),
}