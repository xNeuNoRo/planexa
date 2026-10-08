from datetime import date

from planexa.domain.errors import PlanexaError
from planexa.domain.project import Project
from planexa.domain.task import Task
from planexa.ui.components.menu import MenuItem
from planexa.ui.context import UIContext
from planexa.ui.theme import Theme


class MainScreen:
    """Pantalla principal con las doce funcionalidades solicitadas para Planexa."""

    # O(1): Conserva las dependencias de interfaz recibidas por composicion.
    def __init__(self, context: UIContext) -> None:
        """Inicializa una pantalla delgada, sin reglas de negocio."""

        self._context = context

    # O(n): Mantiene las doce opciones del menu y despacha cada seleccion.
    def show(self) -> None:
        """Ejecuta el flujo principal hasta confirmar la salida."""

        items = (
            MenuItem("Crear proyecto", "Registra un proyecto al rear del Deque."),
            MenuItem("Buscar proyecto", "Consulta codigo, atributos y extremos."),
            MenuItem("Editar proyecto", "Modifica los datos sin cambiar el codigo."),
            MenuItem("Eliminar proyecto", "Elimina solo proyectos sin tareas ni historial."),
            MenuItem("Añadir tareas", "Inserta tareas en el rear del Deque de pendientes."),
            MenuItem("Procesar tarea por el frente", "Atiende la primera tarea pendiente."),
            MenuItem("Procesar tarea por el final", "Atiende la ultima tarea pendiente."),
            MenuItem("Deshacer ultima tarea", "Devuelve al front la ultima tarea procesada."),
            MenuItem("Listar proyectos", "Recorre de front a rear o de rear a front."),
            MenuItem("Generar reportes", "Consulta los seis reportes del sistema."),
            MenuItem("Ver estado del sistema", "Muestra los extremos y conteos reales."),
            MenuItem("Salir", "Confirma la salida y muestra el resumen final."),
        )

        while True:
            choice = self._context.menu.choose(
                "MENU PRINCIPAL",
                items,
                subtitle="Gestor de Proyectos y Tareas | Deque doblemente enlazado | Python",
                allow_back=False,
            )
            if choice == 0:
                self._create_project()
            elif choice == 1:
                self._search_project()
            elif choice == 2:
                self._edit_project()
            elif choice == 3:
                self._delete_project()
            elif choice == 4:
                self._add_task()
            elif choice == 5:
                self._process_task(from_front=True)
            elif choice == 6:
                self._process_task(from_front=False)
            elif choice == 7:
                self._undo_task()
            elif choice == 8:
                self._list_projects()
            elif choice == 9:
                self._reports()
            elif choice == 10:
                self._status()
            elif choice == 11 and self._exit():
                return

    # O(1): Solicita los atributos obligatorios compartidos por crear y editar.
    def _project_fields(self) -> tuple[str, str, str, date]:
        """Captura nombre, descripcion, responsable y fecha de inicio."""

        prompt = self._context.prompt
        return (
            prompt.required("Nombre del proyecto: "),
            prompt.required("Descripcion: "),
            prompt.required("Responsable: "),
            prompt.iso_date("Fecha de inicio [AAAA-MM-DD]: "),
        )

    # O(n): Captura datos y agrega un proyecto en el rear del Deque principal.
    def _create_project(self) -> None:
        """Solicita un codigo unico y registra el proyecto."""

        self._context.terminal.screen("CREAR PROYECTO")
        code = self._context.prompt.required("Codigo del proyecto: ")
        name, description, owner, start_date = self._project_fields()
        try:
            project = self._context.planexa_service.create_project(
                code, name, description, owner, start_date
            )
        except (PlanexaError, ValueError) as error:
            self._context.feedback.error(str(error))
            return
        self._show_project_result("PROYECTO REGISTRADO", project)

    # O(n): Busca secuencialmente el codigo y consulta los extremos de sus Deques.
    def _search_project(self) -> None:
        """Muestra los datos del proyecto y sus tareas extremas."""

        self._context.terminal.screen("BUSCAR PROYECTO")
        code = self._context.prompt.required("Codigo del proyecto: ")
        try:
            project = self._context.planexa_service.get_project(code)
        except PlanexaError as error:
            self._context.feedback.error(str(error))
            return

        self._context.terminal.screen("DETALLES DEL PROYECTO")
        self._context.project_table.render((project,))
        first = project.pending_tasks.get_front()
        last = project.pending_tasks.get_rear()
        processed = project.task_history.get_rear()
        print(f"Primera tarea pendiente: {self._task_label(first)}")
        print(f"Ultima tarea pendiente: {self._task_label(last)}")
        print(f"Ultima tarea procesada: {self._task_label(processed)}")
        print()
        self._context.prompt.wait()

    # O(n): Localiza un proyecto y edita sus atributos salvo el codigo.
    def _edit_project(self) -> None:
        """Edita un proyecto conservando su identidad."""

        self._context.terminal.screen("EDITAR PROYECTO")
        code = self._context.prompt.required("Codigo del proyecto: ")
        try:
            existing = self._context.planexa_service.get_project(code)
        except PlanexaError as error:
            self._context.feedback.error(str(error))
            return

        self._context.terminal.screen("EDITAR PROYECTO", f"Codigo fijo: {existing.code}")
        self._context.project_table.render((existing,))
        print("Introduce los nuevos valores:\n")
        name, description, owner, start_date = self._project_fields()
        try:
            updated = self._context.planexa_service.edit_project(
                code, name, description, owner, start_date
            )
        except (PlanexaError, ValueError) as error:
            self._context.feedback.error(str(error))
            return
        self._show_project_result("PROYECTO ACTUALIZADO", updated)

    # O(n): Busca, confirma y elimina un proyecto sin tareas ni historial.
    def _delete_project(self) -> None:
        """Impide eliminar proyectos ocupados y respeta la confirmacion."""

        self._context.terminal.screen("ELIMINAR PROYECTO")
        code = self._context.prompt.required("Codigo del proyecto: ")
        try:
            project = self._context.planexa_service.get_project(code)
        except PlanexaError as error:
            self._context.feedback.error(str(error))
            return

        self._context.project_table.render((project,))
        if not self._context.prompt.confirm("Confirmas eliminar este proyecto?"):
            return
        try:
            self._context.planexa_service.delete_project(code)
        except PlanexaError as error:
            self._context.feedback.error(str(error))
            return
        self._context.feedback.success(f"Proyecto {code} eliminado correctamente.")

    # O(n): Solicita los atributos obligatorios y registra una tarea pendiente.
    def _add_task(self) -> None:
        """Agrega una nueva tarea al rear de pendientes de un proyecto."""

        prompt = self._context.prompt
        self._context.terminal.screen("AÑADIR TAREA")
        project_code = prompt.required("Codigo del proyecto: ")
        task_id = prompt.required("ID de tarea: ")
        title = prompt.required("Titulo: ")
        description = prompt.required("Descripcion: ")
        priority = prompt.required("Prioridad: ")
        hours = prompt.positive_float("Estimacion en horas: ")
        try:
            task = self._context.planexa_service.add_task(
                project_code, task_id, title, description, priority, hours
            )
        except (PlanexaError, ValueError) as error:
            self._context.feedback.error(str(error))
            return
        self._show_task_result("TAREA REGISTRADA", task)

    # O(n): Mueve una tarea desde el extremo elegido hacia rear del historial.
    def _process_task(self, *, from_front: bool) -> None:
        """Ejecuta delete_front o delete_rear sobre el Deque pendiente."""

        title = "PROCESAR TAREA POR EL FRENTE" if from_front else "PROCESAR TAREA POR EL FINAL"
        self._context.terminal.screen(title)
        code = self._context.prompt.required("Codigo del proyecto: ")
        service = self._context.planexa_service
        try:
            task = (
                service.process_task_front(code)
                if from_front
                else service.process_task_rear(code)
            )
        except PlanexaError as error:
            self._context.feedback.error(str(error))
            return
        self._show_task_result("TAREA PROCESADA", task)

    # O(n): Revierte el ultimo procesado desde rear del historial hacia front.
    def _undo_task(self) -> None:
        """Deshace la ultima tarea y la reinserta al frente."""

        self._context.terminal.screen("DESHACER ULTIMA TAREA")
        code = self._context.prompt.required("Codigo del proyecto: ")
        try:
            task = self._context.planexa_service.undo_last_task(code)
        except PlanexaError as error:
            self._context.feedback.error(str(error))
            return
        self._show_task_result("TAREA RESTAURADA AL FRENTE", task)

    # O(n): Recorre los proyectos en el sentido elegido sin colecciones auxiliares.
    def _list_projects(self) -> None:
        """Presenta el contenido del Deque principal en ambos sentidos."""

        items = (
            MenuItem("Front → rear", "Orden de insercion de los proyectos."),
            MenuItem("Rear → front", "Orden inverso de los proyectos."),
        )
        choice = self._context.menu.choose("LISTAR PROYECTOS", items, allow_back=True)
        if choice not in (0, 1):
            return
        service = self._context.planexa_service
        self._context.terminal.screen("LISTADO DE PROYECTOS")
        projects = service.iter_projects() if choice == 0 else service.iter_projects_reverse()
        if not self._context.project_table.render(projects):
            print("No hay proyectos registrados")
        print()
        self._context.prompt.wait()

    # O(n): Ejecuta los seis reportes solicitados usando recorridos directos.
    def _reports(self) -> None:
        """Separa la navegacion del reporte de su calculo de dominio."""

        items = (
            MenuItem("Total de proyectos", "Cantidad de proyectos en el Deque."),
            MenuItem("Tareas front → rear", "Tareas pendientes en orden natural."),
            MenuItem("Tareas rear → front", "Tareas pendientes en orden inverso."),
            MenuItem("Proyecto con mas tareas", "Mayor cantidad de tareas pendientes."),
            MenuItem("Total de tareas pendientes", "Suma de los Deques de tareas."),
            MenuItem("Historial de un proyecto", "Todas las tareas procesadas."),
        )
        choice = self._context.menu.choose("GENERAR REPORTES", items, allow_back=True)
        if choice < 0:
            return

        service = self._context.planexa_service
        self._context.terminal.screen("REPORTE DE PLANEXA")
        if choice == 0:
            print(f"Total de proyectos registrados: {service.project_count}")
        elif choice in (1, 2, 5):
            self._report_project_tasks(choice)
            return
        elif choice == 3:
            project = service.project_with_most_tasks()
            if project is None:
                print("No hay proyectos registrados")
            else:
                self._context.project_table.render((project,))
        elif choice == 4:
            print(f"Total de tareas pendientes: {service.total_pending_tasks()}")
        print()
        self._context.prompt.wait()

    # O(n): Presenta tareas de un proyecto por ambos sentidos o su historial.
    def _report_project_tasks(self, choice: int) -> None:
        """Muestra las tareas sin modificar ningun extremo de los Deques."""

        code = self._context.prompt.required("Codigo del proyecto: ")
        try:
            service = self._context.planexa_service
            tasks = (
                service.iter_task_history(code)
                if choice == 5
                else service.iter_tasks(code, reverse=choice == 2)
            )
            # Iterar el generador ejecuta la busqueda y permite capturar sus errores.
            if not self._context.task_table.render(tasks):
                print("No hay tareas en este Deque")
        except PlanexaError as error:
            self._context.feedback.error(str(error))
            return
        print()
        self._context.prompt.wait()

    # O(n): Resume extremos, total de proyectos y tamaños de ambos tipos de Deque.
    def _status(self) -> None:
        """Presenta el estado estructural real exigido por el documento."""

        service = self._context.planexa_service
        self._context.terminal.screen("ESTADO DEL SISTEMA")
        first = service.first_project()
        last = service.last_project()
        most = service.project_with_most_tasks()
        print(f"Total de proyectos: {service.project_count}")
        print(f"Primer proyecto: {self._project_label(first)}")
        print(f"Ultimo proyecto: {self._project_label(last)}")
        print(f"Total de tareas activas: {service.total_pending_tasks()}")
        print(f"Proyecto con mas tareas: {self._project_label(most)}")
        print(f"Total de tareas procesadas: {service.total_processed_tasks()}")
        print()
        self._context.prompt.wait()

    # O(n): Confirma la salida y calcula el resumen final del sistema.
    def _exit(self) -> bool:
        """Cancela el cierre o imprime los tres conteos solicitados."""

        self._context.terminal.screen("SALIR DE PLANEXA")
        if not self._context.prompt.confirm("Deseas salir del sistema?"):
            return False
        self._context.terminal.screen("RESUMEN FINAL")
        service = self._context.planexa_service
        print(f"Total de proyectos: {service.project_count}")
        print(f"Total de tareas activas: {service.total_pending_tasks()}")
        print(f"Total de tareas procesadas: {service.total_processed_tasks()}")
        print()
        self._context.prompt.wait()
        return True

    # O(1): Formatea la referencia de un proyecto que puede no existir.
    def _project_label(self, project: Project | None) -> str:
        """Presenta codigo y nombre o un marcador informativo."""

        return f"{project.code} · {project.name}" if project is not None else "Ninguno"

    # O(1): Formatea una tarea opcional sin alterar la estructura.
    def _task_label(self, task: Task | None) -> str:
        """Presenta el ID y titulo de una tarea del extremo consultado."""

        return f"{task.id} · {task.title}" if task is not None else "Ninguna"

    # O(1): Muestra los detalles de un proyecto recibido desde la aplicacion.
    def _show_project_result(self, title: str, project: Project) -> None:
        """Centraliza la pantalla de resultados para crear y editar proyectos."""

        self._context.terminal.screen(title)
        self._context.project_table.render((project,))
        print()
        self._context.prompt.wait()

    # O(1): Muestra los detalles de una tarea devuelta por un caso de uso.
    def _show_task_result(self, title: str, task: Task) -> None:
        """Centraliza la confirmacion visual de una tarea afectada."""

        self._context.terminal.screen(title)
        self._context.task_table.render((task,))
        print()
        self._context.prompt.wait()
