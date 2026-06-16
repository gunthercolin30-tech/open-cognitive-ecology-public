#!/usr/bin/env python3
from ontology.supreme_representative_runtime import SupremeRepresentativeRuntime


def main() -> None:
    leader = SupremeRepresentativeRuntime()
    print(leader.respond("Bonjour, quelle est votre vision de l'avenir ?"))


if __name__ == "__main__":
    main()
