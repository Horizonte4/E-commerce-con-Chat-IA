"""
Objetos de transferencia de datos de la capa de aplicacion.

Los DTOs definidos aqui estandarizan la comunicacion entre endpoints,
servicios y serializacion de respuestas.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ProductDTO(BaseModel):
    """
    DTO para exponer informacion de productos.

    Attributes:
        id (Optional[int]): Identificador del producto.
        name (str): Nombre del producto.
        brand (str): Marca del producto.
        category (str): Categoria principal.
        size (str): Talla del producto.
        color (str): Color del producto.
        price (float): Precio de venta.
        stock (int): Cantidad disponible.
        description (str): Descripcion visible para el cliente.
    """

    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    name: str
    brand: str
    category: str
    size: str
    color: str
    price: float
    stock: int
    description: str


class ChatMessageRequestDTO(BaseModel):
    """
    DTO para recibir un mensaje del usuario.

    Attributes:
        session_id (str): Identificador de la sesion conversacional.
        message (str): Texto enviado por el usuario.
    """

    session_id: str
    message: str


class ChatMessageResponseDTO(BaseModel):
    """
    DTO para responder una interaccion de chat.

    Attributes:
        session_id (str): Identificador de la sesion de chat.
        user_message (str): Texto enviado por el usuario.
        assistant_message (str): Texto generado por la IA.
        timestamp (datetime): Fecha y hora asociada a la respuesta.
    """

    session_id: str
    user_message: str
    assistant_message: str
    timestamp: datetime


class ChatHistoryDTO(BaseModel):
    """
    DTO para exponer mensajes historicos de una sesion.

    Attributes:
        id (int): Identificador del mensaje.
        role (str): Rol del emisor.
        message (str): Texto del mensaje.
        timestamp (datetime): Fecha y hora de creacion.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    message: str
    timestamp: datetime
