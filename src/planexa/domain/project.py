from dataclasses import dataclass, field
from datetime import date

from planexa.domain.task import Task
from planexa.structures.linked_deque import LinkedDeque


@dataclass(slots=True)
class Project:
    """Proyecto empresarial que administra tareas pendientes e historial."""

    code: str
    name: str
    description: str
    owner: str
    start_date: date
    pending_tasks: LinkedDeque[Task] = field(default_factory=LinkedDeque, init=False, repr=False)
    task_history: LinkedDeque[Task] = field(default_factory=LinkedDeque, init=False, repr=False)

    # O(1): Valida todos los campos obligatorios del proyecto.
    def __post_init__(self) -> None:
        """Asegura que un proyecto se construya con datos consistentes."""

        self.code = self.code.strip()
        if not self.code:
            raise ValueError("El codigo del proyecto es obligatorio")
        self.update(self.name, self.description, self.owner, self.start_date)

    # O(1): Actualiza los campos editables sin modificar el codigo.
    def update(self, name: str, description: str, owner: str, start_date: date) -> None:
        """Valida primero los cambios para evitar ediciones parciales."""

        normalized_name = name.strip()
        normalized_description = description.strip()
        normalized_owner = owner.strip()

        if not normalized_name:
            raise ValueError("El nombre del proyecto es obligatorio")
        if not normalized_description:
            raise ValueError("La descripcion del proyecto es obligatoria")
        if not normalized_owner:
            raise ValueError("El responsable del proyecto es obligatorio")
        if not isinstance(start_date, date):
            raise ValueError("La fecha de inicio debe ser valida")

        self.name = normalized_name
        self.description = normalized_description
        self.owner = normalized_owner
        self.start_date = start_date

    @property
    # O(1): Consulta el numero de tareas pendientes del proyecto.
    def pending_count(self) -> int:
        """Retorna la cantidad de tareas activas sin recorrerlas."""

        return len(self.pending_tasks)

    @property
    # O(1): Consulta cuantas tareas estan procesadas en el historial.
    def processed_count(self) -> int:
        """Retorna la cantidad de tareas procesadas almacenadas."""

        return len(self.task_history)
