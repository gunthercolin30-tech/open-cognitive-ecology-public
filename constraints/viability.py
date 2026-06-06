def evaluate_viability(agent_state):

    constraints = {
        "memory_coherence": True,
        "identity_persistence": True,
        "non_closure": True
    }

    return constraints