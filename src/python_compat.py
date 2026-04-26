"""
Utilidades para validar compatibilidad de Python.

Este modulo centraliza la version minima requerida para ejecutar el
proyecto en desarrollo local.
"""

import sys


SUPPORTED_PYTHON = (3, 12)
"""tuple[int, int]: Version exacta soportada por el entorno local."""


def ensure_supported_python() -> None:
    """
    Verifica que el interprete actual sea compatible con el proyecto.

    Returns:
        None

    Raises:
        RuntimeError: Si la version actual no coincide con la version
            soportada definida en `SUPPORTED_PYTHON`.
    """
    current_version = sys.version_info[:2]
    if current_version != SUPPORTED_PYTHON:
        expected = ".".join(str(part) for part in SUPPORTED_PYTHON)
        current = ".".join(str(part) for part in current_version)
        raise RuntimeError(
            f"Python {expected} es requerido por este proyecto. "
            f"Version detectada: {current}. "
            "Crea el entorno virtual con Python 3.12 y reinstala requirements.txt."
        )
