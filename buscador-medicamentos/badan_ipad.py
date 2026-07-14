"""Buscador de medicamentos en Farmacia Badan — via servicio anti-Cloudflare.

Farmacia Badan usa Cloudflare, que bloquea a Python. Para sortearlo usamos
un servicio (ScraperAPI) que carga la pagina con un navegador real en sus
servidores y nos devuelve el HTML ya listo.

REQUISITO: una clave (API key) gratuita de https://www.scraperapi.com
Guarda tu clave en un archivo llamado apikey.txt (misma carpeta):
    pbpaste > apikey.txt      (despues de copiar tu clave)

USO:
    python badan.py paracetamol
"""
import html as _html
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://farmaciabadan.com"


def leer_clave():
    try:
        with open("apikey.txt") as f:
            return f.read().strip()
    except Exception:
        return ""


def pedir_via_servicio(target, clave, intentos=2):
    """Pide la pagina via ScraperAPI en modo potente (ultra_premium + render),
    el mas capaz de superar Cloudflare. Reintenta una vez si hay error 5xx."""
    api = "https://api.scraperapi.com/?" + urllib.parse.urlencode(
        {
            "api_key": clave,
            "url": target,
            "render": "true",
            "ultra_premium": "true",
        }
    )
    req = urllib.request.Request(api, headers={"User-Agent": "buscador-medicamentos"})
    for i in range(intentos):
        try:
            with urllib.request.urlopen(
                req, timeout=140, context=ssl.create_default_context()
            ) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code >= 500 and i < intentos - 1:
                continue  # error temporal del servicio: reintentar
            raise


def _limpiar(t):
    return re.sub(r"\s+", " ", _html.unescape(t)).strip()


def buscar(consulta, clave):
    q = urllib.parse.quote(consulta)
    target = BASE + "/catalogsearch/result/?q=" + q
    html = pedir_via_servicio(target, clave)

    bloques = html.split("product-item-info")[1:]
    filas = []
    for b in bloques[:40]:
        m_nom = re.search(r'product-item-link[^>]*>\s*([^<]+?)\s*<', b)
        if not m_nom:
            continue
        nombre = _limpiar(m_nom.group(1))
        m_p = re.search(
            r'data-price-amount="([\d.]+)"[^>]*data-price-type="finalPrice"', b
        ) or re.search(r'data-price-amount="([\d.]+)"', b)
        precio = float(m_p.group(1)) if m_p else None
        m_v = re.search(r'class=["\']?price["\']?\s*>\s*([^<]+?)\s*<', b)
        visible = _limpiar(m_v.group(1)) if m_v else ""
        m_l = re.search(r'product-item-link"\s+href="([^"]+)"', b)
        link = m_l.group(1) if m_l else ""
        filas.append((nombre, precio, visible, link))
    return html, filas


def main():
    clave = leer_clave()
    if not clave:
        print("Falta tu clave de ScraperAPI.")
        print("1) Crea una cuenta gratis en https://www.scraperapi.com")
        print("2) Copia tu API key")
        print("3) En a-Shell:  pbpaste > apikey.txt")
        print("4) Vuelve a correr:  python badan.py paracetamol")
        return

    consulta = " ".join(sys.argv[1:]).strip() or "paracetamol"
    print("\nBuscando '%s' en Farmacia Badan (via servicio)...\n" % consulta)
    print("(Puede tardar 20-60 segundos, ten paciencia.)\n")

    try:
        html, filas = buscar(consulta, clave)
    except urllib.error.HTTPError as e:
        print("El servicio respondio: HTTP %s" % e.code)
        if e.code == 401:
            print("La clave parece invalida. Revisa apikey.txt.")
        elif e.code in (403, 429):
            print("Puede que se acabaron los creditos gratis del mes.")
        try:
            print("Detalle:", _limpiar(e.read().decode("utf-8", "replace")[:200]))
        except Exception:
            pass
        return
    except Exception as e:
        print("ERROR: %s" % e)
        return

    if "Just a moment" in html or "cf-browser-verification" in html:
        print("Cloudflare todavia bloqueo. Con el plan gratis a veces pasa.")
        print("Prueba agregando mas potencia: dime y activamos la opcion 'premium'.")
        return

    if not filas:
        print("Se leyo la pagina pero no encontre productos.")
        print("  data-price-amount presente:", "data-price-amount" in html)
        print("  tamano html:", len(html))
        return

    print("%d producto(s):\n" % len(filas))
    for i, (nombre, precio, visible, link) in enumerate(filas, 1):
        print("%2d. %s" % (i, nombre))
        if visible:
            print("     Precio mostrado: %s" % visible)
        if precio is not None:
            print("     Precio (numero): %s" % precio)
        if link:
            print("     %s" % (link if link.startswith("http") else BASE + link))
        print("")
    print("Dime: los precios estan en Bs. o en $ (REF)?")


if __name__ == "__main__":
    main()
