import sys
from dataclasses import dataclass
from typing import Any

from prompt_toolkit.application import Application, get_app
from prompt_toolkit.formatted_text import StyleAndTextTuples
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout, Window
from prompt_toolkit.layout.controls import FormattedTextControl

from planexa.ui.terminal import Terminal
from planexa.ui.tui.branding import COMPACT_LOGO, LOGO_LINES
from planexa.ui.tui.style import APP_STYLE


@dataclass(slots=True, frozen=True)
class MenuItem:
    """Opcion visual e inmutable de un menu interactivo."""

    label: str
    description: str = ""


@dataclass(slots=True)
class MenuState:
    """Estado navegable del menu separado del renderer de prompt_toolkit."""

    item_count: int
    selected: int = 0

    # O(1): Mantiene la seleccion dentro del rango valido de opciones.
    def normalize(self) -> None:
        """Normaliza el indice seleccionado."""

        if self.item_count <= 0:
            self.selected = 0
            return

        self.selected = max(0, min(self.selected, self.item_count - 1))

    # O(1): Mueve la seleccion de forma circular una cantidad de posiciones.
    def move(self, delta: int) -> None:
        """Mueve la seleccion y permite envolver el inicio y el final."""

        if self.item_count > 0:
            self.selected = (self.selected + delta) % self.item_count

    # O(1): Calcula el segmento visible que contiene la opcion seleccionada.
    def page_bounds(self, page_size: int) -> tuple[int, int]:
        """Retorna los limites de la pagina activa."""

        if self.item_count <= 0:
            return (0, 0)

        page_size = max(1, page_size)
        start = (self.selected // page_size) * page_size
        return start, min(start + page_size, self.item_count)


class InteractiveMenu:
    """Menu interactivo portable respaldado por prompt_toolkit."""

    # O(1): Guarda el terminal compartido para controlar el ciclo de cada pantalla.
    def __init__(self, terminal: Terminal) -> None:
        """Recibe la abstraccion usada para limpiar la consola entre vistas."""

        self._terminal = terminal

    # O(n): Renderiza las opciones disponibles y procesa la navegacion del usuario.
    def choose(
        self,
        title: str,
        items: tuple[MenuItem, ...],
        *,
        subtitle: str | None = None,
        allow_back: bool = True,
        selected: int = 0,
    ) -> int:
        """Muestra un menu navegable con flechas, W/S y Enter."""

        if not items:
            return -1

        if not sys.stdin.isatty() or not sys.stdout.isatty():
            return self._choose_line_mode(title, items, subtitle, allow_back)

        self._terminal.clear()
        state = MenuState(len(items), selected)
        state.normalize()
        bindings = self._bindings(state, allow_back)

        control = FormattedTextControl(
            text=lambda: self._render_fragments(title, items, state, subtitle, allow_back),
            focusable=True,
            show_cursor=False,
        )
        body = Window(content=control, wrap_lines=False, always_hide_cursor=True)

        application: Application[int] = Application(
            layout=Layout(body, focused_element=body),
            key_bindings=bindings,
            style=APP_STYLE,
            full_screen=True,
            mouse_support=False,
            erase_when_done=True,
            terminal_size_polling_interval=0.25,
        )
        return application.run()

    # O(1): Configura los atajos de teclado utilizados para navegar por el menu.
    def _bindings(self, state: MenuState, allow_back: bool) -> KeyBindings:
        """Define bindings portables sin leer secuencias ANSI manualmente."""

        bindings = KeyBindings()

        @bindings.add("up")
        @bindings.add("w")
        # O(1): Mueve la seleccion una posicion hacia arriba.
        def _up(event: Any) -> None:
            """Procesa la navegacion hacia arriba."""

            state.move(-1)
            event.app.invalidate()

        @bindings.add("down")
        @bindings.add("s")
        # O(1): Mueve la seleccion una posicion hacia abajo.
        def _down(event: Any) -> None:
            """Procesa la navegacion hacia abajo."""

            state.move(1)
            event.app.invalidate()

        @bindings.add("home")
        # O(1): Selecciona directamente la primera opcion.
        def _home(event: Any) -> None:
            """Mueve la seleccion al inicio."""

            state.selected = 0
            event.app.invalidate()

        @bindings.add("end")
        # O(1): Selecciona directamente la ultima opcion.
        def _end(event: Any) -> None:
            """Mueve la seleccion al final."""

            state.selected = max(0, state.item_count - 1)
            event.app.invalidate()

        @bindings.add("enter")
        # O(1): Confirma la opcion actualmente seleccionada.
        def _accept(event: Any) -> None:
            """Finaliza el menu con la seleccion actual."""

            event.app.exit(result=state.selected)

        @bindings.add("c-c")
        # O(1): Gestiona Ctrl+C sin dejar el terminal en un estado inconsistente.
        def _ctrl_c(event: Any) -> None:
            """Cancela el menu cuando sea posible."""

            event.app.exit(result=-1 if allow_back else state.selected)

        if allow_back:

            @bindings.add("escape")
            @bindings.add("q")
            # O(1): Regresa a la pantalla anterior usando Escape o Q.
            def _back(event: Any) -> None:
                """Finaliza el menu indicando que el usuario desea volver."""

                event.app.exit(result=-1)

        return bindings

    # O(n): Construye los fragmentos visuales de la pagina activa del menu.
    def _render_fragments(
        self,
        title: str,
        items: tuple[MenuItem, ...],
        state: MenuState,
        subtitle: str | None,
        allow_back: bool,
    ) -> StyleAndTextTuples:
        """Compone logo, titulo, opciones, descripcion y ayudas de teclado."""

        size = get_app().output.get_size()
        columns = max(30, size.columns)
        rows = max(12, size.rows)
        show_large_logo = columns >= 64 and rows >= 22
        logo_height = len(LOGO_LINES) if show_large_logo else 1
        page_size = max(3, min(10, rows - logo_height - 10))
        start, end = state.page_bounds(page_size)
        content_width = max(24, min(76, columns - 4))

        fragments: StyleAndTextTuples = []
        if show_large_logo:
            for line in LOGO_LINES:
                fragments.append(("class:logo", self._clip(line, content_width)))
                fragments.append(("", "\n"))
        else:
            fragments.extend((("class:logo", COMPACT_LOGO), ("", "\n")))

        separator = "─" * content_width
        fragments.extend(
            (
                ("class:separator", separator),
                ("", "\n"),
                ("class:title", title),
                ("", "\n"),
            )
        )

        if subtitle:
            fragments.extend((("class:subtitle", self._clip(subtitle, content_width)), ("", "\n")))

        fragments.extend((("class:separator", separator), ("", "\n\n")))
        label_width = max(12, content_width - 4)

        for index in range(start, end):
            marker = ">" if index == state.selected else " "
            label = self._clip(items[index].label, label_width)
            line = f" {marker} {label}"
            style = "class:item.selected" if index == state.selected else "class:item"
            fragments.extend(((style, line), ("", "\n")))

        if len(items) > page_size:
            current_page = (state.selected // page_size) + 1
            total_pages = (len(items) + page_size - 1) // page_size
            fragments.extend(
                (("", "\n"), ("class:pager", f"Pagina {current_page}/{total_pages}"), ("", "\n"))
            )

        description = items[state.selected].description
        if description:
            fragments.extend(
                (
                    ("", "\n"),
                    ("class:description", self._clip(description, content_width)),
                    ("", "\n"),
                )
            )

        back = " | Esc/Q volver" if allow_back else ""
        fragments.extend(
            (
                ("", "\n"),
                ("class:hint", f"Flechas o W/S navegar | Enter seleccionar{back}"),
            )
        )
        return fragments

    # O(n): Ofrece un menu numerico cuando la terminal no permite modo interactivo.
    def _choose_line_mode(
        self,
        title: str,
        items: tuple[MenuItem, ...],
        subtitle: str | None,
        allow_back: bool,
    ) -> int:
        """Mantiene el programa utilizable en terminales sin TTY real."""

        while True:
            self._terminal.screen(title, subtitle)

            for index, item in enumerate(items, start=1):
                print(f"  {index}. {item.label}")

            if allow_back:
                print("  0. Volver")

            raw = input("Selecciona una opcion: ").strip()
            if allow_back and raw == "0":
                return -1

            try:
                choice = int(raw) - 1
            except ValueError:
                continue

            if 0 <= choice < len(items):
                return choice

    # O(n): Recorta un texto al ancho disponible sin modificar su contenido original.
    def _clip(self, text: str, width: int) -> str:
        """Evita que textos largos rompan el layout del menu."""

        if len(text) <= width:
            return text

        if width <= 3:
            return text[:width]

        return f"{text[: width - 3]}..."
