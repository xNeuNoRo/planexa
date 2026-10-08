from collections.abc import Iterable

from planexa.domain.task import Task
from planexa.ui.theme import Theme


class TaskTable:
    """Presentacion completa de tareas pendientes o procesadas."""

    # O(n): Renderiza todos los datos de cada tarea sin modificar el Deque.
    def render(self, tasks: Iterable[Task]) -> bool:
        """Muestra ID, titulo, descripcion, prioridad y estimacion."""

        found = False
        for task in tasks:
            found = True
            print(f"{Theme.CYAN}{Theme.BOLD}{task.id} · {task.title}{Theme.RESET}")
            print(f"  Descripcion: {task.description}")
            print(f"  Prioridad: {task.priority} | Estimacion: {task.estimated_hours:g} h")
            print(f"{Theme.GRAY}{'─' * 68}{Theme.RESET}")
        return found
