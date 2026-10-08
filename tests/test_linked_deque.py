import pytest

from planexa.structures.linked_deque import LinkedDeque


@pytest.mark.parametrize("operation", ["delete_front", "delete_rear"])
def test_empty_deque_exposes_no_extremes(operation: str) -> None:
    deque = LinkedDeque[int]()

    assert deque.is_empty()
    assert len(deque) == 0
    assert deque.get_front() is None
    assert deque.get_rear() is None
    assert getattr(deque, operation)() is None
    assert tuple(deque) == ()
    assert tuple(reversed(deque)) == ()


def test_insert_and_traverse_both_directions() -> None:
    deque = LinkedDeque[int]()
    deque.insert_rear(2)
    deque.insert_front(1)
    deque.insert_rear(3)
    deque.insert_front(0)

    assert len(deque) == 4
    assert deque.get_front() == 0
    assert deque.get_rear() == 3
    assert tuple(deque) == (0, 1, 2, 3)
    assert tuple(reversed(deque)) == (3, 2, 1, 0)
    assert deque._front is not None
    assert deque._rear is not None
    assert deque._front.prev is None
    assert deque._rear.next is None
    assert deque._front.next is not None
    assert deque._front.next.prev is deque._front


def test_delete_from_both_ends_and_reuse() -> None:
    deque = LinkedDeque[str]()
    deque.insert_rear("a")
    deque.insert_rear("b")
    deque.insert_rear("c")

    assert deque.delete_front() == "a"
    assert deque.delete_rear() == "c"
    assert deque.get_front() == deque.get_rear() == "b"
    assert deque.delete_rear() == "b"
    assert deque.is_empty()
    assert deque._front is None
    assert deque._rear is None

    deque.insert_front("fresh")
    assert deque.delete_front() == "fresh"
    assert deque.is_empty()


@pytest.mark.parametrize("index", [0, 1, 2, 3, 4])
def test_remove_first_handles_any_position(index: int) -> None:
    deque = LinkedDeque[int]()
    for number in range(5):
        deque.insert_rear(number)

    assert deque.remove_first(lambda value: value == index) == index
    expected = tuple(value for value in range(5) if value != index)
    assert tuple(deque) == expected
    assert tuple(reversed(deque)) == tuple(reversed(expected))
    assert len(deque) == 4
    assert deque._front is not None
    assert deque._front.prev is None
    assert deque._rear is not None
    assert deque._rear.next is None


def test_remove_first_missing_does_not_change_links() -> None:
    deque = LinkedDeque[int]()
    deque.insert_front(7)

    assert deque.remove_first(lambda value: value == 8) is None
    assert deque.find(lambda value: value == 7) == 7
    assert deque.any(lambda value: value == 7)
    assert not deque.any(lambda value: value == 8)
    assert tuple(deque) == (7,)


def test_remove_only_node_restores_empty_invariants() -> None:
    deque = LinkedDeque[str]()
    deque.insert_front("only")

    assert deque.remove_first(lambda value: value == "only") == "only"
    assert deque._front is None
    assert deque._rear is None
    assert len(deque) == 0


def test_many_interleaved_operations_keep_bidirectional_invariants() -> None:
    deque = LinkedDeque[int]()
    for value in range(200):
        if value % 2:
            deque.insert_front(value)
        else:
            deque.insert_rear(value)

    for value in range(40):
        if value % 2:
            assert deque.delete_front() is not None
        else:
            assert deque.delete_rear() is not None

    forward = tuple(deque)
    assert tuple(reversed(deque)) == tuple(reversed(forward))
    assert len(forward) == len(deque) == 160

    previous = None
    current = deque._front
    visited = 0
    while current is not None:
        assert current.prev is previous
        previous = current
        current = current.next
        visited += 1
    assert previous is deque._rear
    assert visited == len(deque)
