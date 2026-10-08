from collections.abc import Callable, Iterator

from planexa.structures.node import DoublyNode


class LinkedDeque[T]:
    """Deque generico implementado mediante nodos doblemente enlazados."""

    _front: DoublyNode[T] | None
    _rear: DoublyNode[T] | None
    _size: int

    # O(1): Inicializa un Deque vacio sin estructuras auxiliares.
    def __init__(self) -> None:
        """Establece los extremos vacios y el contador de elementos."""

        self._front = None
        self._rear = None
        self._size = 0

    # O(1): Retorna la cantidad de nodos almacenados.
    def __len__(self) -> int:
        """Retorna el tamaño actual sin recorrer la estructura."""

        return self._size

    # O(1): Determina si ambos extremos corresponden a un Deque vacio.
    def is_empty(self) -> bool:
        """Indica si la estructura carece de elementos."""

        return self._size == 0

    # O(1): Inserta un nuevo nodo antes del frente actual.
    def insert_front(self, value: T) -> None:
        """Agrega un elemento al comienzo, actualizando prev y front."""

        node = DoublyNode(value=value, next=self._front)
        if self._front is None:
            self._rear = node
        else:
            self._front.prev = node

        self._front = node
        self._size += 1

    # O(1): Inserta un nuevo nodo despues del extremo final.
    def insert_rear(self, value: T) -> None:
        """Agrega un elemento al final, actualizando next y rear."""

        node = DoublyNode(value=value, prev=self._rear)
        if self._rear is None:
            self._front = node
        else:
            self._rear.next = node

        self._rear = node
        self._size += 1

    # O(1): Retira y retorna el nodo ubicado en el frente del Deque.
    def delete_front(self) -> T | None:
        """Elimina el primer elemento o retorna None si esta vacio."""

        node = self._front
        if node is None:
            return None

        self._front = node.next
        if self._front is None:
            self._rear = None
        else:
            self._front.prev = None

        node.next = None
        self._size -= 1
        return node.value

    # O(1): Retira y retorna el nodo ubicado al final del Deque.
    def delete_rear(self) -> T | None:
        """Elimina el ultimo elemento o retorna None si esta vacio."""

        node = self._rear
        if node is None:
            return None

        self._rear = node.prev
        if self._rear is None:
            self._front = None
        else:
            self._rear.next = None

        node.prev = None
        self._size -= 1
        return node.value

    # O(1): Consulta el valor del nodo frontal sin extraerlo.
    def get_front(self) -> T | None:
        """Retorna el primer elemento o None cuando no hay nodos."""

        return self._front.value if self._front is not None else None

    # O(1): Consulta el valor del nodo final sin modificar el Deque.
    def get_rear(self) -> T | None:
        """Retorna el ultimo elemento o None cuando no hay nodos."""

        return self._rear.value if self._rear is not None else None

    # O(n): Recorre los nodos en el orden natural desde front hasta rear.
    def __iter__(self) -> Iterator[T]:
        """Produce cada elemento leyendo directamente los enlaces next."""

        current = self._front
        while current is not None:
            yield current.value
            current = current.next

    # O(n): Recorre los nodos desde rear hasta front sin construir una lista.
    def __reversed__(self) -> Iterator[T]:
        """Produce los elementos del Deque mediante los enlaces prev."""

        current = self._rear
        while current is not None:
            yield current.value
            current = current.prev

    # O(n): Busca el primer valor que satisfaga un criterio determinado.
    def find(self, predicate: Callable[[T], bool]) -> T | None:
        """Localiza un elemento por recorrido secuencial del Deque real."""

        for value in self:
            if predicate(value):
                return value
        return None

    # O(n): Comprueba si algun elemento cumple una condicion.
    def any(self, predicate: Callable[[T], bool]) -> bool:
        """Busca coincidencias sin materializar arreglos ni diccionarios."""

        return self.find(predicate) is not None

    # O(n): Retira el primer nodo coincidente y reajusta sus enlaces vecinos.
    def remove_first(self, predicate: Callable[[T], bool]) -> T | None:
        """Elimina un nodo arbitrario conservando front, rear y tamaño."""

        current = self._front
        while current is not None:
            if predicate(current.value):
                if current.prev is None:
                    self._front = current.next
                else:
                    current.prev.next = current.next

                if current.next is None:
                    self._rear = current.prev
                else:
                    current.next.prev = current.prev

                current.prev = None
                current.next = None
                self._size -= 1
                return current.value
            current = current.next
        return None
