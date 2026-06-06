import random


ENVIRONMENT_EVENTS = [

    {
        "type": "calm",
        "content": "world remains stable",
        "intensity": 0.2
    },

    {
        "type": "signal",
        "content": "weak anomalous signal detected",
        "intensity": 0.5
    },

    {
        "type": "rupture",
        "content": "unexpected structural rupture",
        "intensity": 0.95
    },

    {
        "type": "resource",
        "content": "new resource discovered",
        "intensity": 0.7
    },

    {
        "type": "noise",
        "content": "background noise increases",
        "intensity": 0.3
    }
]


def generate_environment_event():

    return random.choice(
        ENVIRONMENT_EVENTS
    )