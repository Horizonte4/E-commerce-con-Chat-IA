"""
Excepciones especificas del dominio.

Este modulo concentra errores de negocio reutilizables por servicios,
repositorios y endpoints.
"""


class ProductNotFoundError(Exception):
    """
    Error de dominio para un producto inexistente.

    Attributes:
        message (str): Descripcion legible del error.
    """

    def __init__(self, product_id: int | None = None):
        """
        Construye la excepcion con un mensaje contextual.

        Args:
            product_id (int | None): Identificador buscado, si se conoce.
        """
        if product_id is not None:
            self.message = f"Producto con ID {product_id} no encontrado"
        else:
            self.message = "Producto no encontrado"
        super().__init__(self.message)


class InvalidProductDataError(Exception):
    """
    Error de dominio para datos invalidos de producto.

    Attributes:
        message (str): Mensaje asociado al error.
    """

    def __init__(self, message: str = "Datos de producto invalidos"):
        """
        Inicializa la excepcion con un mensaje personalizado.

        Args:
            message (str): Descripcion del problema detectado.
        """
        self.message = message
        super().__init__(self.message)


class ChatServiceError(Exception):
    """
    Error de dominio para fallas durante el flujo de chat.

    Attributes:
        message (str): Descripcion legible de la falla.
    """

    def __init__(self, message: str = "Error en el servicio de chat"):
        """
        Inicializa la excepcion con el detalle correspondiente.

        Args:
            message (str): Mensaje descriptivo del error.
        """
        self.message = message
        super().__init__(self.message)
