from datetime import date
from typing import cast

import pytest

from planexa.domain.project import Project
from planexa.domain.task import Task


@pytest.mark.parametrize("code,name,description,owner", [
    (" ", "Nombre", "Desc", "Angel"),
    ("P1", " ", "Desc", "Angel"),
    ("P1", "Nombre", " ", "Angel"),
    ("P1", "Nombre", "Desc", " "),
])
def test_project_rejects_empty_fields(code: str, name: str, description: str, owner: str) -> None:
    with pytest.raises(ValueError):
        Project(code, name, description, owner, date(2026, 2, 6))


def test_project_edit_is_atomic_and_preserves_code() -> None:
    project = Project(" P-1 ", " Uno ", " Desc ", " Angel ", date(2026, 2, 6))
    assert project.code == "P-1"

    with pytest.raises(ValueError):
        project.update("Otro", " ", "Luis", date(2026, 3, 1))

    assert project.name == "Uno"
    assert project.description == "Desc"
    assert project.owner == "Angel"
    assert project.start_date == date(2026, 2, 6)

    project.update("Nuevo", "Otra desc", "Luis", date(2026, 3, 1))
    assert project.code == "P-1"
    assert project.name == "Nuevo"
    assert project.start_date == date(2026, 3, 1)


@pytest.mark.parametrize("id,title,description,priority", [
    (" ", "Titulo", "Desc", "Alta"),
    ("T1", " ", "Desc", "Alta"),
    ("T1", "Titulo", " ", "Alta"),
    ("T1", "Titulo", "Desc", " "),
])
def test_task_rejects_empty_fields(id: str, title: str, description: str, priority: str) -> None:
    with pytest.raises(ValueError):
        Task(id, title, description, priority, 3.5)


@pytest.mark.parametrize("hours", [0, -1, float("inf"), float("nan"), True, "2"])
def test_task_rejects_invalid_estimates(hours: object) -> None:
    with pytest.raises(ValueError):
        Task("T1", "Titulo", "Desc", "Alta", cast("float", hours))


def test_task_accepts_positive_decimal_and_normalizes_fields() -> None:
    task = Task(" T1 ", " Titulo ", " Desc ", " Alta ", 2.5)
    assert task.id == "T1"
    assert task.title == "Titulo"
    assert task.description == "Desc"
    assert task.priority == "Alta"
    assert task.estimated_hours == 2.5
