from collections.abc import Iterator
from datetime import date

from planexa.domain.errors import PlanexaError
from planexa.domain.project import Project
from planexa.domain.task import Task
from planexa.structures.linked_deque import LinkedDeque


class PlanexaService:
    """Casos de uso y coordinacion del Deque principal de proyectos."""

    _projects: LinkedDeque[Project]

    # O(1): Inicializa el sistema con un Deque principal vacio.
    def __init__(self) -> None:
        """Crea el almacenamiento principal sin indices auxiliares."""

        self._projects = LinkedDeque()

    @property
    # O(1): Expone la cantidad de proyectos registrados.
    def project_count(self) -> int:
        """Retorna el tamaño del Deque principal."""

        return len(self._projects)

    # O(n): Verifica unicidad recorriendo el Deque e inserta por rear.
    def create_project(
        self, code: str, name: str, description: str, owner: str, start_date: date
    ) -> Project:
        """Registra un proyecto con codigo unico al final de la estructura."""

        project = Project(code, name, description, owner, start_date)
        if self._projects.any(lambda current: current.code == project.code):
            raise PlanexaError("Ya existe un proyecto con ese codigo")

        self._projects.insert_rear(project)
        return project

    # O(n): Localiza un proyecto recorriendo cada nodo desde front.
    def find_project(self, code: str) -> Project | None:
        """Busca por codigo en el Deque, sin diccionarios auxiliares."""

        normalized = code.strip()
        return self._projects.find(lambda project: project.code == normalized)

    # O(n): Obtiene un proyecto existente o comunica un error de dominio.
    def get_project(self, code: str) -> Project:
        """Centraliza la comprobacion de existencia de proyectos."""

        project = self.find_project(code)
        if project is None:
            raise PlanexaError("Proyecto no encontrado")
        return project

    # O(n): Ubica un proyecto y actualiza exclusivamente sus campos editables.
    def edit_project(
        self, code: str, name: str, description: str, owner: str, start_date: date
    ) -> Project:
        """Edita los detalles del proyecto conservando su codigo original."""

        project = self.get_project(code)
        project.update(name, description, owner, start_date)
        return project

    # O(n): Busca y elimina un nodo siempre que no tenga tareas ni historial.
    def delete_project(self, code: str) -> Project:
        """Elimina un proyecto vacio mediante ajuste directo de enlaces."""

        project = self.get_project(code)
        if project.pending_count or project.processed_count:
            raise PlanexaError("No se puede eliminar un proyecto con tareas o historial")

        deleted = self._projects.remove_first(lambda current: current is project)
        assert deleted is not None
        return deleted

    # O(n): Valida el ID en ambos Deques y registra la tarea en rear.
    def add_task(
        self, project_code: str, task_id: str, title: str, description: str,
        priority: str, estimated_hours: float
    ) -> Task:
        """Registra una tarea pendiente con ID unico dentro del proyecto."""

        project = self.get_project(project_code)
        task = Task(task_id, title, description, priority, estimated_hours)
        if project.pending_tasks.any(lambda current: current.id == task.id) or (
            project.task_history.any(lambda current: current.id == task.id)
        ):
            raise PlanexaError("Ya existe una tarea con ese ID dentro del proyecto")

        project.pending_tasks.insert_rear(task)
        return task

    # O(n): Localiza el proyecto y mueve su primera tarea al historial.
    def process_task_front(self, project_code: str) -> Task:
        """Procesa la tarea de front y la agrega al rear del historial."""

        project = self.get_project(project_code)
        task = project.pending_tasks.delete_front()
        if task is None:
            raise PlanexaError("No hay tareas pendientes para procesar")
        project.task_history.insert_rear(task)
        return task

    # O(n): Localiza el proyecto y mueve su ultima tarea al historial.
    def process_task_rear(self, project_code: str) -> Task:
        """Procesa la tarea de rear y la agrega al rear del historial."""

        project = self.get_project(project_code)
        task = project.pending_tasks.delete_rear()
        if task is None:
            raise PlanexaError("No hay tareas pendientes para procesar")
        project.task_history.insert_rear(task)
        return task

    # O(n): Localiza el proyecto y restaura el ultimo procesado al frente.
    def undo_last_task(self, project_code: str) -> Task:
        """Ejecuta delete_rear del historial e insert_front en pendientes."""

        project = self.get_project(project_code)
        task = project.task_history.delete_rear()
        if task is None:
            raise PlanexaError("No hay tareas en el historial para deshacer")
        project.pending_tasks.insert_front(task)
        return task

    # O(n): Expone el recorrido directo de proyectos sin copiar los elementos.
    def iter_projects(self) -> Iterator[Project]:
        """Produce los proyectos del frente hacia el final."""

        yield from self._projects

    # O(n): Expone el recorrido inverso usando enlaces prev.
    def iter_projects_reverse(self) -> Iterator[Project]:
        """Produce los proyectos desde rear hasta front."""

        yield from reversed(self._projects)

    # O(n): Busca el proyecto y recorre directamente sus tareas pendientes.
    def iter_tasks(self, project_code: str, *, reverse: bool = False) -> Iterator[Task]:
        """Recorre tareas pendientes en el sentido solicitado."""

        project = self.get_project(project_code)
        yield from reversed(project.pending_tasks) if reverse else project.pending_tasks

    # O(n): Busca el proyecto y recorre su historial de procesamiento.
    def iter_task_history(self, project_code: str) -> Iterator[Task]:
        """Recorre las tareas procesadas desde front hacia rear."""

        yield from self.get_project(project_code).task_history

    # O(1): Consulta el primer proyecto sin modificar el Deque.
    def first_project(self) -> Project | None:
        """Obtiene el valor del extremo front de proyectos."""

        return self._projects.get_front()

    # O(1): Consulta el ultimo proyecto sin modificar el Deque.
    def last_project(self) -> Project | None:
        """Obtiene el valor del extremo rear de proyectos."""

        return self._projects.get_rear()

    # O(n): Selecciona el primer proyecto con mayor cantidad de tareas pendientes.
    def project_with_most_tasks(self) -> Project | None:
        """Calcula el proyecto de mayor carga mediante un recorrido lineal."""

        result: Project | None = None
        for project in self._projects:
            if result is None or project.pending_count > result.pending_count:
                result = project
        return result

    # O(n): Suma las tareas pendientes de los proyectos sin recorrer cada Deque interno.
    def total_pending_tasks(self) -> int:
        """Suma los tamaños almacenados en cada proyecto."""

        total = 0
        for project in self._projects:
            total += project.pending_count
        return total

    # O(n): Suma las tareas procesadas de todos los proyectos.
    def total_processed_tasks(self) -> int:
        """Calcula el total de elementos en los historiales por sus tamaños."""

        total = 0
        for project in self._projects:
            total += project.processed_count
        return total
