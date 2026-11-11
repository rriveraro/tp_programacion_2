"""Configuración del proyecto.

Los valores se leen de variables de entorno o del archivo .env.
Los valores por defecto son solo para desarrollo local.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8', extra='ignore'
    )

    # Seguridad (en producción se define por variable de entorno .env)
    SECRET_KEY: str = 'solo-para-desarrollo-cambiar-en-el-.env'
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()