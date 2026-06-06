import json
from pathlib import Path

MEMORY_FILE = Path("data/memory.json")

SHORT_TERM_LIMIT = 5

LONG_TERM_LIMIT = 20


def load_memory():

    if not MEMORY_FILE.exists():

        return {
            "short_term": [],
            "long_term": [],
            "state": {}
        }

    with open(MEMORY_FILE, "r") as f:
        return json.load(f)


def save_memory(memory):

    MEMORY_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(MEMORY_FILE, "w") as f:
        json.dump(
            memory,
            f,
            indent=2
        )


def add_memory_event(memory, event):

    memory["short_term"].append(event)

    if len(memory["short_term"]) > SHORT_TERM_LIMIT:

        oldest_event = (
            memory["short_term"].pop(0)
        )

        compressed_event = compress_event(
            oldest_event
        )

        memory["long_term"].append(
            compressed_event
        )

    if len(memory["long_term"]) > LONG_TERM_LIMIT:

        memory["long_term"] = sorted(
            memory["long_term"],
            key=lambda x: x["salience"],
            reverse=True
        )

        memory["long_term"] = (
            memory["long_term"][
                :LONG_TERM_LIMIT
            ]
        )

    return memory


def compress_event(event):

    narrative = event["narrative"]

    compressed = {
        "time": narrative["time"],
        "identity": narrative["identity"],
        "summary": narrative["event"]["content"],
        "salience": narrative["salience"]
    }

    return compressed