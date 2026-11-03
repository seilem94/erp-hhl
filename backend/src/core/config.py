"""Configuración central de la aplicación via pydantic-settings.

Lee variables de entorno (y opcionalmente de un archivo .env)
y las expone con tipado estricto a través de la instancia ``settings``.
"""

from __future__ import annotations

from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración principal del backend.

    Las variables son cargadas desde el entorno o desde el archivo ``.env``
    ubicado en la raíz del directorio ``backend/``.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------------------ #
    # Base de datos                                                         #
    # ------------------------------------------------------------------ #
    DATABASE_URL: PostgresDsn

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def _validate_database_url(cls, v: object) -> object:
        """Rechaza URLs vacías o no-string de forma temprana."""
        if isinstance(v, str) and not v.strip():
            msg = "DATABASE_URL no puede estar vacía."
            raise ValueError(msg)
        return v


# Instancia global — importar desde aquí en el resto del proyecto.
settings = Settings()
