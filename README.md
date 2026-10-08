# Planexa

Planexa es una aplicación de consola desarrollada en Python para gestionar proyectos empresariales y sus tareas utilizando exclusivamente Deques implementados manualmente mediante nodos doblemente enlazados.

El sistema mantiene un Deque principal de proyectos. Cada proyecto contiene dos Deques adicionales: uno para las tareas pendientes y otro para el historial de tareas procesadas. Las estructuras mantienen sus propios extremos y enlaces; no se utilizan listas ni diccionarios como almacenamiento principal.

## Autor

Angel Gonzalez
Matrícula: 2025-1122

## Objetivo

Desarrollar una aplicación que permita:

- Registrar, buscar, editar, eliminar y listar proyectos.
- Añadir tareas pendientes dentro de un proyecto.
- Procesar tareas por el frente o por el final de su Deque.
- Deshacer el último procesamiento mediante el historial.
- Generar reportes sobre proyectos, tareas pendientes y tareas procesadas.
- Consultar el estado real de los Deques y cerrar el sistema mostrando un resumen.

## Estructuras de datos utilizadas

### Deque doblemente enlazado

`LinkedDeque[T]` utiliza nodos `DoublyNode[T]` con enlaces `prev` y `next`. Mantiene las referencias `_front`, `_rear` y el contador `_size`.

Operaciones obligatorias:

| Operación | Complejidad | Funcionamiento |
| --- | --- | --- |
| `insert_front` | O(1) | Inserta antes del primer nodo. |
| `insert_rear` | O(1) | Inserta después del último nodo. |
| `delete_front` | O(1) | Desvincula el primer nodo. |
| `delete_rear` | O(1) | Desvincula el último nodo. |
| `get_front` | O(1) | Consulta el primer elemento sin extraerlo. |
| `get_rear` | O(1) | Consulta el último elemento sin extraerlo. |
| `__iter__` | O(n) | Recorre desde front mediante `next`. |
| `__reversed__` | O(n) | Recorre desde rear mediante `prev`. |
| `find` | O(n) | Busca mediante recorrido secuencial. |
| `remove_first` | O(n) | Desvincula el primer nodo coincidente. |

Las operaciones sobre los extremos funcionan en tiempo constante. La búsqueda y eliminación arbitraria requieren recorrido O(n), porque la estructura no mantiene diccionarios o índices auxiliares. Las referencias se ajustan directamente, tanto al eliminar el primer o último elemento como al eliminar un nodo intermedio.

### Deque principal de proyectos

`PlanexaService` administra un único `LinkedDeque[Project]`:

- Los nuevos proyectos se insertan en `rear`.
- Un código duplicado se detecta recorriendo los proyectos almacenados.
- La búsqueda utiliza recorrido secuencial del Deque.
- La edición no acepta modificar el código original.
- La eliminación solo se permite cuando no existen tareas pendientes ni historial.
- El listado admite recorridos de `front` a `rear` y de `rear` a `front`.

### Deques internos de cada proyecto

Cada proyecto tiene:

- `pending_tasks: LinkedDeque[Task]`: tareas pendientes, insertadas inicialmente en `rear`.
- `task_history: LinkedDeque[Task]`: tareas procesadas en orden de procesamiento.

El procesamiento por el frente ejecuta `delete_front` sobre pendientes y `insert_rear` en el historial. El procesamiento por el final ejecuta `delete_rear` sobre pendientes y `insert_rear` en el historial. El proceso de deshacer utiliza `delete_rear` del historial e `insert_front` en pendientes.

Se transfiere la misma entidad `Task` entre estructuras, sin copiarla ni mantenerla simultáneamente en ambas.

## Reglas de integridad

- Los códigos de proyectos se ingresan manualmente, son obligatorios y únicos a nivel del sistema.
- Los IDs de tareas se ingresan manualmente y son únicos dentro de cada proyecto.
- Para proteger esa unicidad, el ID se valida tanto en pendientes como en historial, incluso después del procesamiento.
- El mismo ID de tarea puede existir en proyectos distintos.
- Los campos de texto no aceptan valores vacíos; se eliminan los espacios externos.
- La fecha de inicio se introduce en formato `AAAA-MM-DD` y se almacena como `datetime.date`.
- La prioridad se recibe como texto obligatorio porque la asignación no define un catálogo de prioridades.
- La estimación admite horas positivas con decimales; se rechazan valores negativos, cero, infinitos y NaN.
- Un proyecto solo puede eliminarse si sus dos Deques internos están vacíos.
- No se puede procesar una tarea cuando el Deque de pendientes está vacío.
- No se puede deshacer cuando no existen tareas procesadas.
- Los códigos y los IDs se comparan exactamente después de normalizar espacios externos. No se aplica conversión automática a mayúsculas o minúsculas porque el documento no la exige.

