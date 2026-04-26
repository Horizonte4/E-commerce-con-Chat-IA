#!/usr/bin/env python3
"""
Script para poblar la base de datos con datos de prueba.

Se utiliza durante desarrollo para crear un conjunto pequeno de productos
sin depender de una carga manual desde la API.
"""

from src.domain.entities import Product
from src.infrastructure.db.database import SessionLocal, init_db
from src.infrastructure.repositories.product_repository import SQLProductRepository
from src.python_compat import ensure_supported_python


ensure_supported_python()


def populate_database() -> None:
    """
    Inserta productos de ejemplo en la base de datos local.

    Returns:
        None

    Raises:
        Exception: Si ocurre cualquier error al guardar los productos.
    """
    init_db()
    db = SessionLocal()

    try:
        repo = SQLProductRepository(db)

        test_products = [
            Product(
                id=None,
                name="Nike Air Max 270",
                brand="Nike",
                category="Running",
                size="42",
                color="Black",
                price=150.0,
                stock=10,
                description="Zapatillas running con amortiguacion Air Max",
            ),
            Product(
                id=None,
                name="Adidas Stan Smith",
                brand="Adidas",
                category="Casual",
                size="41",
                color="White",
                price=80.0,
                stock=15,
                description="Zapatillas clasicas de cuero blanco",
            ),
            Product(
                id=None,
                name="Puma RS-X",
                brand="Puma",
                category="Lifestyle",
                size="43",
                color="Blue",
                price=120.0,
                stock=8,
                description="Zapatillas retro con diseno moderno",
            ),
            Product(
                id=None,
                name="Converse All Star",
                brand="Converse",
                category="Casual",
                size="40",
                color="Red",
                price=65.0,
                stock=20,
                description="Zapatillas canvas clasicas de cana alta",
            ),
            Product(
                id=None,
                name="New Balance 574",
                brand="New Balance",
                category="Casual",
                size="42",
                color="Navy",
                price=95.0,
                stock=12,
                description="Zapatillas vintage con suela de goma",
            ),
        ]

        saved_products = []
        for product in test_products:
            saved = repo.save(product)
            saved_products.append(saved)
            print(f"Producto guardado: {saved.name} (ID: {saved.id})")

        print(f"\nBase de datos poblada exitosamente con {len(saved_products)} productos")

    except Exception as e:
        print(f"Error poblando base de datos: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    populate_database()
