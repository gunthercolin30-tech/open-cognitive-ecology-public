import time

from narrative.self_story import (
    build_narrative
)

from constraints.viability import (
    evaluate_viability
)

from world.environment import (
    generate_environment_event
)

from memory.store import (
    load_memory,
    save_memory,
    add_memory_event
)


def run_loop(agent):

    memory = load_memory()

    while True:

        environment_event = (
            generate_environment_event()
        )

        perception = agent.perceive(
            environment_event
        )

        narrative = build_narrative(
            agent.state,
            perception
        )

        viability = evaluate_viability(
            agent.state
        )

        event = {
            "narrative": narrative,
            "viability": viability
        }

        memory = add_memory_event(
            memory,
            event
        )

        save_memory(memory)

        print(
            f"[cycle {agent.state['cycle']}] "
            f"{perception['content']}"
        )

        print(
            f"salience="
            f"{round(narrative['salience'], 2)}"
        )

        print(
            f"short_term="
            f"{len(memory['short_term'])} "
            f"long_term="
            f"{len(memory['long_term'])}"
        )

        print("")

        agent.evolve()

        time.sleep(2)