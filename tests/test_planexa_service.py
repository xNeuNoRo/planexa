from datetime import date

import pytest

from planexa.application.planexa_service import PlanexaService
from planexa.domain.errors import PlanexaError


@pytest.fixture
def service() -> PlanexaService:
    return PlanexaService()


def create(service: PlanexaService, code: str = "P-001"):
    return service.create_project(
        code, f"Proyecto {code}", "Descripcion", "Angel", date(2026, 2, 6)
    )


def add(service: PlanexaService, id: str, code: str = "P-001"):
    return service.add_task(code, id, f"Tarea {id}", "Descripcion", "Alta", 2.5)


def test_empty_system_state(service: PlanexaService) -> None:
    assert service.project_count == 0
    assert service.first_project() is None
    assert service.last_project() is None
    assert service.project_with_most_tasks() is None
    assert service.total_pending_tasks() == 0
    assert service.total_processed_tasks() == 0
    assert tuple(service.iter_projects()) == ()
    assert tuple(service.iter_projects_reverse()) == ()


def test_create_and_find_are_sequential_and_normalized(service: PlanexaService) -> None:
    first = create(service, "P-001")
    second = create(service, "P-002")
    assert tuple(p.code for p in service.iter_projects()) == ("P-001", "P-002")
    assert tuple(p.code for p in service.iter_projects_reverse()) == ("P-002", "P-001")
    assert service.find_project(" P-002 ") is second
    assert service.first_project() is first
    assert service.last_project() is second
    assert service.find_project("missing") is None


def test_create_rejects_duplicate_code_without_modification(service: PlanexaService) -> None:
    create(service)
    with pytest.raises(PlanexaError, match="Ya existe"):
        create(service)
    assert service.project_count == 1


def test_edit_missing_or_invalid_does_not_mutate(service: PlanexaService) -> None:
    project = create(service)
    with pytest.raises(PlanexaError, match="no encontrado"):
        service.edit_project("missing", "new", "Desc", "Luis", date(2026, 2, 7))
    with pytest.raises(ValueError):
        service.edit_project(project.code, "Nuevo", " ", "Luis", date(2026, 2, 7))
    assert project.name == "Proyecto P-001"
    updated = service.edit_project(project.code, "Nuevo", "Desc", "Luis", date(2026, 2, 7))
    assert updated is project
    assert updated.code == "P-001"
    assert updated.owner == "Luis"


@pytest.mark.parametrize("removed", ["P-001", "P-002", "P-003"])
def test_delete_project_adjusts_extremes_and_inner_links(
    service: PlanexaService, removed: str
) -> None:
    for code in ("P-001", "P-002", "P-003"):
        create(service, code)
    assert service.delete_project(removed).code == removed
    expected = tuple(code for code in ("P-001", "P-002", "P-003") if code != removed)
    assert tuple(p.code for p in service.iter_projects()) == expected
    assert tuple(p.code for p in service.iter_projects_reverse()) == expected[::-1]
    assert service.project_count == 2


def test_delete_missing_project_raises_error(service: PlanexaService) -> None:
    with pytest.raises(PlanexaError, match="no encontrado"):
        service.delete_project("missing")


def test_reject_duplicate_task_in_same_project_and_allow_in_different_project(
    service: PlanexaService,
) -> None:
    first = create(service)
    second = create(service, "P-002")
    task = add(service, "T-001")
    with pytest.raises(PlanexaError, match="Ya existe una tarea"):
        add(service, "T-001")
    assert add(service, "T-001", "P-002").id == task.id
    assert first.pending_count == 1
    assert second.pending_count == 1


def test_reject_duplicate_task_even_after_processing(service: PlanexaService) -> None:
    create(service)
    add(service, "T-001")
    service.process_task_front("P-001")
    with pytest.raises(PlanexaError, match="Ya existe una tarea"):
        add(service, "T-001")


def test_process_both_ends_and_undo_preserve_identity(service: PlanexaService) -> None:
    project = create(service)
    first, middle, last = (add(service, id) for id in ("T-1", "T-2", "T-3"))

    assert service.process_task_front("P-001") is first
    assert service.process_task_rear("P-001") is last
    assert tuple(service.iter_tasks("P-001")) == (middle,)
    assert tuple(service.iter_task_history("P-001")) == (first, last)
    assert project.pending_count == 1
    assert project.processed_count == 2

    assert service.undo_last_task("P-001") is last
    assert tuple(service.iter_tasks("P-001")) == (last, middle)
    assert tuple(service.iter_tasks("P-001", reverse=True)) == (middle, last)
    assert tuple(service.iter_task_history("P-001")) == (first,)
    assert project.pending_tasks.get_front() is last
    assert project.task_history.get_rear() is first


def test_empty_task_and_history_operations_fail_without_mutation(service: PlanexaService) -> None:
    project = create(service)
    with pytest.raises(PlanexaError, match="No hay tareas pendientes"):
        service.process_task_front(project.code)
    with pytest.raises(PlanexaError, match="No hay tareas pendientes"):
        service.process_task_rear(project.code)
    with pytest.raises(PlanexaError, match="No hay tareas en el historial"):
        service.undo_last_task(project.code)
    assert project.pending_count == project.processed_count == 0


def test_deletion_blocked_with_pending_or_processed_history(service: PlanexaService) -> None:
    create(service)
    add(service, "T-1")
    with pytest.raises(PlanexaError, match="tareas o historial"):
        service.delete_project("P-001")
    service.process_task_rear("P-001")
    with pytest.raises(PlanexaError, match="tareas o historial"):
        service.delete_project("P-001")
    assert service.project_count == 1


def test_full_reports_and_status_match_current_deques(service: PlanexaService) -> None:
    p1 = create(service)
    p2 = create(service, "P-002")
    p3 = create(service, "P-003")
    add(service, "A")
    add(service, "B")
    add(service, "C", "P-002")
    assert service.project_with_most_tasks() is p1
    assert service.total_pending_tasks() == 3
    assert service.total_processed_tasks() == 0
    assert tuple(t.id for t in service.iter_tasks(p1.code)) == ("A", "B")
    assert tuple(t.id for t in service.iter_tasks(p1.code, reverse=True)) == ("B", "A")

    service.process_task_front("P-001")
    assert service.total_pending_tasks() == 2
    assert service.total_processed_tasks() == 1
    assert service.project_with_most_tasks() is p1  # Empate: primero en el Deque.
    assert tuple(t.id for t in service.iter_task_history("P-001")) == ("A",)
    assert p3.pending_count == 0
    assert p2.pending_count == 1


def test_nonexistent_project_is_rejected_in_task_operations(service: PlanexaService) -> None:
    with pytest.raises(PlanexaError, match="no encontrado"):
        add(service, "T-1")
    with pytest.raises(PlanexaError, match="no encontrado"):
        service.process_task_front("P-001")
    with pytest.raises(PlanexaError, match="no encontrado"):
        service.undo_last_task("P-001")
    with pytest.raises(PlanexaError, match="no encontrado"):
        tuple(service.iter_tasks("P-001"))
