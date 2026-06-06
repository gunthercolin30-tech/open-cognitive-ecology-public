import random


class EnvironmentManager:

    def __init__(self, event_bus):

        self.event_bus = event_bus

        self.state = {

            "noise": 0.0,

            "activity": 0.0,
        }

    async def tick(self):

        self.state["noise"] = (
            random.random()
        )

        self.state["activity"] = (
            random.random()
        )

        await self.event_bus.emit(

            "ENVIRONMENT_UPDATED",

            self.state,
        )