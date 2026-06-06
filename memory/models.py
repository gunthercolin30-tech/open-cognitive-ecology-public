from dataclasses import dataclass
from dataclasses import field

from typing import List


@dataclass
class MemoryNode:

    id: str

    content: str

    salience: float = 0.0

    tension: float = 0.0

    energy: float = 1.0

    tags: List[str] = field(
        default_factory=list
    )