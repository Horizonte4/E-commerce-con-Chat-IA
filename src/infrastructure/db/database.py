"""
Configuracion de acceso a base de datos.

Este modulo define el engine de SQLAlchemy, la fabrica de sesiones y las
utilidades de inicializacion usadas por la API.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker


SQLALCHEMY_DATABASE_URL = "sqlite:///./data/ecommerce_chat.db"
"""str: URL de conexion por defecto para la base de datos SQLite local."""

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
"""Engine: Motor de SQLAlchemy configurado para SQLite."""

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
"""sessionmaker: Fabrica de sesiones sincronas para la aplicacion."""

Base = declarative_base()
"""DeclarativeMeta: Clase base para todos los modelos ORM."""


def get_db() -> Session:
    """
    Proporciona una sesion de base de datos para FastAPI.

    Esta funcion se utiliza como dependencia y garantiza el cierre de la
    sesion incluso si ocurre un error durante la solicitud.

    Yields:
        Session: Sesion activa de SQLAlchemy.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Inicializa la base de datos creando todas las tablas.

    Returns:
        None

    Note:
        Esta funcion debe ejecutarse antes de atender solicitudes si la base
        de datos aun no existe.
    """
    Base.metadata.create_all(bind=engine)
