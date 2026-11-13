from pydantic import BaseModel, Field


class Token(BaseModel):
    """Respuesta del login."""

    access_token: str
    token_type: str


class CambiarPassword(BaseModel):
    password_actual: str
    password_nueva: str = Field(min_length=8, max_length=128)
