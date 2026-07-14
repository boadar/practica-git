"""Aplicacion FastAPI: API de busqueda + frontend web.

Correr en local:
    uvicorn app.main:app --reload

Luego abrir http://127.0.0.1:8000 en el navegador.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .aggregator import buscar_en_todos
from .config import cargar_config
from .models import RespuestaBusqueda
from .scrapers import scrapers_disponibles

app = FastAPI(title="Buscador de Medicamentos", version="0.1.0")

STATIC_DIR = Path(__file__).parent / "static"


@app.get("/api/salud")
async def salud() -> dict:
    """Chequeo simple de estado y configuracion activa."""
    cfg = cargar_config()
    return {
        "estado": "ok",
        "moneda_comun": cfg.moneda_comun,
        "tasa_bs_por_usd": cfg.tasa_bs_por_usd,
        "sitios": [s.nombre for s in scrapers_disponibles()],
    }


@app.get("/api/buscar", response_model=RespuestaBusqueda)
async def buscar(q: str = Query(..., min_length=1, description="Medicamento a buscar")):
    """Busca un medicamento en todos los sitios y compara precios."""
    cfg = cargar_config()
    return await buscar_en_todos(q.strip(), cfg)


@app.get("/")
async def index() -> FileResponse:
    """Sirve la interfaz web."""
    return FileResponse(STATIC_DIR / "index.html")


# Archivos estaticos (JS, CSS).
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
