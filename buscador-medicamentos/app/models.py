"""Modelos de datos compartidos por scrapers y API."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class Resultado(BaseModel):
    """Un medicamento encontrado en un sitio, con su precio."""

    nombre: str
    # Precio tal cual aparece en el sitio.
    precio: float
    # Moneda original del precio: "BOB" (Bs.) o "USD" (Dolares REF).
    moneda: str
    # Nombre del sitio de donde proviene el resultado.
    fuente: str
    # URL del producto (para abrir la pagina original).
    url: Optional[str] = None
    # Presentacion o descripcion corta (ej. "Tabletas 500mg x 20").
    presentacion: Optional[str] = None
    # URL de imagen del producto, si el sitio la ofrece.
    imagen: Optional[str] = None

    # Campos calculados al normalizar (ver currency.py).
    precio_bs: Optional[float] = None
    precio_usd: Optional[float] = None
    # Precio en la moneda comun configurada, usado para ordenar/comparar.
    precio_comparacion: Optional[float] = None


class RespuestaBusqueda(BaseModel):
    """Respuesta del endpoint de busqueda."""

    consulta: str
    moneda_comun: str
    tasa_bs_por_usd: float
    total: int
    resultados: list[Resultado]
    # Sitios que fallaron durante la busqueda (nombre -> motivo).
    errores: dict[str, str] = {}
