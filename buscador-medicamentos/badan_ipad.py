"""Buscador de medicamentos en Farmacia Badan — version LIGERA para iPad.

No necesita instalar nada (solo la libreria estandar de Python).
Farmacia Badan parece estar hecha con Magento, que entrega los precios
dentro del HTML de la pagina.

USO:
    python badan.py paracetamol

Esta version, ademas de buscar, muestra un pequeno diagnostico si no logra
leer los precios, para poder ajustarla.
"""
import html as _html
import re
import ssl
import sys
import urllib.parse
import urllib.request

BASE = "https://farmaciabadan.com"
_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile Safari/605.1.15"
)


def pedir(url):
    req = urllib.request.Request(
        url, headers={"User-Agent": _UA, "Accept": "text/html,application/xhtml+xml"}
    )
    with urllib.request.urlopen(
        req, timeout=30, context=ssl.create_default_context()
    ) as r:
        return r.read().decode("utf-8", "replace")


def _limpiar(t):
    # Decodifica entidades (&nbsp;, &reg;, etc.) y normaliza espacios.
    return re.sub(r"\s+", " ", _html.unescape(t)).strip()


def buscar(consulta):
    """Devuelve (html, filas). Cada fila: (nombre, precio_num, precio_visible, link)."""
    q = urllib.parse.quote(consulta)
    html = pedir(BASE + "/catalogsearch/result/?q=" + q)

    # En Magento, cada producto va dentro de un bloque "product-item-info".
    bloques = html.split("product-item-info")[1:]
    filas = []
    for b in bloques[:40]:
        m_nom = re.search(r'product-item-link[^>]*>\s*([^<]+?)\s*<', b)
        if not m_nom:
            continue
        nombre = _limpiar(m_nom.group(1))

        # Precio numerico (Magento lo pone en data-price-amount).
        m_p = re.search(
            r'data-price-amount="([\d.]+)"[^>]*data-price-type="finalPrice"', b
        ) or re.search(r'data-price-amount="([\d.]+)"', b)
        precio = float(m_p.group(1)) if m_p else None

        # Precio visible (texto), para saber la moneda (Bs. o $).
        m_v = re.search(r'class=["\']?price["\']?\s*>\s*([^<]+?)\s*<', b)
        visible = _limpiar(m_v.group(1)) if m_v else ""

        # Enlace al producto.
        m_l = re.search(r'product-item-link"\s+href="([^"]+)"', b)
        link = m_l.group(1) if m_l else ""

        filas.append((nombre, precio, visible, link))
    return html, filas


def main():
    consulta = " ".join(sys.argv[1:]).strip() or "paracetamol"
    print("\nBuscando '%s' en Farmacia Badan...\n" % consulta)

    try:
        html, filas = buscar(consulta)
    except Exception as e:
        print("ERROR al conectar: %s" % e)
        print("Copiame este mensaje.")
        return

    if not filas:
        print("No pude leer productos con el metodo esperado.")
        print("DIAGNOSTICO (copiame estas lineas):")
        print("  product-item-link presente:", "product-item-link" in html)
        print("  data-price-amount presente:", "data-price-amount" in html)
        pide_login = "customer/account/login" in html or "Iniciar sesión" in html
        print("  parece pedir login:", pide_login)
        print("  tamano del html:", len(html))
        t = re.search(r"<title>([^<]*)</title>", html)
        if t:
            print("  titulo:", _limpiar(t.group(1)))
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

    print("Dime: los precios estan en Bs. o en $ (REF)? Con eso lo termino.")


if __name__ == "__main__":
    main()
