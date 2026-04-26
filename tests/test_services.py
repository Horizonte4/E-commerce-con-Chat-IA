import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock

import pytest

from src.application.chat_service import ChatService
from src.application.dtos import ChatMessageRequestDTO, ProductDTO
from src.application.product_service import ProductService
from src.domain.entities import ChatMessage, Product
from src.domain.exceptions import ChatServiceError, ProductNotFoundError


def make_product(**overrides) -> Product:
    data = {
        "id": 1,
        "name": "Nike v2k run",
        "brand": "Nike",
        "category": "Running",
        "size": "39",
        "color": "Black",
        "price": 129.99,
        "stock": 5,
        "description": "Zapatillas de running",
    }
    data.update(overrides)
    return Product(**data)


def make_product_dto(**overrides) -> ProductDTO:
    data = {
        "name": "Nike Air Zoom",
        "brand": "Nike",
        "category": "Running",
        "size": "42",
        "color": "Black",
        "price": 129.99,
        "stock": 6,
        "description": "Zapatillas de running",
    }
    data.update(overrides)
    return ProductDTO(**data)


def make_chat_message(**overrides) -> ChatMessage:
    data = {
        "id": 1,
        "session_id": "session-1",
        "role": "user",
        "message": "Hola",
        "timestamp": datetime.now(timezone.utc),
    }
    data.update(overrides)
    return ChatMessage(**data)


@pytest.fixture
def sample_products():
    return [
        make_product(
            id=1,
            name="Nike Air Zoom Pegasus 39",
            brand="Nike",
            category="Running",
            color="Black",
            price=129.99,
            stock=16,
        ),
        make_product(
            id=2,
            name="Adidas Ultraboost 22",
            brand="Adidas",
            category="Running",
            color="White",
            price=189.99,
            stock=0,
        ),
        make_product(
            id=3,
            name="Nike Revolution 6",
            brand="Nike",
            category="Casual",
            color="Blue",
            price=79.99,
            stock=7,
        ),
    ]


@pytest.fixture
def product_repository():
    return Mock()


@pytest.fixture
def chat_repository():
    return Mock()


@pytest.fixture
def ai_service():
    service = Mock()
    service.generate_response = AsyncMock(return_value="Te recomiendo Nike Air Zoom Pegasus 39")
    return service


class TestProductService:
    def test_get_all_products_returns_repository_products(self, product_repository, sample_products):
        product_repository.get_all.return_value = sample_products
        service = ProductService(product_repository)

        result = service.get_all_products()

        assert result == sample_products
        product_repository.get_all.assert_called_once_with()

    def test_get_product_by_id_returns_product(self, product_repository, sample_products):
        product_repository.get_by_id.return_value = sample_products[0]
        service = ProductService(product_repository)

        result = service.get_product_by_id(1)

        assert result == sample_products[0]
        product_repository.get_by_id.assert_called_once_with(1)

    def test_get_product_by_id_raises_when_product_does_not_exist(self, product_repository):
        product_repository.get_by_id.return_value = None
        service = ProductService(product_repository)

        with pytest.raises(ProductNotFoundError, match="Producto con ID 999 no encontrado"):
            service.get_product_by_id(999)

    def test_search_products_filters_by_multiple_criteria(self, product_repository, sample_products):
        product_repository.get_all.return_value = sample_products
        service = ProductService(product_repository)

        result = service.search_products(
            {
                "brand": "nike",
                "category": "running",
                "min_price": 100,
                "max_price": 150,
                "name_contains": "pegasus",
            }
        )

        assert result == [sample_products[0]]

    def test_create_product_builds_entity_and_saves_it(self, product_repository):
        captured = {}

        def save_side_effect(product):
            captured["product"] = product
            return product

        product_repository.save.side_effect = save_side_effect
        service = ProductService(product_repository)
        product_dto = make_product_dto()

        result = service.create_product(product_dto)

        assert result.id is None
        assert result.name == product_dto.name
        assert captured["product"].brand == product_dto.brand
        product_repository.save.assert_called_once()

    def test_update_product_validates_existence_and_saves_updated_entity(
        self, product_repository, sample_products
    ):
        product_repository.get_by_id.return_value = sample_products[0]
        product_repository.save.side_effect = lambda product: product
        service = ProductService(product_repository)
        product_dto = make_product_dto(name="Nike Actualizado", stock=20)

        result = service.update_product(1, product_dto)

        assert result.id == 1
        assert result.name == "Nike Actualizado"
        assert result.stock == 20
        product_repository.get_by_id.assert_called_once_with(1)
        product_repository.save.assert_called_once()

    def test_delete_product_raises_when_product_does_not_exist(self, product_repository):
        product_repository.get_by_id.return_value = None
        service = ProductService(product_repository)

        with pytest.raises(ProductNotFoundError):
            service.delete_product(50)

        product_repository.delete.assert_not_called()

    def test_get_available_products_returns_repository_result(self, product_repository, sample_products):
        product_repository.get_available_products.return_value = [sample_products[0], sample_products[2]]
        service = ProductService(product_repository)

        result = service.get_available_products()

        assert result == [sample_products[0], sample_products[2]]
        product_repository.get_available_products.assert_called_once_with()


