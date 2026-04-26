"""
Utilidades de base de datos para inicializacion y datos semilla.

Este modulo expone helpers para abrir sesiones y cargar el catalogo inicial
cuando la base de datos se encuentra vacia.
"""

from .database import SessionLocal
from .models import ProductModel


def load_initial_data() -> int:
    """
    Carga los 10 productos iniciales si la tabla de productos esta vacia.

    La funcion actua como semilla idempotente: si ya existe al menos un
    producto, no inserta nada adicional.

    Returns:
        int: Cantidad de productos insertados. Sera `10` cuando la tabla este
        vacia o `0` cuando ya existan registros.

    Raises:
        Exception: Si ocurre un error durante la transaccion de insercion.
    """
    db = SessionLocal()
    try:
        product_count = db.query(ProductModel).count()
        if product_count > 0:
            return 0

        initial_products = [
            ProductModel(
                name="Nike Air Zoom Pegasus 39",
                brand="Nike",
                category="Running",
                size="42",
                color="Black/White",
                price=129.99,
                stock=15,
                description="Zapatillas de running comodas y ligeras para entrenamientos diarios",
            ),
            ProductModel(
                name="Nike React Element 55",
                brand="Nike",
                category="Casual",
                size="41",
                color="White",
                price=89.99,
                stock=8,
                description="Zapatillas urbanas versatiles para uso diario",
            ),
            ProductModel(
                name="Adidas Ultraboost 22",
                brand="Adidas",
                category="Running",
                size="43",
                color="Black",
                price=189.99,
                stock=12,
                description="Zapatillas premium con tecnologia Boost para maxima comodidad",
            ),
            ProductModel(
                name="Adidas Stan Smith",
                brand="Adidas",
                category="Casual",
                size="40",
                color="White",
                price=79.99,
                stock=20,
                description="Clasicas zapatillas de tenis blancas, icono del estilo",
            ),
            ProductModel(
                name="Puma Suede Classic",
                brand="Puma",
                category="Casual",
                size="42",
                color="Black",
                price=69.99,
                stock=18,
                description="Zapatillas retro con plataforma elevada, estilo urbano",
            ),
            ProductModel(
                name="Puma RS-X3 Puzzle",
                brand="Puma",
                category="Casual",
                size="41",
                color="Multi",
                price=109.99,
                stock=6,
                description="Zapatillas chunky con diseno puzzle colorido",
            ),
            ProductModel(
                name="New Balance 574",
                brand="New Balance",
                category="Casual",
                size="43",
                color="Navy",
                price=89.99,
                stock=14,
                description="Zapatillas clasicas con herencia running, versatiles",
            ),
            ProductModel(
                name="Converse Chuck Taylor All Star",
                brand="Converse",
                category="Casual",
                size="42",
                color="Navy",
                price=59.99,
                stock=25,
                description="Las clasicas zapatillas de lona, atemporales",
            ),
            ProductModel(
                name="Vans Old Skool",
                brand="Vans",
                category="Casual",
                size="41",
                color="Black/White",
                price=64.99,
                stock=16,
                description="Zapatillas skate con la iconica banda lateral",
            ),
            ProductModel(
                name="Reebok Club C 85",
                brand="Reebok",
                category="Formal",
                size="42",
                color="White",
                price=79.99,
                stock=10,
                description="Zapatillas elegantes para ocasiones formales",
            ),
        ]

        db.add_all(initial_products)
        db.commit()
        return len(initial_products)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
