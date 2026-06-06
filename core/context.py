from dataclasses import dataclass


@dataclass
class CognitiveContext:

    memory_manager: object

    salience_engine: object

    environment_manager: object

    cognitive_graph: object

    event_bus: object