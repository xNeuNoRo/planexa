import os
import shutil
import sys

from planexa.ui.theme import Theme


class Terminal:
    """Abstraccion pequena para renderizar pantallas de consola."""

    # O(1): Habilita soporte ANSI en terminales modernas de Windows.
    def __init__(self) -> None:
        """Prepara el terminal para los codigos ANSI usados por la interfaz."""

        if os.name == "nt":
            os.system("")

    # O(1): Limpia la pantalla, el scrollback visible y reposiciona el cursor.
    def clear(self) -> None:
        """Descarta el contenido anterior para comenzar una pantalla limpia."""

        sys.stdout.write("\033[2J\033[3J\033[H")
        sys.stdout.flush()

    # O(1): Inicia una pantalla limpia y muestra su encabezado comun.
    def screen(self, title: str, subtitle: str | None = None) -> None:
        """Centraliza el ciclo de limpieza y encabezado de cada vista."""

        self.clear()
        self.header(title, subtitle)

    # O(1): Retorna un ancho seguro para renderizar tablas y separadores.
    def width(self) -> int:
        """Calcula un ancho limitado para mantener la interfaz legible."""

        return max(80, min(shutil.get_terminal_size((100, 24)).columns, 120))

    # O(1): Imprime el encabezado comun de las pantallas de Planexa.
    def header(self, title: str, subtitle: str | None = None) -> None:
        """Muestra el nombre de la aplicacion y el titulo de la pantalla."""

        width = self.width()
        print(f"{Theme.CYAN}{Theme.BOLD}PLANEXA{Theme.RESET}")
        print(f"{Theme.GRAY}{'─' * width}{Theme.RESET}")
        print(f"{Theme.BOLD}{title}{Theme.RESET}")
        if subtitle:
            print(f"{Theme.DIM}{subtitle}{Theme.RESET}")
        print(f"{Theme.GRAY}{'─' * width}{Theme.RESET}")
