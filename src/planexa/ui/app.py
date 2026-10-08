from planexa.ui.context import UIContext
from planexa.ui.screens.main import MainScreen
from planexa.ui.theme import Theme


class ConsoleApplication:
    """Punto de entrada de la UI sin reglas de negocio."""

    # O(1): Compone una unica pantalla principal con su contexto.
    def __init__(self, context: UIContext) -> None:
        """Prepara las dependencias compartidas por el flujo visual."""

        self._context = context
        self._main_screen = MainScreen(context)

    # O(n): Ejecuta el menu y mantiene controlado el cierre del terminal.
    def run(self) -> None:
        """Inicia Planexa y garantiza una salida ordenada."""

        try:
            self._main_screen.show()
        except (EOFError, KeyboardInterrupt):
            print()
        finally:
            self._context.terminal.clear()
            print(f"{Theme.CYAN}{Theme.BOLD}Planexa finalizado.{Theme.RESET}\n")
