from planexa.application.planexa_service import PlanexaService
from planexa.ui.app import ConsoleApplication
from planexa.ui.components.feedback import Feedback
from planexa.ui.components.menu import InteractiveMenu
from planexa.ui.components.project_table import ProjectTable
from planexa.ui.components.prompt import Prompt
from planexa.ui.components.task_table import TaskTable
from planexa.ui.context import UIContext
from planexa.ui.terminal import Terminal


# O(1): Compone dominio, servicio e interfaz e inicia Planexa.
def main() -> None:
    """Entry point declarado como script en pyproject.toml."""

    service = PlanexaService()
    terminal = Terminal()
    prompt = Prompt()

    context = UIContext(
        planexa_service=service,
        terminal=terminal,
        menu=InteractiveMenu(terminal),
        prompt=prompt,
        feedback=Feedback(terminal, prompt),
        project_table=ProjectTable(),
        task_table=TaskTable(),
    )
    ConsoleApplication(context).run()


if __name__ == "__main__":
    main()
