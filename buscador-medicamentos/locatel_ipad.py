"""Buscador de medicamentos en Locatel — version LIGERA para iPad (a-Shell).

No necesita instalar NADA: usa solo lo que Python ya trae.
Funciona en a-Shell (la app gratuita de terminal para iPad/iPhone).

USO:
    python locatel_ipad.py paracetamol
    python locatel_ipad.py "vitamina c"

Muestra los productos ordenados del mas barato al mas caro, con su
precio en Bs. y un estimado en USD.
"""
import json
import ssl
import sys
import urllib.parse
import urllib.request

# Cuantos Bs. equivale 1 USD. Ajustalo al valor del dia.
# (En la web de Locatel, el numero "REF" es el USD exacto.)
TASA_BS_POR_USD = 720.0

BASE = "https://www.locatel.com.ve"
_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile Safari/605.1.15"
)


def _pedir_json(url):
    """Descarga una URL y devuelve el JSON. Lanza error con mensaje claro."""
    req = urllib.request.Request(
        url, headers={"User-Agent": _UA, "Accept": "application/json, */*"}
    )
    contexto = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=25, context=contexto) as resp:
        datos = resp.read().decode("utf-8", "replace")
    return json.loads(datos)


def _producto_a_fila(p):
    """Convierte un producto (formato VTEX) en (nombre, marca, precio_bs, link)."""
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
        rango = (p.get("priceRange") or {}).get("sellingPrice") or {}
        precio = rango.get("lowPrice")
    if not precio:
        return None

    link = p.get("link") or ""
    if not link and p.get("linkText"):
        link = BASE + "/" + p["linkText"] + "/p"
    elif link.startswith("/"):
        link = BASE + link

    return (nombre.strip(), marca, float(precio), link)


def buscar(consulta):
    """Busca en Locatel y devuelve una lista de filas."""
    q = urllib.parse.quote(consulta)

    # Metodo 1: API de catalogo (la mas simple).
    url1 = BASE + "/api/catalog_system/pub/products/search/" + q + "?_from=0&_to=19"
    try:
        datos = _pedir_json(url1)
        if isinstance(datos, list) and datos:
            filas = [_producto_a_fila(p) for p in datos]
            filas = [f for f in filas if f]
            if filas:
                return filas
    except Exception as e:
        print("(Aviso: metodo 1 no funciono: %s)" % e)

    # Metodo 2: API de busqueda inteligente.
    url2 = (
        BASE
        + "/api/io/_v/api/intelligent-search/product_search/*?query="
        + q
        + "&count=20&locale=es-VE"
    )
    datos = _pedir_json(url2)
    productos = datos.get("products", []) if isinstance(datos, dict) else []
    filas = [_producto_a_fila(p) for p in productos]
    return [f for f in filas if f]


def bs(n):
    """Formatea un numero como Bs. con separador de miles (estilo Venezuela)."""
    entero, dec = ("%.2f" % n).split(".")
    grupos = []
    while len(entero) > 3:
        grupos.insert(0, entero[-3:])
        entero = entero[:-3]
    grupos.insert(0, entero)
    return ".".join(grupos) + "," + dec


def main():
    consulta = " ".join(sys.argv[1:]).strip() or "paracetamol"
    print("\nBuscando '%s' en Locatel...\n" % consulta)

    try:
        filas = buscar(consulta)
    except Exception as e:
        print("ERROR al conectar con Locatel: %s" % e)
        print("Copiame este mensaje y lo reviso.")
        return

    if not filas:
        print("No se encontraron productos.")
        return

    # Ordenar del mas barato al mas caro.
    filas.sort(key=lambda f: f[2])

    print("%d producto(s), del mas barato al mas caro:\n" % len(filas))
    for i, (nombre, marca, precio, link) in enumerate(filas, 1):
        usd = precio / TASA_BS_POR_USD
        estrella = " *" if i == 1 else ""
        print("%2d.%s %s" % (i, estrella, nombre))
        if marca:
            print("     Marca: %s" % marca)
        print("     Bs. %s   (~$%.2f)" % (bs(precio), usd))
        if link:
            print("     %s" % link)
        print("")

    print("(* = mas barato.  USD estimado con tasa 1 USD = %s Bs.)" % bs(TASA_BS_POR_USD))


if __name__ == "__main__":
    main()
