"""Conexión a la base de datos con SQLAlchemy.

Todos los módulos usan:
    - `Base`: la clase de la que heredan los modelos.
    - `get_db()`: la dependencia de FastAPI que entrega una sesión.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from paseos.core.settings import settings

connect_args = (
    {'check_same_thread': False}
    if settings.DATABASE_URL.startswith('sqlite')
    else {}
)
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    """Clase base de todos los modelos SQLAlchemy."""


def get_db():
    """Entrega una sesión por request y la cierra al terminar."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
