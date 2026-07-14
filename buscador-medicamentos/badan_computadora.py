"""Buscador de Farmacia Badan — para COMPUTADORA (Mac/PC), no para iPad.

Badan usa Cloudflare y solo se puede leer con un navegador real. Este script
usa Playwright (un navegador automatico) que SI pasa ese guardia.

INSTALACION (una sola vez, en una computadora con Python):
    pip install playwright
    playwright install chromium

USO:
    python badan_computadora.py paracetamol

Se abrira una ventana de navegador que carga Badan y luego se cierra sola;
los resultados salen en la terminal.
"""
import asyncio
import html as _html
import re
import sys
import urllib.parse

BASE = "https://farmaciabadan.com"
_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


def _limpiar(t):
    return re.sub(r"\s+", " ", _html.unescape(t)).strip()


def _parsear(html):
    filas = []
    for b in html.split("product-item-info")[1:41]:
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
    return filas


async def buscar(consulta):
    from playwright.async_api import async_playwright

    url = BASE + "/catalogsearch/result/?q=" + urllib.parse.quote(consulta)
    async with async_playwright() as p:
        navegador = await p.chromium.launch(headless=False)
        contexto = await navegador.new_context(user_agent=_UA, locale="es-VE")
        pagina = await contexto.new_page()
        await pagina.goto(url, wait_until="domcontentloaded", timeout=60000)
        # Esperar a que Cloudflare pase y aparezcan los productos.
        try:
            await pagina.wait_for_selector(".product-item-info", timeout=45000)
        except Exception:
            pass  # quiza no hay resultados; igual leemos la pagina
        html = await pagina.content()
        await navegador.close()
    return html


def main():
    consulta = " ".join(sys.argv[1:]).strip() or "paracetamol"
    print("\nBuscando '%s' en Farmacia Badan (abriendo navegador)...\n" % consulta)

    try:
        html = asyncio.run(buscar(consulta))
    except ImportError:
        print("Falta Playwright. Instalalo con:")
        print("    pip install playwright")
        print("    playwright install chromium")
        return
    except Exception as e:
        print("ERROR: %s" % e)
        return

    filas = _parsear(html)
    if not filas:
        if "Just a moment" in html:
            print("Cloudflare no dejo pasar ni con navegador. Reintenta en un momento.")
        else:
            print("No encontre productos.")
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
