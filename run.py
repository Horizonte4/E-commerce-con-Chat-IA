#!/usr/bin/env python3
"""
Punto de entrada para ejecutar la API en desarrollo local.

Este script carga variables de entorno, valida la version de Python y
arranca Uvicorn con recarga automatica.
"""

import os

import uvicorn
from dotenv import load_dotenv

from src.python_compat import ensure_supported_python


load_dotenv()
ensure_supported_python()


def main() -> None:
    """
    Arranca el servidor Uvicorn con configuracion de desarrollo.

    Returns:
        None
    """
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))

    print(f"Iniciando E-commerce Chat IA API en http://{host}:{port}")
    print(f"Documentacion disponible en http://{host}:{port}/docs")

    uvicorn.run(
        "src.infrastructure.api.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    main()
