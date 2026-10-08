import math
from datetime import date

from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.shortcuts import print_formatted_text

from planexa.ui.tui.style import APP_STYLE


class Prompt:
    """Entradas de datos con validaciones reutilizables para la consola."""

    # O(1): Solicita texto hasta recibir un valor no vacio.
    def required(self, label: str) -> str:
        """Lee un campo obligatorio y elimina espacios externos."""

        while True:
            value = self._read(label).strip()
            if value:
                return value

            self._error("Este campo es obligatorio.")

    # O(1): Solicita un entero estrictamente mayor que cero.
    def positive_int(self, label: str) -> int:
        """Lee y valida una cantidad numerica positiva."""

        while True:
            raw = self._read(label).strip()

            try:
                value = int(raw)
            except ValueError:
                self._error("Introduce un numero entero valido.")
                continue

            if value > 0:
                return value

            self._error("El valor debe ser mayor que cero.")

    # O(1): Solicita un numero positivo y finito con posibilidad de decimales.
    def positive_float(self, label: str) -> float:
        """Valida la estimacion de horas antes de registrar una tarea."""

        while True:
            raw = self._read(label).strip()
            try:
                value = float(raw)
            except ValueError:
                self._error("Introduce un numero valido de horas.")
                continue

            if math.isfinite(value) and value > 0:
                return value

            self._error("La estimacion debe ser mayor que cero y finita.")

    # O(1): Lee y valida una fecha de calendario con formato ISO 8601.
    def iso_date(self, label: str) -> date:
        """Recibe fechas AAAA-MM-DD y rechaza fechas inexistentes."""

        while True:
            raw = self._read(label).strip()
            try:
                if len(raw) != 10 or raw[4] != "-" or raw[7] != "-":
                    raise ValueError
                return date.fromisoformat(raw)
            except ValueError:
                self._error("Fecha invalida. Usa AAAA-MM-DD.")

    # O(1): Solicita una confirmacion explicita de tipo S/N.
    def confirm(self, label: str) -> bool:
        """Retorna True para respuestas afirmativas y False para negativas."""

        while True:
            raw = self._read(f"{label} [s/n]: ").strip().casefold()

            if raw in ("s", "si", "sí"):
                return True

            if raw in ("n", "no"):
                return False

            self._error("Responde con 's' o 'n'.")

    # O(1): Pausa la interfaz hasta que el usuario presione Enter.
    def wait(self, label: str = "Presiona Enter para continuar...") -> None:
        """Mantiene visible el resultado actual antes de regresar al menu."""

        self._read(label)

    # O(1): Centraliza la lectura de texto mediante prompt_toolkit.
    def _read(self, label: str) -> str:
        """Lee una linea usando el mismo estilo visual que el resto de la interfaz."""

        return prompt(FormattedText([("class:description", label)]), style=APP_STYLE)

    # O(1): Muestra un error de validacion sin interrumpir la ejecucion.
    def _error(self, message: str) -> None:
        """Renderiza mensajes de entrada invalida con estilo consistente."""

        print_formatted_text(FormattedText([("class:error", message)]), style=APP_STYLE)
