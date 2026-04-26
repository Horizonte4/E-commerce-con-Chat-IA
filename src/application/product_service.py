"""
Servicios de aplicacion relacionados con productos.

Este modulo contiene la logica que orquesta validaciones, filtros y
persistencia para el catalogo del e-commerce.
"""

from typing import Any, Dict, List

from ..domain.entities import Product
from ..domain.exceptions import ProductNotFoundError
from ..domain.repositories import IProductRepository
from .dtos import ProductDTO


class ProductService:
    """
    Servicio de aplicacion para operaciones del catalogo.

    Attributes:
        _product_repository (IProductRepository): Repositorio inyectado para
            acceder a productos.
    """

    def __init__(self, product_repository: IProductRepository):
        """
        Inicializa el servicio con su dependencia principal.

        Args:
            product_repository (IProductRepository): Repositorio concreto para
                leer y persistir productos.
        """
        self._product_repository = product_repository

    def get_all_products(self) -> List[Product]:
        """
        Lista todos los productos registrados.

        Returns:
            List[Product]: Productos del catalogo completo.
        """
        return self._product_repository.get_all()

    def get_product_by_id(self, product_id: int) -> Product:
        """
        Busca un producto por su identificador.

        Args:
            product_id (int): Identificador del producto.

        Returns:
            Product: Producto encontrado.

        Raises:
            ProductNotFoundError: Si no existe un producto con ese ID.
        """
        product = self._product_repository.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError(product_id)
        return product

    def search_products(self, filters: Dict[str, Any]) -> List[Product]:
        """
        Filtra productos usando criterios simples en memoria.

        Args:
            filters (Dict[str, Any]): Diccionario con filtros como `brand`,
                `category`, `min_price`, `max_price` o `name_contains`.

        Returns:
            List[Product]: Productos que cumplen todos los criterios.
        """
        all_products = self._product_repository.get_all()
        filtered_products = []

        for product in all_products:
            match = True

            if "brand" in filters and filters["brand"]:
                if product.brand.lower() != filters["brand"].lower():
                    match = False

            if "category" in filters and filters["category"]:
                if product.category.lower() != filters["category"].lower():
                    match = False

            if "min_price" in filters and filters["min_price"] is not None:
                if product.price < filters["min_price"]:
                    match = False

            if "max_price" in filters and filters["max_price"] is not None:
                if product.price > filters["max_price"]:
                    match = False

            if "name_contains" in filters and filters["name_contains"]:
                if filters["name_contains"].lower() not in product.name.lower():
                    match = False

            if match:
                filtered_products.append(product)

        return filtered_products

    def create_product(self, product_dto: ProductDTO) -> Product:
        """
        Crea un producto a partir de un DTO y lo persiste.

        Args:
            product_dto (ProductDTO): Datos del producto a registrar.

        Returns:
            Product: Producto almacenado por el repositorio.
        """
        product = Product(
            id=None,
            name=product_dto.name,
            brand=product_dto.brand,
            category=product_dto.category,
            size=product_dto.size,
            color=product_dto.color,
            price=product_dto.price,
            stock=product_dto.stock,
            description=product_dto.description,
        )
        return self._product_repository.save(product)

    def update_product(self, product_id: int, product_dto: ProductDTO) -> Product:
        """
        Actualiza un producto existente.

        Args:
            product_id (int): Identificador del producto a actualizar.
            product_dto (ProductDTO): Datos nuevos del producto.

        Returns:
            Product: Producto actualizado.

        Raises:
            ProductNotFoundError: Si el producto objetivo no existe.
        """
        self.get_product_by_id(product_id)

        updated_product = Product(
            id=product_id,
            name=product_dto.name,
            brand=product_dto.brand,
            category=product_dto.category,
            size=product_dto.size,
            color=product_dto.color,
            price=product_dto.price,
            stock=product_dto.stock,
            description=product_dto.description,
        )
        return self._product_repository.save(updated_product)

    def delete_product(self, product_id: int) -> bool:
        """
        Elimina un producto del catalogo.

        Args:
            product_id (int): Identificador del producto a eliminar.

        Returns:
            bool: ``True`` si el repositorio confirma la eliminacion.

        Raises:
            ProductNotFoundError: Si el producto no existe.
        """
        self.get_product_by_id(product_id)
        return self._product_repository.delete(product_id)

    def get_available_products(self) -> List[Product]:
        """
        Recupera solo productos con stock disponible.

        Returns:
            List[Product]: Productos disponibles para la venta.
        """
        return self._product_repository.get_available_products()
