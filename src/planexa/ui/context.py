from dataclasses import dataclass

from planexa.application.planexa_service import PlanexaService
from planexa.ui.components.feedback import Feedback
from planexa.ui.components.menu import InteractiveMenu
from planexa.ui.components.project_table import ProjectTable
from planexa.ui.components.prompt import Prompt
from planexa.ui.components.task_table import TaskTable
from planexa.ui.terminal import Terminal


@dataclass(slots=True, frozen=True)
class UIContext:
    """Dependencias compartidas por las pantallas de la interfaz."""

    planexa_service: PlanexaService
    terminal: Terminal
    menu: InteractiveMenu
    prompt: Prompt
    feedback: Feedback
    project_table: ProjectTable
    task_table: TaskTable
