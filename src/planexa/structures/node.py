from dataclasses import dataclass
from typing import Self


@dataclass(slots=True)
class DoublyNode[T]:
    """Nodo generico con enlaces al elemento anterior y al siguiente."""

    value: T
    prev: Self | None = None
    next: Self | None = None
