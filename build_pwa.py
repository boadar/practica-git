#!/usr/bin/env python3
"""
Regenera la versión PWA (GitHub Pages) a partir de la app principal.

Uso:  python3 build_pwa.py

- Lee  Pedidos_OFICA.html  (la app / artifact).
- Genera  docs/index.html  inyectando: manifest, apple-touch-icon,
  registro del service worker, y desactivando la inyección de manifest
  en tiempo de ejecución (pwaSetup) para no duplicarla.
- Sube la versión del caché en  docs/sw.js  (pedidos-ofica-vN -> vN+1)
  para que los dispositivos instalados reciban la nueva versión.

Ejecutar este script después de CADA cambio en Pedidos_OFICA.html,
luego commit + push para que GitHub Pages reconstruya.
"""
import re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "Pedidos_OFICA.html"
OUT = ROOT / "docs" / "index.html"
SW = ROOT / "docs" / "sw.js"

def main():
    src = SRC.read_text(encoding="utf-8")

    # 1) manifest + iconos en <head>
    head_inject = (
        '<link rel="manifest" href="./manifest.webmanifest">\n'
        '<link rel="apple-touch-icon" href="./icon-180.png">\n'
        '<link rel="icon" href="./icon-192.png">\n'
        '</head>'
    )
    if '<link rel="manifest"' not in src:
        if '</head>' not in src:
            sys.exit("ERROR: no se encontró </head> en Pedidos_OFICA.html")
        src = src.replace('</head>', head_inject, 1)

    # 2) evitar el manifest en tiempo de ejecución (usamos el estático)
    src = src.replace('wire(); pwaSetup();', 'wire();', 1)

    # 3) registro del service worker antes de </body>
    if 'serviceWorker' not in src:
        sw_reg = (
            '<script>\n'
            "if('serviceWorker' in navigator){\n"
            "  window.addEventListener('load',function(){\n"
            "    navigator.serviceWorker.register('./sw.js').catch(function(){});\n"
            '  });\n'
            '}\n'
            '</script>\n'
            '</body>'
        )
        if '</body>' not in src:
            sys.exit("ERROR: no se encontró </body> en Pedidos_OFICA.html")
        src = src.replace('</body>', sw_reg, 1)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(src, encoding="utf-8")

    # 4) subir versión del caché en sw.js
    sw = SW.read_text(encoding="utf-8")
    m = re.search(r"pedidos-ofica-v(\d+)", sw)
    if not m:
        sys.exit("ERROR: no se encontró la versión del caché en docs/sw.js")
    old = int(m.group(1))
    new = old + 1
    sw = sw.replace(f"pedidos-ofica-v{old}", f"pedidos-ofica-v{new}")
    SW.write_text(sw, encoding="utf-8")

    print(f"OK -> docs/index.html generado ({len(src)} bytes)")
    print(f"OK -> caché del service worker: v{old} -> v{new}")

if __name__ == "__main__":
    main()
