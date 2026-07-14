"""Detective de la API de Farmatodo — para iPad (a-Shell), sin instalar nada.

Farmatodo es una app Angular: su codigo JavaScript contiene la direccion de
la API que usa para buscar productos. Este script descarga la pagina y sus
archivos .js principales, y extrae las direcciones de API candidatas.

USO:
    python descubrir.py

Copia y pegame la lista de "CANDIDATOS" que imprima.
"""
import re
import ssl
import urllib.request

BASE = "https://www.farmatodo.com.ve"
_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile Safari/605.1.15"
)
_CLAVES = ("api", "search", "product", "graphql", "algolia", "catalog", "service", "ws")


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
    print("Descargando la pagina de Farmatodo...")
    try:
        home = get(BASE + "/")
    except Exception as e:
        print("ERROR al abrir la pagina: %s" % e)
        return

    scripts = re.findall(r'<script[^>]+src="([^"]+\.js[^"]*)"', home)
    bundles = [absol(s) for s in scripts]
    # Priorizamos los archivos principales de Angular.
    principales = [
        b for b in bundles
        if any(k in b.lower() for k in ("main", "scripts", "runtime", "vendor"))
    ][:4]

    print("Archivos JS encontrados: %d (revisando %d principales)\n"
          % (len(bundles), len(principales)))

    fuentes = [home]
    for b in principales:
        try:
            fuentes.append(get(b))
        except Exception:
            pass

    candidatos = set()
    algolia = set()
    for txt in fuentes:
        for m in re.findall(r'https?://[A-Za-z0-9._\-]+(?:/[A-Za-z0-9._\-/]*)?', txt):
            low = m.lower()
            if "farmatodo.com.ve/categorias" in low or low.endswith(".js"):
                continue
            if any(k in low for k in _CLAVES):
                candidatos.add(m)
        for m in re.findall(
            r'(?:applicationId|appId|algoliaId)["\']?\s*[:=]\s*["\']([A-Z0-9]{6,})["\']',
            txt,
        ):
            algolia.add(m)

    print("CANDIDATOS DE API (copiamelos todos):")
    if candidatos:
        for c in sorted(candidatos)[:60]:
            print("  ", c)
    else:
        print("   (ninguno claro)")
    if algolia:
        print("\nPosible Algolia appId:", ", ".join(sorted(algolia)[:5]))

    print("\n(Si la lista sale vacia, pegame estas primeras lineas:)")
    print(home[:200])


if __name__ == "__main__":
    main()
