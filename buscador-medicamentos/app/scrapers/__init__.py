"""Registro de scrapers.

Importa aqui cada modulo de sitio para que se registre automaticamente.
Al agregar un sitio nuevo, agrega su import en la lista de abajo.
"""
from . import demo  # noqa: F401  scraper de demostracion (deshabilitado)
from . import locatel  # noqa: F401  Locatel Venezuela

# Cuando agreguemos mas sitios reales, se importan aqui, por ejemplo:
# from . import farmatodo  # noqa: F401

from .base import scrapers_disponibles  # noqa: E402,F401
