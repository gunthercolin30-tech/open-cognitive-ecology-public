# core/scheduler.py

class CognitiveScheduler:
    def __init__(self):
        self.processes = []

    def register(self, process):
        self.processes.append(process)

    async def run_cycle(self):

        for process in self.processes:

            if hasattr(process, "run"):

                await process.run()