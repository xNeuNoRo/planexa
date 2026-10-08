import math
from dataclasses import dataclass


@dataclass(slots=True)
class Task:
    """Representa una tarea perteneciente a un unico proyecto."""

    id: str
    title: str
    description: str
    priority: str
    estimated_hours: float

    # O(1): Normaliza y valida los atributos obligatorios de una tarea.
    def __post_init__(self) -> None:
        """Impide tareas sin informacion o con una estimacion invalida."""

        self.id = self.id.strip()
        self.title = self.title.strip()
        self.description = self.description.strip()
        self.priority = self.priority.strip()

        if not self.id:
            raise ValueError("El ID de tarea es obligatorio")
        if not self.title:
            raise ValueError("El titulo de la tarea es obligatorio")
        if not self.description:
            raise ValueError("La descripcion de la tarea es obligatoria")
        if not self.priority:
            raise ValueError("La prioridad es obligatoria")
        if isinstance(self.estimated_hours, bool) or not isinstance(
            self.estimated_hours, (int, float)
        ):
            raise ValueError("La estimacion debe ser numerica")
        if not math.isfinite(self.estimated_hours) or self.estimated_hours <= 0:
            raise ValueError("La estimacion debe ser mayor que cero y finita")

        self.estimated_hours = float(self.estimated_hours)
