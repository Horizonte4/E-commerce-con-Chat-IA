"""
Aplicacion FastAPI principal del proyecto.

Este modulo define la instancia de FastAPI, la configuracion de CORS y los
endpoints REST para productos, chat, historial y health check.
"""

from datetime import datetime, timezone
import os
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from ...application.chat_service import ChatService
from ...application.dtos import (
    ChatHistoryDTO,
    ChatMessageRequestDTO,
    ChatMessageResponseDTO,
    ProductDTO,
)
from ...application.product_service import ProductService
from ...domain.exceptions import ChatServiceError, ProductNotFoundError
from ..db import load_initial_data
from ..db.database import get_db, init_db
from ..llm_providers.gemini_service import GeminiService
from ..repositories.chat_repository import SQLChatRepository
from ..repositories.product_repository import SQLProductRepository


app = FastAPI(
    title="E-commerce Chat IA API",
    description="API REST para sistema de e-commerce con asistente virtual de ventas",
    version="1.0.0",
)
"""FastAPI: Aplicacion principal expuesta por Uvicorn."""

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event() -> None:
    """
    Inicializa la base de datos y carga el catalogo semilla.

    Returns:
        None
    """
    init_db()
    load_initial_data()


def _build_product_service(db: Session) -> ProductService:
    """
    Crea una instancia de `ProductService` para la solicitud actual.

    Args:
        db (Session): Sesion de base de datos activa.

    Returns:
        ProductService: Servicio de productos configurado.
    """
    repository = SQLProductRepository(db)
    return ProductService(repository)


def _build_chat_service(db: Session, ai_service=None) -> ChatService:
    """
    Crea una instancia de `ChatService` para la solicitud actual.

    Args:
        db (Session): Sesion de base de datos activa.
        ai_service (object | None): Servicio de IA opcional.

    Returns:
        ChatService: Servicio de chat configurado.
    """
    product_repository = SQLProductRepository(db)
    chat_repository = SQLChatRepository(db)
    return ChatService(product_repository, chat_repository, ai_service)


def _to_product_dto(product) -> ProductDTO:
    """
    Convierte una entidad `Product` en `ProductDTO`.

    Args:
        product (Product): Entidad de dominio a serializar.

    Returns:
        ProductDTO: DTO listo para respuesta HTTP.
    """
    return ProductDTO(
        id=product.id,
        name=product.name,
        brand=product.brand,
        category=product.category,
        size=product.size,
        color=product.color,
        price=product.price,
        stock=product.stock,
        description=product.description,
    )


def _to_chat_history_dto(message) -> ChatHistoryDTO:
    """
    Convierte una entidad `ChatMessage` en `ChatHistoryDTO`.

    Args:
        message (ChatMessage): Mensaje del dominio.

    Returns:
        ChatHistoryDTO: DTO listo para respuesta HTTP.
    """
    return ChatHistoryDTO(
        id=message.id,
        role=message.role,
        message=message.message,
        timestamp=message.timestamp,
    )


@app.get("/")
def root():
    """
    Retorna informacion basica de la API.

    Este endpoint expone metadatos generales de la aplicacion y la lista
    de rutas principales disponibles para clientes y desarrolladores.

    Returns:
        dict: Objeto JSON con nombre, version, descripcion y endpoints.

    Example:
        GET /
        Response: {
            "name": "E-commerce Chat IA API",
            "version": "1.0.0"
        }
    """
    return {
        "name": "E-commerce Chat IA API",
        "version": app.version,
        "description": app.description,
        "available_endpoints": [
            "GET /",
            "GET /products",
            "GET /products/{product_id}",
            "POST /chat",
            "GET /chat/history/{session_id}",
            "DELETE /chat/history/{session_id}",
            "GET /health",
        ],
    }


@app.get("/products", response_model=List[ProductDTO])
def get_products(db: Session = Depends(get_db)) -> List[ProductDTO]:
    """
    Obtiene la lista completa de productos disponibles.

    Este endpoint retorna todos los productos registrados en la base de
    datos, incluyendo aquellos con stock agotado.

    Args:
        db (Session): Sesion de base de datos inyectada por FastAPI.

    Returns:
        List[ProductDTO]: Lista completa de productos.

    Raises:
        HTTPException: Si ocurre un error inesperado durante la consulta.

    Example:
        GET /products
    """
    try:
        service = _build_product_service(db)
        products = service.get_all_products()
        return [_to_product_dto(product) for product in products]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo productos: {str(e)}") from e


