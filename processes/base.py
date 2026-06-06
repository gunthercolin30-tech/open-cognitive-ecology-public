class CognitiveProcess:

    def __init__(self, name):

        self.name = name

        self.energy = 100.0

        self.priority = 1.0

        self.active = True

        self.context = None

    def bind_context(self, context):

        self.context = context

    def compute_score(self):

        return (

            self.priority
            * self.energy

        )

    async def step(self):

        raise NotImplementedError