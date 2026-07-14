"""Scraper para Locatel Venezuela (https://www.locatel.com.ve).

Locatel es una tienda tipo SPA. Los productos NO vienen en el HTML inicial:
se cargan por una API interna. Este scraper consulta esa API (formato VTEX,
que es el mas comun en tiendas de este tipo) y devuelve los productos.

En la web, cada producto muestra:
  - Marca (ej. DISTRILAB)
  - Nombre (ej. DISTRILAB PARACETAMOL DLAB 1GR 100 ML)
  - COD: codigo interno
  - Precio en Bs. (Bolivares)  <- lo tomamos como precio principal
  - REF: precio de referencia en USD

Nota: el precio principal se guarda en Bs. (BOB). El USD se calcula con la
tasa configurable en config.json. Mas adelante se puede capturar el "REF"
exacto que muestra el sitio.
"""
from __future__ import annotations

from urllib.parse import quote

import httpx

from ..models import Resultado
from .base import BaseScraper

_ACCEPT_JSON = {"Accept": "application/json, text/plain, */*"}


class LocatelScraper(BaseScraper):
    nombre = "Locatel"
    moneda_por_defecto = "BOB"  # el precio principal del sitio esta en Bs.
    habilitado = True

    BASE = "https://www.locatel.com.ve"

    async def buscar(
        self, consulta: str, cliente: httpx.AsyncClient, limite: int
    ) -> list[Resultado]:
        # 1) Intentamos la API "legacy" de catalogo (la mas simple y comun).
        try:
            resultados = await self._buscar_legacy(consulta, cliente, limite)
            if resultados:
                return resultados
        except httpx.HTTPStatusError:
            pass  # probamos el siguiente metodo

        # 2) Fallback: API de Intelligent Search (VTEX mas nuevo).
        return await self._buscar_intelligent(consulta, cliente, limite)

    # ------------------------------------------------------------------ #
    # Metodo 1: /api/catalog_system/pub/products/search
    # ------------------------------------------------------------------ #
    async def _buscar_legacy(
        self, consulta: str, cliente: httpx.AsyncClient, limite: int
    ) -> list[Resultado]:
        url = f"{self.BASE}/api/catalog_system/pub/products/search/{quote(consulta)}"
        resp = await cliente.get(
            url,
            params={"_from": 0, "_to": max(0, limite - 1)},
            headers=_ACCEPT_JSON,
        )
        resp.raise_for_status()
        productos = resp.json()  # lista de productos
        salida: list[Resultado] = []
        for p in productos:
            r = self._desde_producto_vtex(p)
            if r:
                salida.append(r)
        return salida

    # ------------------------------------------------------------------ #
    # Metodo 2: /api/io/_v/api/intelligent-search/product_search
    # ------------------------------------------------------------------ #
    async def _buscar_intelligent(
        self, consulta: str, cliente: httpx.AsyncClient, limite: int
    ) -> list[Resultado]:
        url = f"{self.BASE}/api/io/_v/api/intelligent-search/product_search/*"
        resp = await cliente.get(
            url,
            params={"query": consulta, "count": limite, "locale": "es-VE"},
            headers=_ACCEPT_JSON,
        )
        resp.raise_for_status()
        datos = resp.json()
        productos = datos.get("products", []) if isinstance(datos, dict) else []
        salida: list[Resultado] = []
        for p in productos:
            r = self._desde_producto_vtex(p)
            if r:
                salida.append(r)
        return salida

    # ------------------------------------------------------------------ #
    # Parseo comun de un producto en formato VTEX
    # ------------------------------------------------------------------ #
    def _desde_producto_vtex(self, p: dict) -> Resultado | None:
        nombre = p.get("productName") or p.get("productTitle")
        if not nombre:
            return None
        marca = p.get("brand")

        items = p.get("items") or []
        precio = None
        imagen = None
        if items:
            item0 = items[0]
            imagenes = item0.get("images") or []
            if imagenes:
                imagen = imagenes[0].get("imageUrl")
            sellers = item0.get("sellers") or []
            if sellers:
                oferta = sellers[0].get("commertialOffer") or {}
                precio = oferta.get("Price") or oferta.get("spotPrice")

        # Intelligent Search a veces trae el precio en priceRange.
        if precio is None:
            rango = (p.get("priceRange") or {}).get("sellingPrice") or {}
            precio = rango.get("lowPrice")

        if not precio:
            return None

        # Enlace absoluto al producto.
        link = p.get("link")
        if not link:
            slug = p.get("linkText")
            link = f"{self.BASE}/{slug}/p" if slug else None
        elif link.startswith("/"):
            link = self.BASE + link

        return Resultado(
            nombre=nombre.strip(),
            precio=float(precio),
            moneda=self.moneda_por_defecto,
            fuente=self.nombre,
            presentacion=f"Marca: {marca}" if marca else None,
            url=link,
            imagen=imagen,
        )
