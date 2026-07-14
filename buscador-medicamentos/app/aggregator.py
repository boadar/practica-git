"""Agregador: corre todos los scrapers en paralelo y unifica resultados."""
from __future__ import annotations

import asyncio

import httpx

from .config import Config
from .currency import enriquecer
from .models import RespuestaBusqueda, Resultado
from .scrapers import scrapers_disponibles

# User-Agent de navegador para reducir bloqueos simples.
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}


async def buscar_en_todos(consulta: str, cfg: Config) -> RespuestaBusqueda:
    """Busca ``consulta`` en todos los sitios habilitados y devuelve la
    respuesta ordenada por precio (en la moneda comun configurada)."""
    scrapers = scrapers_disponibles()
    errores: dict[str, str] = {}
    todos: list[Resultado] = []

    async with httpx.AsyncClient(
        headers=_HEADERS,
        timeout=cfg.timeout_segundos,
        follow_redirects=True,
    ) as cliente:

        async def _correr(scraper) -> list[Resultado]:
            try:
                return await scraper.buscar(
                    consulta, cliente, cfg.max_resultados_por_sitio
                )
            except Exception as exc:  # noqa: BLE001 - reportamos, no rompemos
                errores[scraper.nombre] = f"{type(exc).__name__}: {exc}"
                return []

        listas = await asyncio.gather(*(_correr(s) for s in scrapers))

    for lista in listas:
        for r in lista:
            todos.append(enriquecer(r, cfg))

    # Orden ascendente por precio de comparacion (mas barato primero).
    todos.sort(key=lambda r: (r.precio_comparacion is None, r.precio_comparacion))

    return RespuestaBusqueda(
        consulta=consulta,
        moneda_comun=cfg.moneda_comun,
        tasa_bs_por_usd=cfg.tasa_bs_por_usd,
        total=len(todos),
        resultados=todos,
        errores=errores,
    )
