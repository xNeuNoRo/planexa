from planexa.ui.tui.menu import MenuState


def test_menu_state_wraps_navigation() -> None:
    state = MenuState(item_count=6, selected=0)

    state.move(-1)
    assert state.selected == 5

    state.move(1)
    assert state.selected == 0


def test_menu_state_normalizes_selected_index() -> None:
    state = MenuState(item_count=6, selected=99)

    state.normalize()

    assert state.selected == 5


def test_menu_state_returns_active_page_bounds() -> None:
    state = MenuState(item_count=12, selected=8)

    assert state.page_bounds(5) == (5, 10)
