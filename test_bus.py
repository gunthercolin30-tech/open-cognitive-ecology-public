import asyncio

from core.event_bus import EventBus


bus = EventBus()


async def listener(payload):

    print("EVENT RECEIVED:", payload)


bus.subscribe(
    "TEST_EVENT",
    listener,
)


async def main():

    await bus.emit(
        "TEST_EVENT",
        {"value": 42},
    )

    await asyncio.sleep(1)


asyncio.run(main())