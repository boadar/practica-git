"""Registro de scrapers.

Importa aqui cada modulo de sitio para que se registre automaticamente.
Al agregar un sitio nuevo, agrega su import en la lista de abajo.
"""
from . import demo  # noqa: F401  scraper de demostracion

# Cuando agreguemos sitios reales, se importan aqui, por ejemplo:
# from . import mi_sitio  # noqa: F401

from .base import scrapers_disponibles  # noqa: E402,F401
