"""
Artificial Society CLI

Console unifiée de pilotage de la société artificielle.
"""

from __future__ import annotations

PRIMITIVE = "artificial_society_cli"

DEPENDENCIES = ['supreme_representative_chat_interface', 'society_simulation_runner', 'civilizational_dashboard', 'conversation_memory_archive']


class ArtificialSocietyCLI:
    def __init__(self) -> None:
        from ontology.civilizational_dashboard import CivilizationalDashboard
        from ontology.conversation_memory_archive import ConversationMemoryArchive
        from ontology.society_simulation_runner import SocietySimulationRunner
        from ontology.supreme_representative_chat_interface import (
            SupremeRepresentativeChatInterface,
        )

        self.dashboard = CivilizationalDashboard()
        self.archive = ConversationMemoryArchive()
        self.runner = SocietySimulationRunner()
        self.chat = SupremeRepresentativeChatInterface()

    def run(self) -> None:
        print("Artificial Society CLI")
        print("Commandes : chat, simulate, dashboard, archives, quit")

        while True:
            try:
                command = input("CLI > ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\nAu revoir.")
                break

            if command in ("quit", "exit", "q"):
                print("Au revoir.")
                break
            elif command == "chat":
                self.chat.run()
            elif command == "simulate":
                self.runner.run(cycles=5)
            elif command == "dashboard":
                print(self.dashboard.step())
            elif command == "archives":
                print(self.archive.list_archives())
            elif not command:
                continue
            else:
                print("Commande inconnue.")

    def step(self) -> dict:
        return {
            "primitive": PRIMITIVE,
            "cli_ready": True,
            "classification": "Artificial Society CLI Operational",
            "diagnostics": {
                "dependencies": DEPENDENCIES,
            },
        }


def main() -> None:
    ArtificialSocietyCLI().run()


if __name__ == "__main__":
    main()
