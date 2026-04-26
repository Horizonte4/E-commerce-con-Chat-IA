"""
Repositorio SQLAlchemy para productos.

Este modulo implementa el contrato del dominio usando modelos ORM y una
sesion sincronica de SQLAlchemy.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from ...domain.entities import Product
from ...domain.repositories import IProductRepository
from ..db.models import ProductModel


class SQLProductRepository(IProductRepository):
    """
    Implementacion concreta del repositorio de productos.

    Attributes:
        db (Session): Sesion activa de SQLAlchemy utilizada para consultas y
            persistencia.
    """

    def __init__(self, db: Session):
        """
        Inicializa el repositorio con una sesion de base de datos.

        Args:
            db (Session): Sesion activa de SQLAlchemy.
        """
        self.db = db

    def _model_to_entity(self, model: ProductModel) -> Product:
        """
        Convierte un modelo ORM en una entidad de dominio.

        Args:
            model (ProductModel): Instancia ORM leida de la base de datos.

        Returns:
            Product: Entidad de dominio equivalente.
        """
        return Product(
            id=model.id,
            name=model.name,
            brand=model.brand,
            category=model.category,
            size=model.size,
            color=model.color,
            price=model.price,
            stock=model.stock,
            description=model.description,
        )

    def _entity_to_model(self, entity: Product) -> ProductModel:
        """
        Convierte una entidad de dominio en un modelo ORM.

        Args:
            entity (Product): Entidad a transformar.

        Returns:
            ProductModel: Modelo ORM listo para persistencia.
        """
        return ProductModel(
            id=entity.id,
            name=entity.name,
            brand=entity.brand,
            category=entity.category,
            size=entity.size,
            color=entity.color,
            price=entity.price,
            stock=entity.stock,
            description=entity.description,
        )

    def get_all(self) -> List[Product]:
        """
        Recupera todos los productos almacenados.

        Returns:
            List[Product]: Lista completa de productos.
        """
        models = self.db.query(ProductModel).all()
        return [self._model_to_entity(model) for model in models]

    def get_by_id(self, product_id: int) -> Optional[Product]:
        """
        Busca un producto por su ID.

        Args:
            product_id (int): Identificador del producto.

        Returns:
            Optional[Product]: Producto encontrado o ``None``.
        """
        model = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        return self._model_to_entity(model) if model else None

    def get_by_brand(self, brand: str) -> List[Product]:
        """
        Recupera productos de una marca exacta.

        Args:
            brand (str): Marca a consultar.

        Returns:
            List[Product]: Productos que pertenecen a la marca.
        """
        models = self.db.query(ProductModel).filter(ProductModel.brand == brand).all()
        return [self._model_to_entity(model) for model in models]

    def get_by_category(self, category: str) -> List[Product]:
        """
        Recupera productos de una categoria exacta.

        Args:
            category (str): Categoria a consultar.

        Returns:
            List[Product]: Productos de la categoria solicitada.
        """
        models = self.db.query(ProductModel).filter(ProductModel.category == category).all()
        return [self._model_to_entity(model) for model in models]

    def get_available_products(self) -> List[Product]:
        """
        Recupera productos con stock positivo.

        Returns:
            List[Product]: Productos disponibles para la venta.
        """
        models = self.db.query(ProductModel).filter(ProductModel.stock > 0).all()
        return [self._model_to_entity(model) for model in models]

    def search_products(self, query: str) -> List[Product]:
        """
        Busca productos por nombre o descripcion.

        Args:
            query (str): Texto libre a buscar.

        Returns:
            List[Product]: Productos que coinciden con la busqueda.
        """
        search_filter = f"%{query}%"
        models = self.db.query(ProductModel).filter(
            (ProductModel.name.ilike(search_filter))
            | (ProductModel.description.ilike(search_filter))
        ).all()
        return [self._model_to_entity(model) for model in models]

    def get_products_by_price_range(self, min_price: float, max_price: float) -> List[Product]:
        """
        Recupera productos dentro de un rango de precios.

        Args:
            min_price (float): Precio minimo aceptado.
            max_price (float): Precio maximo aceptado.

        Returns:
            List[Product]: Productos cuyo precio cae en el rango indicado.
        """
        models = self.db.query(ProductModel).filter(
            (ProductModel.price >= min_price) & (ProductModel.price <= max_price)
        ).all()
        return [self._model_to_entity(model) for model in models]

    def save(self, product: Product) -> Product:
        """
        Guarda o actualiza un producto.

        Args:
            product (Product): Entidad a persistir.

        Returns:
            Product: Producto guardado o actualizado.
        """
        model = self._entity_to_model(product)

        if product.id is None:
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)
        else:
            existing = self.db.query(ProductModel).filter(ProductModel.id == product.id).first()
            if existing:
                existing.name = model.name
                existing.brand = model.brand
                existing.category = model.category
                existing.size = model.size
                existing.color = model.color
                existing.price = model.price
                existing.stock = model.stock
                existing.description = model.description
                self.db.commit()
                self.db.refresh(existing)
                model = existing

        return self._model_to_entity(model)

    def delete(self, product_id: int) -> bool:
        """
        Elimina un producto por su identificador.

        Args:
            product_id (int): Identificador del producto a eliminar.

        Returns:
            bool: ``True`` si se elimino un registro, ``False`` si no existia.
        """
        model = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if model:
            self.db.delete(model)
            self.db.commit()
            return True
        return False
