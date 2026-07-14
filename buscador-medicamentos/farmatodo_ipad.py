"""Buscador de medicamentos en Farmatodo — version LIGERA para iPad (a-Shell).

No necesita instalar nada (solo la libreria estandar de Python).
Farmatodo es una SPA que carga los precios por una API interna. Este script
prueba las rutas de API mas comunes (formato VTEX, como Locatel) y, si no
lo logra, muestra un diagnostico para saber que tipo de bloqueo hay.

USO:
    python farmatodo.py paracetamol
"""
import json
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request

# Cuantos Bs. equivale 1 USD. Ajustalo al valor del dia.
TASA_BS_POR_USD = 720.0

BASE = "https://www.farmatodo.com.ve"
_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile Safari/605.1.15"
)


def _pedir(url):
    req = urllib.request.Request(
        url, headers={"User-Agent": _UA, "Accept": "application/json, text/plain, */*"}
    )
    with urllib.request.urlopen(
        req, timeout=30, context=ssl.create_default_context()
    ) as r:
        return r.read().decode("utf-8", "replace")


def _fila_vtex(p):
    """Convierte un producto VTEX en (nombre, marca, precio_bs, link)."""
    nombre = p.get("productName") or p.get("productTitle")
    if not nombre:
        return None
    marca = p.get("brand") or ""
    precio = None
    items = p.get("items") or []
    if items:
        vendedores = items[0].get("sellers") or []
        if vendedores:
            oferta = vendedores[0].get("commertialOffer") or {}
            precio = oferta.get("Price") or oferta.get("spotPrice")
    if precio is None:
        precio = ((p.get("priceRange") or {}).get("sellingPrice") or {}).get("lowPrice")
    if not precio:
        return None
    link = p.get("link") or ""
    if not link and p.get("linkText"):
        link = BASE + "/" + p["linkText"] + "/p"
    elif link.startswith("/"):
        link = BASE + link
    return (nombre.strip(), marca, float(precio), link)


def buscar(consulta):
    """Devuelve (filas, diagnostico). filas=[] si no logro leer productos."""
    q = urllib.parse.quote(consulta)
    diag = []

    intentos = [
        ("catalogo VTEX",
         BASE + "/api/catalog_system/pub/products/search/" + q + "?_from=0&_to=19"),
        ("intelligent-search",
         BASE + "/api/io/_v/api/intelligent-search/product_search/*?query="
         + q + "&count=20&locale=es-VE"),
    ]

    for nombre_metodo, url in intentos:
        try:
            texto = _pedir(url)
            datos = json.loads(texto)
            if isinstance(datos, dict):
                datos = datos.get("products", [])
            filas = [f for f in (_fila_vtex(p) for p in datos) if f]
            if filas:
                return filas, diag
            diag.append("%s: respondio pero sin productos" % nombre_metodo)
        except urllib.error.HTTPError as e:
            cuerpo = ""
            try:
                cuerpo = e.read().decode("utf-8", "replace")
            except Exception:
                pass
            cf = "cloudflare" in (e.headers.get("Server", "").lower()) or (
                "just a moment" in cuerpo.lower()
            )
            diag.append(
                "%s: HTTP %s%s"
                % (nombre_metodo, e.code, " (CLOUDFLARE)" if cf else "")
            )
        except Exception as e:
            diag.append("%s: %s" % (nombre_metodo, type(e).__name__))

    return [], diag


def bs(n):
    entero, dec = ("%.2f" % n).split(".")
    grupos = []
    while len(entero) > 3:
        grupos.insert(0, entero[-3:])
        entero = entero[:-3]
    grupos.insert(0, entero)
    return ".".join(grupos) + "," + dec


def main():
    consulta = " ".join(sys.argv[1:]).strip() or "paracetamol"
    print("\nBuscando '%s' en Farmatodo...\n" % consulta)

    filas, diag = buscar(consulta)

    if not filas:
        print("No pude leer productos. DIAGNOSTICO (copiamelo):")
        for d in diag:
            print("  -", d)
        return

    filas.sort(key=lambda f: f[2])
    print("%d producto(s), del mas barato al mas caro:\n" % len(filas))
    for i, (nombre, marca, precio, link) in enumerate(filas, 1):
        estrella = " *" if i == 1 else ""
        print("%2d.%s %s" % (i, estrella, nombre))
        if marca:
            print("     Marca: %s" % marca)
        print("     Bs. %s   (~$%.2f)" % (bs(precio), precio / TASA_BS_POR_USD))
        if link:
            print("     %s" % link)
        print("")
    print("(* = mas barato.  USD estimado con 1 USD = %s Bs.)" % bs(TASA_BS_POR_USD))


if __name__ == "__main__":
    main()
