"""
Entidades y value objects del dominio.

Este modulo concentra las estructuras principales del negocio para el
e-commerce: productos, mensajes de chat y contexto conversacional.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Product:
    """
    Entidad que representa un producto del catalogo.

    Esta clase encapsula la informacion minima necesaria para vender un
    producto y parte de la logica de negocio relacionada con inventario.

    Attributes:
        id (Optional[int]): Identificador unico del producto.
        name (str): Nombre comercial del producto.
        brand (str): Marca del producto.
        category (str): Categoria principal del producto.
        size (str): Talla disponible.
        color (str): Color del producto.
        price (float): Precio del producto. Debe ser mayor a cero.
        stock (int): Cantidad disponible en inventario.
        description (str): Descripcion corta para mostrar al usuario.
    """

    id: Optional[int]
    name: str
    brand: str
    category: str
    size: str
    color: str
    price: float
    stock: int
    description: str

    def __post_init__(self) -> None:
        """
        Ejecuta validaciones basicas luego de crear la entidad.

        Raises:
            ValueError: Si el nombre esta vacio, el precio no es positivo
                o el stock es negativo.
        """
        if not self.name or self.name.strip() == "":
            raise ValueError("El nombre del producto no puede estar vacio")
        if self.price <= 0:
            raise ValueError("El precio debe ser mayor a 0")
        if self.stock < 0:
            raise ValueError("El stock no puede ser negativo")

    def is_available(self) -> bool:
        """
        Indica si el producto tiene stock disponible.

        Returns:
            bool: ``True`` si el stock es mayor a cero. ``False`` en caso
            contrario.
        """
        return self.stock > 0

    def reduce_stock(self, quantity: int) -> None:
        """
        Reduce el stock del producto en la cantidad especificada.

        Este metodo valida que la cantidad sea positiva y que exista
        suficiente inventario antes de descontar unidades.

        Args:
            quantity (int): Cantidad a descontar del inventario.

        Raises:
            ValueError: Si la cantidad es cero o negativa, o si supera el
                stock disponible.

        Example:
            >>> product = Product(1, "Zapato", "Marca", "Running", "42", "Black", 100.0, 10, "Desc")
            >>> product.reduce_stock(3)
            >>> product.stock
            7
        """
        if quantity <= 0:
            raise ValueError("La cantidad a reducir debe ser positiva")
        if quantity > self.stock:
            raise ValueError("No hay suficiente stock disponible")
        self.stock -= quantity

    def increase_stock(self, quantity: int) -> None:
        """
        Aumenta el stock del producto.

        Args:
            quantity (int): Cantidad a sumar al inventario.

        Raises:
            ValueError: Si la cantidad es cero o negativa.
        """
        if quantity <= 0:
            raise ValueError("La cantidad a aumentar debe ser positiva")
        self.stock += quantity


@dataclass
class ChatMessage:
    """
    Entidad que representa un mensaje individual del chat.

    Attributes:
        id (Optional[int]): Identificador unico del mensaje.
        session_id (str): Identificador de la sesion de chat.
        role (str): Rol del emisor. Puede ser ``user`` o ``assistant``.
        message (str): Contenido textual del mensaje.
        timestamp (datetime): Fecha y hora de creacion del mensaje.
    """

    id: Optional[int]
    session_id: str
    role: str
    message: str
    timestamp: datetime

    def __post_init__(self) -> None:
        """
        Valida la consistencia minima del mensaje.

        Raises:
            ValueError: Si el rol no es valido, si la sesion esta vacia o si
                el mensaje no tiene contenido.
        """
        if self.role not in {"user", "assistant"}:
            raise ValueError("El role debe ser 'user' o 'assistant'")
        if not self.session_id or self.session_id.strip() == "":
            raise ValueError("El session_id no puede estar vacio")
        if not self.message or self.message.strip() == "":
            raise ValueError("El mensaje no puede estar vacio")

    def is_from_user(self) -> bool:
        """
        Indica si el mensaje fue enviado por el usuario.

        Returns:
            bool: ``True`` si el rol es ``user``.
        """
        return self.role == "user"

    def is_from_assistant(self) -> bool:
        """
        Indica si el mensaje fue enviado por el asistente.

        Returns:
            bool: ``True`` si el rol es ``assistant``.
        """
        return self.role == "assistant"


@dataclass
class ChatContext:
    """
    Value object que encapsula el contexto reciente de una conversacion.

    Attributes:
        messages (list[ChatMessage]): Lista completa de mensajes disponibles.
        max_messages (int): Numero maximo de mensajes que se usaran como
            contexto al construir el prompt.
    """

    messages: list[ChatMessage]
    max_messages: int = 6

    def get_recent_messages(self) -> list[ChatMessage]:
        """
        Retorna los ultimos mensajes segun el limite configurado.

        Returns:
            list[ChatMessage]: Lista de mensajes recientes en orden
            cronologico.
        """
        return self.messages[-self.max_messages :]

    def format_for_prompt(self) -> str:
        """
        Convierte el contexto conversacional en texto para el prompt.

        Returns:
            str: Texto listo para incluir en una solicitud a un modelo de IA.

        Example:
            >>> context.format_for_prompt()
            'Usuario: Hola\\nAsistente: Hola, en que puedo ayudarte?'
        """
        lines = []
        for message in self.get_recent_messages():
            label = "Usuario" if message.role == "user" else "Asistente"
            lines.append(f"{label}: {message.message}")
        return "\n".join(lines)