class TestChatService:
    def test_process_message_returns_response_and_persists_messages(
        self, product_repository, chat_repository, ai_service, sample_products
    ):
        request = ChatMessageRequestDTO(session_id="session-1", message="Quiero tenis negros")
        recent_messages = [
            make_chat_message(id=1, role="user", message="Hola"),
            make_chat_message(id=2, role="assistant", message="Hola, en que te ayudo?"),
        ]
        saved_messages = []

        def save_message_side_effect(message):
            saved_messages.append(message)
            return ChatMessage(
                id=len(saved_messages),
                session_id=message.session_id,
                role=message.role,
                message=message.message,
                timestamp=message.timestamp,
            )

        product_repository.get_all.return_value = sample_products
        chat_repository.get_recent_messages.return_value = recent_messages
        chat_repository.save_message.side_effect = save_message_side_effect
        service = ChatService(product_repository, chat_repository, ai_service)

        result = asyncio.run(service.process_message(request))

        assert result.session_id == "session-1"
        assert result.user_message == "Quiero tenis negros"
        assert result.assistant_message == "Te recomiendo Nike Air Zoom Pegasus 39"
        assert len(saved_messages) == 2
        assert saved_messages[0].role == "user"
        assert saved_messages[1].role == "assistant"
        product_repository.get_all.assert_called_once_with()
        chat_repository.get_recent_messages.assert_called_once_with("session-1", 6)
        ai_service.generate_response.assert_awaited_once()

    def test_process_message_raises_when_ai_service_is_missing(
        self, product_repository, chat_repository
    ):
        request = ChatMessageRequestDTO(session_id="session-1", message="Hola")
        service = ChatService(product_repository, chat_repository, None)

        with pytest.raises(ChatServiceError, match="servicio de IA no esta configurado"):
            asyncio.run(service.process_message(request))

    def test_process_message_wraps_unexpected_errors(
        self, product_repository, chat_repository, ai_service
    ):
        request = ChatMessageRequestDTO(session_id="session-1", message="Hola")
        product_repository.get_all.side_effect = RuntimeError("db down")
        service = ChatService(product_repository, chat_repository, ai_service)

        with pytest.raises(ChatServiceError, match="db down"):
            asyncio.run(service.process_message(request))

    def test_get_session_history_returns_repository_history(self, product_repository, chat_repository):
        history = [
            make_chat_message(id=1, role="user", message="Hola"),
            make_chat_message(id=2, role="assistant", message="Hola, en que te ayudo?"),
        ]
        chat_repository.get_session_history.return_value = history
        service = ChatService(product_repository, chat_repository, Mock())

        result = service.get_session_history("session-1", 10)

        assert result == history
        chat_repository.get_session_history.assert_called_once_with("session-1", 10)

    def test_clear_session_history_returns_deleted_count(self, product_repository, chat_repository):
        chat_repository.delete_session_history.return_value = 4
        service = ChatService(product_repository, chat_repository, Mock())

        result = service.clear_session_history("session-1")

        assert result == 4
        chat_repository.delete_session_history.assert_called_once_with("session-1")
