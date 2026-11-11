"""Funciones de seguridad: contraseñas y tokens JWT.
"""

from datetime import datetime, timedelta, timezone

from jwt import PyJWTError, decode, encode
from pwdlib import PasswordHash

from paseos.core.settings import Settings

settings = Settings()
pwd_context = PasswordHash.recommended()


def get_password_hash(password: str) -> str:
    """Convierte la contraseña en un hash. Es lo único que se guarda."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """True si la contraseña escrita corresponde a ese hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """Crea un JWT firmado con SECRET_KEY y con fecha de vencimiento."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({'exp': expire})
    return encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """Devuelve el contenido del token, o None si es inválido o venció."""
    try:
        return decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
    except PyJWTError:
        return None