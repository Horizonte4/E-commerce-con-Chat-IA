from datetime import datetime

import pytest

from src.domain.entities import ChatContext, ChatMessage, Product


def make_product(**overrides) -> Product:
    data = {
        "id": 1,
        "name": "Nike Air Zoom Pegasus 39",
        "brand": "Nike",
        "category": "Running",
        "size": "42",
        "color": "Black",
        "price": 129.99,
        "stock": 10,
        "description": "Zapatillas de running",
    }
    data.update(overrides)
    return Product(**data)


def make_chat_message(**overrides) -> ChatMessage:
    data = {
        "id": 1,
        "session_id": "session-1",
        "role": "user",
        "message": "Hola",
        "timestamp": datetime(2026, 4, 26, 12, 0, 0),
    }
    data.update(overrides)
    return ChatMessage(**data)


class TestProductValidation:
    def test_should_raise_error_when_name_is_empty(self):
        with pytest.raises(ValueError, match="nombre del producto"):
            make_product(name="   ")

    def test_should_raise_error_when_price_is_not_positive(self):
        with pytest.raises(ValueError, match="precio debe ser mayor a 0"):
            make_product(price=0)

    def test_should_raise_error_when_stock_is_negative(self):
        with pytest.raises(ValueError, match="stock no puede ser negativo"):
            make_product(stock=-1)


class TestProductMethods:
    def test_is_available_returns_true_when_stock_exists(self):
        product = make_product(stock=5)

        assert product.is_available() is True

    def test_is_available_returns_false_when_stock_is_zero(self):
        product = make_product(stock=0)

        assert product.is_available() is False

    def test_reduce_stock_decreases_stock(self):
        product = make_product(stock=10)

        product.reduce_stock(4)

        assert product.stock == 6

    def test_reduce_stock_should_raise_error_when_quantity_is_not_positive(self):
        product = make_product(stock=10)

        with pytest.raises(ValueError, match="cantidad a reducir debe ser positiva"):
            product.reduce_stock(0)

    def test_reduce_stock_should_raise_error_when_quantity_exceeds_stock(self):
        product = make_product(stock=3)

        with pytest.raises(ValueError, match="suficiente stock"):
            product.reduce_stock(4)


class TestChatMessageValidation:
    def test_should_raise_error_when_role_is_invalid(self):
        with pytest.raises(ValueError, match="role debe ser 'user' o 'assistant'"):
            make_chat_message(role="system")

    def test_should_raise_error_when_session_id_is_empty(self):
        with pytest.raises(ValueError, match="session_id no puede estar vac"):
            make_chat_message(session_id=" ")

    def test_should_raise_error_when_message_is_empty(self):
        with pytest.raises(ValueError, match="mensaje no puede estar vac"):
            make_chat_message(message=" ")


class TestChatContext:
    def test_format_for_prompt_returns_expected_labels_and_order(self):
        messages = [
            make_chat_message(role="user", message="Hola"),
            make_chat_message(id=2, role="assistant", message="Hola, en que puedo ayudarte?"),
            make_chat_message(id=3, role="user", message="Busco tenis negros"),
        ]
        context = ChatContext(messages=messages)

        formatted = context.format_for_prompt()

        assert formatted == (
            "Usuario: Hola\n"
            "Asistente: Hola, en que puedo ayudarte?\n"
            "Usuario: Busco tenis negros"
        )

    def test_format_for_prompt_uses_only_recent_messages(self):
        messages = [
            make_chat_message(id=1, role="user", message="m1"),
            make_chat_message(id=2, role="assistant", message="m2"),
            make_chat_message(id=3, role="user", message="m3"),
        ]
        context = ChatContext(messages=messages, max_messages=2)

        formatted = context.format_for_prompt()

        assert formatted == "Asistente: m2\nUsuario: m3"
