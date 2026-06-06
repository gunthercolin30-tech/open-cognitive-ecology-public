import asyncio
from collections import defaultdict


class EventBus:

    def __init__(self):

        self.listeners = defaultdict(list)

    def subscribe(self, event_type, callback):

        self.listeners[event_type].append(callback)

    async def emit(self, event_type, payload=None):

        if event_type not in self.listeners:
            return

        for callback in self.listeners[event_type]:

            asyncio.create_task(
                callback(payload)
            )