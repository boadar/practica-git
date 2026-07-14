"""Detective 2 de Farmatodo — busca la clave Algolia, el indice y rutas de API.

Sabemos que Farmatodo usa Algolia (app id: vcojeyd2po) y una API propia
(api-search.farmatodo.com). Falta la clave de busqueda de Algolia y el nombre
del indice de productos. Este script los extrae del JavaScript del sitio.

USO:
    python descubrir2.py
"""
import re
import ssl
import urllib.request

BASE = "https://www.farmatodo.com.ve"
_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile Safari/605.1.15"
)


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(
        req, timeout=45, context=ssl.create_default_context()
    ) as r:
        return r.read().decode("utf-8", "replace")


def absol(u):
    if u.startswith("http"):
        return u
    if u.startswith("//"):
        return "https:" + u
    if u.startswith("/"):
        return BASE + u
    return BASE + "/" + u


def main():
    print("Descargando Farmatodo...")
    home = get(BASE + "/")
    bundles = [absol(s) for s in re.findall(r'<script[^>]+src="([^"]+\.js[^"]*)"', home)]
    principales = [
        b for b in bundles
        if any(k in b.lower() for k in ("main", "scripts", "runtime", "vendor"))
    ][:5]

    fuentes = [home]
    for b in principales:
        try:
            fuentes.append(get(b))
        except Exception:
            pass

    claves, indices, ventanas, prod_strings = set(), set(), set(), set()
    for txt in fuentes:
        # Claves Algolia: 32 hex cerca de la palabra "algolia".
        for m in re.finditer(r'algolia', txt, re.I):
            win = txt[max(0, m.start() - 100): m.start() + 250]
            for k in re.findall(r'[a-f0-9]{32}', win):
                claves.add(k)
        # Claves por header/propiedad explicita.
        for m in re.finditer(
            r'(?:api[_-]?key|x-algolia-api-key|apiKey)["\']?\s*[:=]\s*'
            r'["\']([A-Za-z0-9=+/_-]{20,})["\']',
            txt, re.I,
        ):
            claves.add(m.group(1))
        # Nombres de indice.
        for m in re.findall(
            r'(?:indexName\s*[:=]\s*|initIndex\s*\(\s*|index\s*[:=]\s*)'
            r'["\']([A-Za-z0-9_\-]{3,})["\']',
            txt,
        ):
            indices.add(m)
        # Strings cortos con "product" o "prod_" (posibles indices/rutas).
        for m in re.findall(r'["\']([A-Za-z0-9_\-]*prod[A-Za-z0-9_\-]*)["\']', txt):
            if 3 <= len(m) <= 40:
                prod_strings.add(m)
        # Contexto alrededor de api-search.farmatodo.com.
        for m in re.finditer(r'api-search\.farmatodo\.com', txt):
            ventanas.add(txt[m.start(): m.start() + 100])

    print("\n=== CLAVES ALGOLIA candidatas (copiamelas) ===")
    for c in sorted(claves)[:12]:
        print("  ", c)
    print("\n=== INDICES candidatos ===")
    for c in sorted(indices)[:40]:
        print("  ", c)
    print("\n=== Strings con 'prod' ===")
    for c in sorted(prod_strings)[:40]:
        print("  ", c)
    print("\n=== Rutas api-search ===")
    for c in sorted(ventanas)[:12]:
        print("  ", c)


if __name__ == "__main__":
    main()
