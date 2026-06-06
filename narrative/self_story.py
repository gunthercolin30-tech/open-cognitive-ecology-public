from datetime import datetime
import random


def build_narrative(agent_state, event):

    timestamp = datetime.now().isoformat()

    base_salience = event["intensity"]

    variability = random.uniform(
        0.0,
        0.3
    )

    salience = min(
        1.0,
        base_salience + variability
    )

    narrative = {
        "time": timestamp,
        "identity": agent_state["name"],
        "event": event,
        "continuity": "agent persists through change",
        "salience": salience
    }

    return narrative