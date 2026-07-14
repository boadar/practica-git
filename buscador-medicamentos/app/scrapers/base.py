"""Clase base y registro de scrapers.

Cada sitio web se implementa como una subclase de :class:`BaseScraper`.
Al importarse, las subclases se registran solas para que el agregador las
descubra. Para agregar un sitio nuevo basta con crear un archivo en
``app/scrapers/`` con una subclase y agregar su ``import`` en
``app/scrapers/__init__.py``.
"""
from __future__ import annotations

import abc

import httpx

from ..models import Resultado

# Registro global de scrapers disponibles (se llena via __init_subclass__).
REGISTRO: list[type["BaseScraper"]] = []


class BaseScraper(abc.ABC):
    """Contrato que debe cumplir cada sitio soportado."""

    # Nombre legible del sitio (se muestra en los resultados).
    nombre: str = "sitio-desconocido"
    # Moneda por defecto del sitio: "BOB" (Bs.) o "USD" (REF).
    moneda_por_defecto: str = "BOB"
    # Si es False, el agregador lo ignora (util para deshabilitar temporalmente).
    habilitado: bool = True

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        # No registramos scrapers "abstractos" auxiliares.
        if getattr(cls, "nombre", None) and cls.nombre != "sitio-desconocido":
            REGISTRO.append(cls)

    @abc.abstractmethod
    async def buscar(
        self, consulta: str, cliente: httpx.AsyncClient, limite: int
    ) -> list[Resultado]:
        """Busca ``consulta`` en el sitio y devuelve una lista de resultados."""
        raise NotImplementedError


def scrapers_disponibles() -> list["BaseScraper"]:
    """Instancia todos los scrapers habilitados del registro."""
    return [cls() for cls in REGISTRO if cls.habilitado]
