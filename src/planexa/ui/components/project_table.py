from collections.abc import Iterable

from planexa.domain.project import Project
from planexa.ui.theme import Theme


class ProjectTable:
    """Presentacion de proyectos sin ocultar sus datos obligatorios."""

    # O(n): Imprime los proyectos recibidos en el orden del iterador.
    def render(self, projects: Iterable[Project]) -> bool:
        """Muestra cada proyecto y todos sus atributos sin truncamientos."""

        found = False
        for project in projects:
            found = True
            print(f"{Theme.CYAN}{Theme.BOLD}{project.code} · {project.name}{Theme.RESET}")
            print(f"  Descripcion: {project.description}")
            print(f"  Responsable: {project.owner} | Inicio: {project.start_date:%Y-%m-%d}")
            print(
                f"  Tareas pendientes: {project.pending_count} | "
                f"Procesadas: {project.processed_count}"
            )
            print(f"{Theme.GRAY}{'─' * 68}{Theme.RESET}")
        return found
