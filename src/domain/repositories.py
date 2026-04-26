"""
Contratos abstractos para acceso a datos.

Las interfaces definidas en este modulo desacoplan la logica de aplicacion
de los detalles concretos de persistencia.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from .entities import ChatMessage, Product


class IProductRepository(ABC):
    """
    Contrato para repositorios de productos.

    Las implementaciones concretas pueden usar SQLAlchemy, memoria o
    cualquier otra fuente de datos mientras respeten esta interfaz.
    """

    @abstractmethod
    def get_all(self) -> List[Product]:
        """
        Recupera todos los productos disponibles en el sistema.

        Returns:
            List[Product]: Lista completa de productos.
        """

    @abstractmethod
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """
        Busca un producto por su identificador.

        Args:
            product_id (int): Identificador del producto.

        Returns:
            Optional[Product]: Producto encontrado o ``None`` si no existe.
        """

    @abstractmethod
    def get_by_brand(self, brand: str) -> List[Product]:
        """
        Recupera productos de una marca especifica.

        Args:
            brand (str): Marca a consultar.

        Returns:
            List[Product]: Productos asociados a la marca.
        """

    @abstractmethod
    def get_by_category(self, category: str) -> List[Product]:
        """
        Recupera productos de una categoria especifica.

        Args:
            category (str): Categoria a consultar.

        Returns:
            List[Product]: Productos asociados a la categoria.
        """

    @abstractmethod
    def save(self, product: Product) -> Product:
        """
        Persiste un producto nuevo o existente.

        Args:
            product (Product): Entidad a guardar.

        Returns:
            Product: Producto persistido, potencialmente con ID asignado.
        """

    @abstractmethod
    def delete(self, product_id: int) -> bool:
        """
        Elimina un producto por su identificador.

        Args:
            product_id (int): Identificador del producto a eliminar.

        Returns:
            bool: ``True`` si el producto fue eliminado.
        """


class IChatRepository(ABC):
    """
    Contrato para almacenamiento de mensajes de chat.

    Esta interfaz cubre guardado, consulta historica y limpieza de sesiones.
    """

    @abstractmethod
    def save_message(self, message: ChatMessage) -> ChatMessage:
        """
        Guarda un mensaje de chat en la persistencia.

        Args:
            message (ChatMessage): Mensaje a almacenar.

        Returns:
            ChatMessage: Mensaje almacenado con su ID definitivo.
        """

    @abstractmethod
    def get_session_history(
        self, session_id: str, limit: Optional[int] = None
    ) -> List[ChatMessage]:
        """
        Recupera el historial de una sesion.

        Args:
            session_id (str): Identificador de la sesion.
            limit (Optional[int]): Numero maximo de mensajes a devolver.

        Returns:
            List[ChatMessage]: Historial en orden cronologico.
        """

    @abstractmethod
    def delete_session_history(self, session_id: str) -> int:
        """
        Elimina todos los mensajes de una sesion.

        Args:
            session_id (str): Identificador de la sesion.

        Returns:
            int: Cantidad de mensajes eliminados.
        """

    @abstractmethod
    def get_recent_messages(self, session_id: str, count: int) -> List[ChatMessage]:
        """
        Recupera los ultimos mensajes de una sesion.

        Args:
            session_id (str): Identificador de la sesion.
            count (int): Numero de mensajes a recuperar.

        Returns:
            List[ChatMessage]: Mensajes recientes en orden cronologico.
        """
