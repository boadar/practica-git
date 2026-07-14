# 💊 Buscador y comparador de precios de medicamentos

App para **buscar un medicamento en varios sitios web** y **comparar sus precios**.
Algunos sitios muestran precios en **Bs. (Bolivianos)** y otros en **Dólares (REF)**;
la app normaliza todo usando una **tasa de cambio configurable** y ordena del más
barato al más caro.

Corre **en local** y es accesible desde el **navegador** (en la misma máquina o
desde otros dispositivos de tu red local).

## Arquitectura

```
buscador-medicamentos/
├── app/
│   ├── main.py            # API FastAPI + sirve el frontend
│   ├── aggregator.py      # corre todos los scrapers en paralelo
│   ├── config.py          # carga config.json (tasa de cambio, etc.)
│   ├── currency.py        # convierte Bs. <-> USD para comparar
│   ├── models.py          # modelos de datos
│   ├── scrapers/
│   │   ├── base.py        # clase base + registro de sitios
│   │   ├── demo.py        # scraper de ejemplo (datos ficticios)
│   │   └── plantilla.py.txt  # plantilla para agregar un sitio real
│   └── static/            # frontend (HTML, CSS, JS)
├── config.example.json    # copia a config.json y ajusta
├── requirements.txt
└── run.py                 # arranque rápido
```

**Un scraper por sitio.** Cada página web se implementa como una subclase de
`BaseScraper` que se registra sola. Así podemos ir agregando sitios uno por uno.

## Instalación

```bash
cd buscador-medicamentos
python -m venv .venv
source .venv/bin/activate      # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp config.example.json config.json   # y ajusta la tasa de cambio
```

## Uso

```bash
python run.py
```

Abre <http://127.0.0.1:8000> en el navegador, escribe un medicamento (ej.
`Paracetamol`) y compara precios. Desde otro dispositivo de la red, usa la IP
de tu máquina, ej. `http://192.168.x.x:8000`.

### API

- `GET /api/buscar?q=paracetamol` — busca y devuelve resultados comparados (JSON).
- `GET /api/salud` — estado y configuración activa.

## Configuración (`config.json`)

| Campo | Descripción |
|-------|-------------|
| `moneda_comun` | Moneda para comparar/ordenar: `"USD"` o `"BOB"`. |
| `tasa_bs_por_usd` | Cuántos Bs. equivale 1 USD (ej. `6.96`). |
| `timeout_segundos` | Timeout de red por sitio. |
| `max_resultados_por_sitio` | Tope de resultados por sitio. |

> `config.json` está en `.gitignore` para que tu tasa local no se suba al repo.

## Agregar un sitio real

1. Copia `app/scrapers/plantilla.py.txt` como `app/scrapers/mi_sitio.py`.
2. Ajusta `nombre`, `moneda_por_defecto`, la URL de búsqueda y los selectores HTML.
3. Impórtalo en `app/scrapers/__init__.py` (`from . import mi_sitio`).
4. Listo: el agregador lo detecta automáticamente.

Cuando me pases las páginas, implemento el scraper de cada una siguiendo este patrón.

## Probar solo Locatel

Antes de levantar toda la app, puedes verificar que Locatel responde en tu red:

```bash
python probar_locatel.py paracetamol
```

Debería listar los productos con su precio en Bs. Si sale un error o no
encuentra nada, cópialo y lo ajustamos (probablemente el sitio use otra ruta
de API).

## Scripts ligeros para iPad (a-Shell)

Para usar en el iPad con la app **a-Shell** (Python sin instalar nada):

```bash
python locatel.py paracetamol
```

- `locatel_ipad.py` → busca en **Locatel**. Funciona directo. ✅

## Farmacia Badan — solo desde COMPUTADORA

Badan usa **Cloudflare**, que exige un navegador real. Por eso **no** se puede
leer con Python en el iPad (ni gratis con servicios). Se lee con Playwright
(navegador automático) en una Mac/PC:

```bash
pip install playwright
playwright install chromium
python badan_computadora.py paracetamol
```

## Estado actual

| Farmacia | Moneda | Estado |
|----------|--------|--------|
| **Locatel** | Bs. (+ USD estimado) | ✅ Funciona (iPad y PC) |
| **Farmacia Badan** | por confirmar (Bs./$) | 🖥️ Solo computadora (Cloudflare) |
| **Farmatodo** | Bs. | ⏳ Pendiente |
| Farmacia Demo | — | Deshabilitado (ejemplo) |

> ⚠️ Nota: el entorno de desarrollo remoto bloquea estos dominios, así que los
> scrapers se prueban corriendo en **tu dispositivo** (iPad o computadora).
