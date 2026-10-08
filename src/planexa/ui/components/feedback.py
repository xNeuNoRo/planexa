from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.shortcuts import print_formatted_text

from planexa.ui.components.prompt import Prompt
from planexa.ui.terminal import Terminal
from planexa.ui.tui.style import APP_STYLE


class Feedback:
    """Mensajes de resultado consistentes para operaciones del sistema."""

    # O(1): Inicializa el componente con terminal y entrada compartidos.
    def __init__(self, terminal: Terminal, prompt: Prompt) -> None:
        """Guarda las dependencias necesarias para mostrar mensajes."""

        self._terminal = terminal
        self._prompt = prompt

    # O(1): Muestra una confirmacion visual de operacion exitosa.
    def success(self, message: str) -> None:
        """Muestra un mensaje exitoso y espera confirmacion del usuario."""

        self._message("OPERACION COMPLETADA", message, "class:success")

    # O(1): Muestra un error esperado sin finalizar la aplicacion.
    def error(self, message: str) -> None:
        """Muestra un mensaje de error y permite volver al menu."""

        self._message("NO SE PUDO COMPLETAR", message, "class:error")

    # O(1): Renderiza un mensaje con formato comun y espera Enter.
    def _message(self, title: str, message: str, style_class: str) -> None:
        """Centraliza el layout usado para mensajes breves."""

        self._terminal.screen(title)
        print_formatted_text(FormattedText([(style_class, message)]), style=APP_STYLE)
        print()
        self._prompt.wait()
