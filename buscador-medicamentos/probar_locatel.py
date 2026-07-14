"""Prueba rapida SOLO del scraper de Locatel.

Uso:
    python probar_locatel.py paracetamol

Sirve para verificar que la conexion con Locatel funciona en TU maquina
(desde el entorno de desarrollo el sitio esta bloqueado). Imprime lo que
encuentra o el error, para poder ajustar el scraper si hace falta.
"""
from __future__ import annotations

import asyncio
import sys

import httpx

from app.scrapers.locatel import LocatelScraper

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}


async def main() -> None:
    consulta = " ".join(sys.argv[1:]) or "paracetamol"
    print(f"Buscando '{consulta}' en Locatel...\n")

    scraper = LocatelScraper()
    async with httpx.AsyncClient(
        headers=_HEADERS, timeout=20, follow_redirects=True
    ) as cliente:
        try:
            resultados = await scraper.buscar(consulta, cliente, limite=20)
        except Exception as exc:  # noqa: BLE001
            print(f"ERROR: {type(exc).__name__}: {exc}")
            return

    if not resultados:
        print("No se encontraron resultados (revisar la API del sitio).")
        return

    print(f"{len(resultados)} resultado(s):\n")
    for r in resultados:
        print(f"- {r.nombre}")
        print(f"    Precio: Bs. {r.precio}   ({r.presentacion or ''})")
        print(f"    Link:   {r.url}")


if __name__ == "__main__":
    asyncio.run(main())
