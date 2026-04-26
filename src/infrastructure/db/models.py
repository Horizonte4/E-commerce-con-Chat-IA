"""
Modelos ORM para persistencia con SQLAlchemy.

Este modulo contiene el mapeo entre tablas SQLite y objetos Python de
infraestructura.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Index, Integer, String, Text

from .database import Base


class ProductModel(Base):
    """
    Modelo ORM de la tabla `products`.

    Attributes:
        id (Column): Clave primaria autoincremental.
        name (Column): Nombre del producto.
        brand (Column): Marca del producto.
        category (Column): Categoria principal.
        size (Column): Talla almacenada como texto.
        color (Column): Color del producto.
        price (Column): Precio numerico del producto.
        stock (Column): Cantidad disponible.
        description (Column): Descripcion extendida del producto.
    """

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    brand = Column(String(100))
    category = Column(String(100))
    size = Column(String(20))
    color = Column(String(50))
    price = Column(Float)
    stock = Column(Integer)
    description = Column(Text)


class ChatMemoryModel(Base):
    """
    Modelo ORM de la tabla `chat_memory`.

    Attributes:
        id (Column): Clave primaria del mensaje.
        session_id (Column): Identificador de la sesion.
        role (Column): Rol del emisor del mensaje.
        message (Column): Texto del mensaje.
        timestamp (Column): Momento de creacion del registro.
    """

    __tablename__ = "chat_memory"

    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), index=True)
    role = Column(String(20))
    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_chat_memory_session_timestamp", "session_id", "timestamp"),
    )
