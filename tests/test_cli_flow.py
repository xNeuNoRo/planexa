from collections.abc import Iterator
from datetime import date
from typing import cast

from planexa.application.planexa_service import PlanexaService
from planexa.ui.components.project_table import ProjectTable
from planexa.ui.components.task_table import TaskTable
from planexa.ui.screens.main import MainScreen
from planexa.ui.context import UIContext


class FakeMenu:
    """Menu preprogramado para probar el ciclo visual sin terminal interactiva."""

    # O(1): Construye un iterador de selecciones para las pantallas.
    def __init__(self, choices: tuple[int, ...]) -> None:
        """Guarda opciones de menus principales y secundarios."""
        self._choices = iter(choices)

    # O(1): Entrega la siguiente seleccion programada en el test.
    def choose(self, *args: object, **kwargs: object) -> int:
        """Simula la respuesta del usuario a un menu."""
        return next(self._choices)


class FakePrompt:
    """Lecturas de formularios controladas para pruebas de integracion."""

    # O(1): Inicializa secuencias predeterminadas de entradas de usuario.
    def __init__(self, values: tuple[str, ...], confirms: tuple[bool, ...] = (True, True)) -> None:
        """Prepara valores para required, iso_date, float y confirmaciones."""
        self._values: Iterator[str] = iter(values)
        self._confirms = iter(confirms)

    # O(1): Devuelve el siguiente valor textual de prueba.
    def required(self, label: str) -> str:
        """Simula un campo requerido."""
        return next(self._values)

    # O(1): Convierte el siguiente texto en fecha ISO valida.
    def iso_date(self, label: str) -> date:
        """Simula un campo de fecha validado."""
        return date.fromisoformat(next(self._values))

    # O(1): Convierte el siguiente texto en decimal positivo.
    def positive_float(self, label: str) -> float:
        """Simula el formulario numerico."""
        return float(next(self._values))

    # O(1): Simula una confirmacion del usuario.
    def confirm(self, label: str) -> bool:
        """Entrega la siguiente respuesta booleana."""
        return next(self._confirms)

    # O(1): Omite la espera interactiva durante las pruebas.
    def wait(self, label: str = "") -> None:
        """Continua con el flujo sin bloquear el test."""


class FakeTerminal:
    """Terminal sin ANSI para verificar la navegacion entre pantallas."""

    # O(1): Registra la apertura de una pantalla de interfaz.
    def screen(self, title: str, subtitle: str | None = None) -> None:
        """Simula una transicion de pantalla."""

    # O(1): Simula la limpieza de consola.
    def clear(self) -> None:
        """Omite efectos secundarios de terminal."""


class FakeFeedback:
    """Mensajes almacenados temporalmente por el propio test."""

    # O(1): Inicia registros de mensajes esperados.
    def __init__(self) -> None:
        """Prepara un registro temporal de errores."""
        self.errors: list[str] = []
        self.successes: list[str] = []

    # O(1): Registra el mensaje de error informado al usuario.
    def error(self, message: str) -> None:
        """Inspecciona mensajes de fallo esperados."""
        self.errors.append(message)

    # O(1): Registra el resultado positivo de una operacion.
    def success(self, message: str) -> None:
        """Inspecciona los mensajes de exito."""
        self.successes.append(message)


class FakeContext:
    """Composicion minima para ejercitar MainScreen en aislamiento."""

    # O(1): Ensambla pantallas reales con entradas deterministas.
    def __init__(self, choices: tuple[int, ...], values: tuple[str, ...]) -> None:
        """Configura estructuras reales y adaptadores simulados."""
        self.planexa_service = PlanexaService()
        self.terminal = FakeTerminal()
        self.menu = FakeMenu(choices)
        self.prompt = FakePrompt(values)
        self.feedback = FakeFeedback()
        self.project_table = ProjectTable()
        self.task_table = TaskTable()


def test_main_screen_happy_path_and_error_during_delete(capsys) -> None:
    context = FakeContext(
        # Crear, añadir x2, procesar ambos extremos, undo, buscar, editar, eliminar, estado, salir.
        (0, 4, 4, 5, 6, 7, 1, 2, 3, 10, 11),
        (
            "P-1", "Plan", "Descripcion", "Angel", "2026-02-06",
            "P-1", "T-1", "Primera", "Desc tarea 1", "Alta", "2.5",
            "P-1", "T-2", "Segunda", "Desc tarea 2", "Baja", "1",
            "P-1", "P-1", "P-1", "P-1", "P-1",
            "Plan actualizado", "Desc nueva", "Luis", "2026-03-01",
            "P-1",
        ),
    )
    MainScreen(cast("UIContext", context)).show()

    service = context.planexa_service
    project = service.get_project("P-1")
    assert project.name == "Plan actualizado"
    assert project.pending_count == 1
    assert project.processed_count == 1
    first_pending = project.pending_tasks.get_front()
    last_processed = project.task_history.get_rear()
    assert first_pending is not None and first_pending.id == "T-2"
    assert last_processed is not None and last_processed.id == "T-1"
    assert context.feedback.errors == ["No se puede eliminar un proyecto con tareas o historial"]
    output = capsys.readouterr().out
    assert "Total de proyectos: 1" in output
    assert "Total de tareas activas: 1" in output
    assert "Total de tareas procesadas: 1" in output


def test_all_six_reports_and_reverse_project_listing(capsys) -> None:
    context = FakeContext(
        (0, 4, 9, 0, 9, 1, 9, 2, 9, 3, 9, 4, 9, 5, 8, 1, 11),
        (
            "P-1", "Plan", "Desc", "Angel", "2026-02-06",
            "P-1", "T-1", "Primera", "Desc tarea", "Alta", "2.5",
            "P-1", "P-1", "P-1",
        ),
    )
    MainScreen(cast("UIContext", context)).show()

    output = capsys.readouterr().out
    assert "Total de proyectos registrados: 1" in output
    assert "Total de tareas pendientes: 1" in output
    assert "P-1 · Plan" in output
    assert "T-1 · Primera" in output
    assert "No hay tareas en este Deque" in output
