"""Buscador de medicamentos en Farmatodo — via Algolia (para iPad, a-Shell).

Farmatodo busca con Algolia. Datos descubiertos del sitio:
    App id:  vcojeyd2po
    Clave:   869a91e98550dd668b8b1dc04bca9011  (clave publica de busqueda)
    Indices: products-vzla / products-venezuela / products

Este script consulta Algolia, detecta el indice correcto y muestra los
productos. Ademas imprime los CAMPOS del primer resultado, para afinar
que campo es el nombre y cual el precio.

USO:
    python farmatodo.py paracetamol
"""
import json
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request

APP = "vcojeyd2po"
KEY = "869a91e98550dd668b8b1dc04bca9011"
INDICES = ["products-vzla", "products-venezuela", "products", "prod-vzla"]
TASA_BS_POR_USD = 720.0


def algolia(index, consulta):
    url = "https://%s-dsn.algolia.net/1/indexes/%s/query" % (APP, index)
    cuerpo = json.dumps(
        {"params": urllib.parse.urlencode({"query": consulta, "hitsPerPage": 24})}
    ).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=cuerpo,
        method="POST",
        headers={
            "X-Algolia-Application-Id": APP,
            "X-Algolia-API-Key": KEY,
            "Content-Type": "application/json",
            "User-Agent": "buscador-medicamentos",
        },
    )
    with urllib.request.urlopen(
        req, timeout=30, context=ssl.create_default_context()
    ) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def campo(h, nombres):
    for n in nombres:
        v = h.get(n)
        if v not in (None, "", [], {}):
            return v
    return None


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
    print("\nBuscando '%s' en Farmatodo (Algolia)...\n" % consulta)

    hits, usado = None, None
    for idx in INDICES:
        try:
            data = algolia(idx, consulta)
            n = data.get("nbHits", 0)
            print("  indice '%s': %s resultados" % (idx, n))
            if n and data.get("hits"):
                hits, usado = data["hits"], idx
                break
        except urllib.error.HTTPError as e:
            print("  indice '%s': HTTP %s" % (idx, e.code))
        except Exception as e:
            print("  indice '%s': %s" % (idx, type(e).__name__))

    if not hits:
        print("\nNo hubo resultados en ningun indice. Copiame lo de arriba.")
        return

    print("\nUsando indice: %s\n" % usado)

    # Esquema del primer producto (para afinar nombre/precio).
    print("=== CAMPOS del primer producto (copiamelos) ===")
    for k in sorted(hits[0].keys()):
        s = str(hits[0][k])
        if len(s) > 70:
            s = s[:70] + "..."
        print("   %s = %s" % (k, s))
    print("")

    # Extraccion best-effort (por si los campos son los tipicos).
    filas = []
    for h in hits:
        nombre = campo(h, ["name", "productName", "fullName", "description", "title", "nombre"])
        precio = campo(h, ["price", "finalPrice", "fullPrice", "sellPrice", "precio",
                           "priceWithDiscount", "offerPrice", "salePrice"])
        marca = campo(h, ["brand", "marca", "laboratory", "laboratorio", "manufacturer"])
        try:
            precio = float(precio) if precio is not None else None
        except Exception:
            precio = None
        if nombre:
            filas.append((str(nombre), marca, precio))

    filas.sort(key=lambda f: (f[2] is None, f[2] if f[2] is not None else 0))
    print("=== %d PRODUCTOS (del mas barato al mas caro) ===\n" % len(filas))
    for i, (nombre, marca, precio) in enumerate(filas, 1):
        print("%2d.%s %s" % (i, " *" if i == 1 else "", nombre))
        if marca:
            print("     Marca: %s" % marca)
        if precio is not None:
            print("     Bs. %s   (~$%.2f)" % (bs(precio), precio / TASA_BS_POR_USD))
        else:
            print("     (precio: ver campos de arriba)")
        print("")


if __name__ == "__main__":
    main()