## Menú principal

El sistema ofrece exactamente las doce opciones de la asignación:

1. Crear proyecto.
2. Buscar proyecto.
3. Editar proyecto.
4. Eliminar proyecto.
5. Añadir tareas a un proyecto.
6. Procesar tarea por el frente.
7. Procesar tarea por el final.
8. Deshacer última tarea procesada.
9. Listar proyectos.
10. Generar reportes.
11. Ver estado del sistema.
12. Salir.

Los listados y reportes ofrecen submenús cuando se requiere seleccionar un recorrido. El menú utiliza `prompt-toolkit` para navegar con flechas o W/S y confirmar con Enter, junto con un modo numérico de respaldo para terminales no interactivas. Los formularios, tablas y mensajes de resultado mantienen el estilo modular utilizado en QuickDispatch.

## Reportes

Los seis reportes implementados son:

1. Total de proyectos registrados.
2. Tareas pendientes de un proyecto, de `front` a `rear`.
3. Tareas pendientes de un proyecto, de `rear` a `front`.
4. Proyecto con más tareas pendientes.
5. Total de tareas pendientes de todos los proyectos.
6. Historial de tareas procesadas de un proyecto.

En el empate por cantidad de tareas se conserva el primer proyecto del recorrido. Si todos están vacíos, se mostrará el primer proyecto como máximo con cero tareas; si no hay proyectos, se mostrará un mensaje informativo.

El apartado **Ver estado del sistema** muestra total de proyectos, primer proyecto, último proyecto, total de tareas activas, proyecto con más tareas y total de tareas procesadas.

**Nota sobre el reporte E:** se contabilizan las tareas pendientes en los Deques de tareas; los elementos procesados se cuentan por separado en sus respectivos historiales, conforme al apartado de estado del sistema.

## Requisitos

Python 3.14 o superior, de acuerdo con la configuración de los proyectos anteriores.

Dependencia de ejecución:

- `prompt-toolkit`

Herramientas de desarrollo:

- `uv`
- `pytest`
- `ruff`
- `ty`

## Instalación y ejecución

Desde la raíz del proyecto:

```bash
uv sync
uv run planexa
```

## Pruebas

Las pruebas automatizadas cubren enlaces bidireccionales, tamaños y extremos, operaciones del Deque, validaciones de entidades, ciclos de procesamiento y undo, bloqueos de eliminación, recorridos e informes.

```bash
uv run pytest
```

## Calidad de código

```bash
uv run ruff check .
uv run ruff format --check .
uv run ty check
```

Para aplicar el formato de manera automática:

```bash
uv run ruff format .
```

Los métodos contienen comentarios en español con complejidad Big-O encima de su definición, además de docstrings descriptivos. Ningún caso de uso realiza búsquedas cuadráticas; las operaciones combinadas recorren como máximo cada Deque afectado una vez, por lo que su costo es O(n) respecto de los elementos involucrados.

## Organización del proyecto

```text
planexa/
├── src/planexa/
│   ├── application/
│   │   └── planexa_service.py
│   ├── domain/
│   │   ├── errors.py
│   │   ├── project.py
│   │   └── task.py
│   ├── structures/
│   │   ├── linked_deque.py
│   │   └── node.py
│   ├── ui/
│   │   ├── components/
│   │   ├── screens/
│   │   ├── tui/
│   │   ├── app.py
│   │   ├── context.py
│   │   ├── terminal.py
│   │   └── theme.py
│   └── main.py
├── tests/
├── .gitignore
├── .python-version
├── pyproject.toml
├── uv.lock
└── README.md
```

### domain

Contiene `Project`, `Task` y las validaciones de integridad que no deben depender de la interfaz.

### structures

Implementa el nodo doblemente enlazado y el Deque genérico; no almacena entidades de negocio en estructuras nativas.

### application

Contiene `PlanexaService`, que coordina los tres tipos de Deques y ejecuta los casos de uso.

### ui

Contiene TUI, formularios, tablas, componentes reutilizables y pantalla principal. No modifica enlaces internos ni resuelve reglas de negocio.

### tests

Contiene pruebas de las estructuras, dominio, aplicación y estado del menú.

## Consideraciones

Planexa conserva los datos exclusivamente durante la ejecución. No necesita una capa de infraestructura de persistencia ni puertos de acceso externos, por lo que utiliza composición manual de dependencias en `main.py`.

El proyecto mantiene el almacenamiento principal únicamente en Deques reales. Las tuplas del menú y las secuencias empleadas para presentar resultados no se utilizan como repositorios de datos del dominio.
