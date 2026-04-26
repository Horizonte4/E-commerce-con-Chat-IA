"""
Servicios de aplicacion relacionados con el chat con IA.

Este modulo orquesta productos, historial y proveedor de lenguaje para
responder conversaciones del usuario.
"""

from datetime import datetime, timezone
from typing import List, Optional

from ..domain.entities import ChatContext, ChatMessage
from ..domain.exceptions import ChatServiceError
from ..domain.repositories import IChatRepository, IProductRepository
from .dtos import ChatMessageRequestDTO, ChatMessageResponseDTO


class ChatService:
    """
    Servicio de aplicacion para gestionar el chat con IA.

    Este servicio coordina el acceso al catalogo, el historial de mensajes
    y el proveedor de IA para generar respuestas contextuales.

    Attributes:
        _product_repository (IProductRepository): Repositorio de productos.
        _chat_repository (IChatRepository): Repositorio del historial de chat.
        _ai_service (object | None): Servicio encargado de generar texto.
    """

    def __init__(
        self,
        product_repository: IProductRepository,
        chat_repository: IChatRepository,
        ai_service=None,
    ):
        """
        Inicializa el servicio con sus dependencias.

        Args:
            product_repository (IProductRepository): Acceso al catalogo.
            chat_repository (IChatRepository): Acceso al historial de chat.
            ai_service (object | None): Proveedor de IA con metodo
                `generate_response`.
        """
        self._product_repository = product_repository
        self._chat_repository = chat_repository
        self._ai_service = ai_service

    async def process_message(self, request: ChatMessageRequestDTO) -> ChatMessageResponseDTO:
        """
        Procesa un mensaje del usuario y genera una respuesta con IA.

        El flujo incluye consulta de productos, recuperacion del historial,
        construccion de contexto, generacion de respuesta y persistencia de
        ambos mensajes.

        Args:
            request (ChatMessageRequestDTO): Solicitud con `session_id` y
                mensaje del usuario.

        Returns:
            ChatMessageResponseDTO: Respuesta generada con timestamp final.

        Raises:
            ChatServiceError: Si la IA no esta configurada o si ocurre
                cualquier error durante el proceso.
        """
        try:
            if self._ai_service is None:
                raise ChatServiceError("El servicio de IA no esta configurado")

            products = self._product_repository.get_all()
            recent_messages = self._chat_repository.get_recent_messages(request.session_id, 6)
            chat_context = ChatContext(messages=recent_messages, max_messages=6)

            ai_response = await self._ai_service.generate_response(
                user_message=request.message,
                products=products,
                context=chat_context,
            )

            user_message = ChatMessage(
                id=None,
                session_id=request.session_id,
                role="user",
                message=request.message,
                timestamp=datetime.now(timezone.utc),
            )
            self._chat_repository.save_message(user_message)

            assistant_message = ChatMessage(
                id=None,
                session_id=request.session_id,
                role="assistant",
                message=ai_response,
                timestamp=datetime.now(timezone.utc),
            )
            saved_assistant_message = self._chat_repository.save_message(assistant_message)

            return ChatMessageResponseDTO(
                session_id=request.session_id,
                user_message=request.message,
                assistant_message=ai_response,
                timestamp=saved_assistant_message.timestamp,
            )
        except ChatServiceError:
            raise
        except Exception as e:
            raise ChatServiceError(f"Error procesando mensaje: {str(e)}") from e

    def get_session_history(self, session_id: str, limit: Optional[int] = None) -> List[ChatMessage]:
        """
        Recupera el historial de una sesion especifica.

        Args:
            session_id (str): Identificador de la sesion.
            limit (Optional[int]): Numero maximo de mensajes a recuperar.

        Returns:
            List[ChatMessage]: Historial de la sesion en orden cronologico.
        """
        return self._chat_repository.get_session_history(session_id, limit)

    def clear_session_history(self, session_id: str) -> int:
        """
        Elimina todos los mensajes de una sesion.

        Args:
            session_id (str): Identificador de la sesion a limpiar.

        Returns:
            int: Cantidad de mensajes eliminados.
        """
        return self._chat_repository.delete_session_history(session_id)
