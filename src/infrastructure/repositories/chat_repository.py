"""
Repositorio SQLAlchemy para historial de chat.

Este modulo implementa el contrato del dominio para mensajes de chat usando
la tabla `chat_memory`.
"""

from typing import List, Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from ...domain.entities import ChatMessage
from ...domain.repositories import IChatRepository
from ..db.models import ChatMemoryModel


class SQLChatRepository(IChatRepository):
    """
    Implementacion concreta del repositorio de mensajes de chat.

    Attributes:
        db (Session): Sesion activa de SQLAlchemy.
    """

    def __init__(self, db: Session):
        """
        Inicializa el repositorio con una sesion de base de datos.

        Args:
            db (Session): Sesion activa de SQLAlchemy.
        """
        self.db = db

    def _model_to_entity(self, model: ChatMemoryModel) -> ChatMessage:
        """
        Convierte un modelo ORM en una entidad de dominio.

        Args:
            model (ChatMemoryModel): Registro ORM del historial.

        Returns:
            ChatMessage: Entidad de dominio equivalente.
        """
        return ChatMessage(
            id=model.id,
            session_id=model.session_id,
            role=model.role,
            message=model.message,
            timestamp=model.timestamp,
        )

    def _entity_to_model(self, entity: ChatMessage) -> ChatMemoryModel:
        """
        Convierte una entidad de dominio en un modelo ORM.

        Args:
            entity (ChatMessage): Mensaje del dominio a persistir.

        Returns:
            ChatMemoryModel: Modelo ORM listo para guardar.
        """
        return ChatMemoryModel(
            id=entity.id,
            session_id=entity.session_id,
            role=entity.role,
            message=entity.message,
            timestamp=entity.timestamp,
        )

    def save_message(self, message: ChatMessage) -> ChatMessage:
        """
        Guarda un mensaje en la persistencia.

        Args:
            message (ChatMessage): Mensaje a registrar.

        Returns:
            ChatMessage: Mensaje persistido con ID asignado.
        """
        model = self._entity_to_model(message)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._model_to_entity(model)

    def get_session_history(self, session_id: str, limit: Optional[int] = None) -> List[ChatMessage]:
        """
        Recupera el historial completo o parcial de una sesion.

        Args:
            session_id (str): Identificador de la sesion.
            limit (Optional[int]): Numero maximo de mensajes a devolver.

        Returns:
            List[ChatMessage]: Mensajes ordenados del mas antiguo al mas
            reciente.
        """
        query = self.db.query(ChatMemoryModel).filter(
            ChatMemoryModel.session_id == session_id
        ).order_by(desc(ChatMemoryModel.timestamp))

        if limit:
            query = query.limit(limit)

        models = query.all()
        messages = [self._model_to_entity(model) for model in models]
        messages.reverse()
        return messages

    def delete_session_history(self, session_id: str) -> int:
        """
        Elimina todos los mensajes de una sesion.

        Args:
            session_id (str): Identificador de la sesion.

        Returns:
            int: Cantidad de mensajes eliminados.
        """
        count = self.db.query(ChatMemoryModel).filter(
            ChatMemoryModel.session_id == session_id
        ).count()

        self.db.query(ChatMemoryModel).filter(
            ChatMemoryModel.session_id == session_id
        ).delete()

        self.db.commit()
        return count

    def get_recent_messages(self, session_id: str, count: int) -> List[ChatMessage]:
        """
        Recupera los ultimos mensajes de una sesion.

        Args:
            session_id (str): Identificador de la sesion.
            count (int): Numero maximo de mensajes a devolver.

        Returns:
            List[ChatMessage]: Mensajes recientes ordenados cronologicamente.
        """
        models = (
            self.db.query(ChatMemoryModel)
            .filter(ChatMemoryModel.session_id == session_id)
            .order_by(desc(ChatMemoryModel.timestamp))
            .limit(count)
            .all()
        )

        messages = [self._model_to_entity(model) for model in models]
        messages.reverse()
        return messages
