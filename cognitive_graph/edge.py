# cognitive_graph/edge.py

class CognitiveEdge:
    def __init__(
        self,
        source,
        target,
        weight=1.0,
        relation="association"
    ):
        self.source = source

        self.target = target

        self.weight = weight

        self.relation = relation