@app.get("/products/{product_id}", response_model=ProductDTO)
def get_product(product_id: int, db: Session = Depends(get_db)) -> ProductDTO:
    """
    Obtiene un producto especifico por su identificador.

    Args:
        product_id (int): Identificador unico del producto.
        db (Session): Sesion de base de datos inyectada por FastAPI.

    Returns:
        ProductDTO: Producto encontrado.

    Raises:
        HTTPException: Con codigo 404 si el producto no existe o 500 si falla
            la operacion.

    Example:
        GET /products/1
    """
    service = _build_product_service(db)

    try:
        product = service.get_product_by_id(product_id)
        return _to_product_dto(product)
    except ProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo producto: {str(e)}") from e


@app.post("/chat", response_model=ChatMessageResponseDTO)
async def process_chat_message(
    request: ChatMessageRequestDTO,
    db: Session = Depends(get_db),
) -> ChatMessageResponseDTO:
    """
    Procesa un mensaje de chat y genera una respuesta con IA.

    Este endpoint construye el servicio de chat, consulta el historial de la
    sesion y delega la generacion de respuesta al proveedor de Gemini.

    Args:
        request (ChatMessageRequestDTO): Mensaje del usuario y sesion.
        db (Session): Sesion de base de datos inyectada por FastAPI.

    Returns:
        ChatMessageResponseDTO: Respuesta del asistente con timestamp.

    Raises:
        HTTPException: Con codigo 500 si la configuracion de IA es invalida
            o si falla el procesamiento.

    Example:
        POST /chat
        Body: {"session_id": "demo", "message": "Busco tenis negros"}
    """
    try:
        service = _build_chat_service(db, GeminiService())
        return await service.process_message(request)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Configuracion de IA invalida: {str(e)}") from e
    except ChatServiceError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}") from e


@app.get("/chat/history/{session_id}", response_model=List[ChatHistoryDTO])
def get_chat_history(
    session_id: str,
    limit: int = Query(10, ge=1, description="Numero maximo de mensajes a retornar"),
    db: Session = Depends(get_db),
) -> List[ChatHistoryDTO]:
    """
    Obtiene el historial de una sesion de chat.

    Args:
        session_id (str): Identificador de la sesion conversacional.
        limit (int): Numero maximo de mensajes a devolver.
        db (Session): Sesion de base de datos inyectada por FastAPI.

    Returns:
        List[ChatHistoryDTO]: Historial de mensajes en orden cronologico.

    Raises:
        HTTPException: Si ocurre un error inesperado durante la consulta.

    Example:
        GET /chat/history/demo-session?limit=10
    """
    try:
        service = _build_chat_service(db)
        history = service.get_session_history(session_id, limit)
        return [_to_chat_history_dto(message) for message in history]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo historial: {str(e)}") from e


@app.delete("/chat/history/{session_id}")
def delete_chat_history(session_id: str, db: Session = Depends(get_db)):
    """
    Elimina el historial completo de una sesion de chat.

    Args:
        session_id (str): Identificador de la sesion a limpiar.
        db (Session): Sesion de base de datos inyectada por FastAPI.

    Returns:
        dict: Objeto con la sesion afectada y la cantidad de mensajes
        eliminados.

    Raises:
        HTTPException: Si ocurre un error durante la operacion.

    Example:
        DELETE /chat/history/demo-session
    """
    try:
        service = _build_chat_service(db)
        deleted_messages = service.clear_session_history(session_id)
        return {"session_id": session_id, "deleted_messages": deleted_messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error eliminando historial: {str(e)}") from e


@app.get("/health")
def health_check():
    """
    Verifica el estado general de la aplicacion.

    Returns:
        dict: Estado, timestamp, version y ambiente actual.

    Example:
        GET /health
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc),
        "version": app.version,
        "environment": os.getenv("ENVIRONMENT", "unknown"),
    }
