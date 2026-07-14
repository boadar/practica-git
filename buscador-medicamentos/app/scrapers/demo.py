"""Scraper de demostracion (datos ficticios, sin red).

Sirve para probar la app de punta a punta antes de conectar sitios reales.
Muestra el patron a seguir: recibir una consulta y devolver ``Resultado``.
Cuando agreguemos sitios reales, este scraper se puede deshabilitar poniendo
``habilitado = False``.
"""
from __future__ import annotations

import httpx

from ..models import Resultado
from .base import BaseScraper

# Catalogo ficticio: (nombre, presentacion, precio, moneda)
_CATALOGO = [
    ("Paracetamol 500mg", "Tabletas x 20", 12.50, "BOB"),
    ("Paracetamol 500mg", "Jarabe 120ml", 2.10, "USD"),
    ("Ibuprofeno 400mg", "Tabletas x 10", 18.00, "BOB"),
    ("Amoxicilina 500mg", "Capsulas x 21", 45.00, "BOB"),
    ("Amoxicilina 500mg", "Suspension 250mg", 6.50, "USD"),
    ("Loratadina 10mg", "Tabletas x 10", 15.00, "BOB"),
    ("Omeprazol 20mg", "Capsulas x 14", 22.00, "BOB"),
    ("Vitamina C 1g", "Efervescente x 10", 3.20, "USD"),
]


class DemoScraper(BaseScraper):
    nombre = "Farmacia Demo"
    moneda_por_defecto = "BOB"
    # Deshabilitado: ya tenemos un sitio real (Locatel). Pon True para volver
    # a probar la app con datos ficticios de ejemplo.
    habilitado = False

    async def buscar(
        self, consulta: str, cliente: httpx.AsyncClient, limite: int
    ) -> list[Resultado]:
        q = consulta.lower().strip()
        encontrados: list[Resultado] = []
        for nombre, presentacion, precio, moneda in _CATALOGO:
            if q in nombre.lower():
                encontrados.append(
                    Resultado(
                        nombre=nombre,
                        precio=precio,
                        moneda=moneda,
                        fuente=self.nombre,
                        presentacion=presentacion,
                        url="https://example.com/demo",
                    )
                )
            if len(encontrados) >= limite:
                break
        return encontrados
