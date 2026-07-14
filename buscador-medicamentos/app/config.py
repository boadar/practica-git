"""Carga de configuracion de la aplicacion.

La configuracion se lee de ``config.json`` (si existe) y en su defecto usa
valores por defecto. La tasa de cambio Bs/USD es configurable para poder
comparar precios que vienen en distintas monedas.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

# Raiz del proyecto (carpeta buscador-medicamentos/)
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config.json"


@dataclass
class Config:
    """Parametros de la aplicacion."""

    # Moneda a la que se convierte todo para poder comparar ("USD" o "BOB").
    moneda_comun: str = "USD"
    # Cuantos bolivianos (Bs.) equivale 1 dolar.
    tasa_bs_por_usd: float = 6.96
    # Timeout de red para cada peticion a un sitio.
    timeout_segundos: float = 15.0
    # Tope de resultados que se piden a cada sitio.
    max_resultados_por_sitio: int = 20


def cargar_config() -> Config:
    """Lee ``config.json`` si existe; si no, devuelve valores por defecto."""
    if not CONFIG_PATH.exists():
        return Config()

    datos = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    # Ignoramos claves que empiezan con "//" (comentarios en el ejemplo).
    datos = {k: v for k, v in datos.items() if not k.startswith("//")}
    return Config(
        moneda_comun=str(datos.get("moneda_comun", "USD")).upper(),
        tasa_bs_por_usd=float(datos.get("tasa_bs_por_usd", 6.96)),
        timeout_segundos=float(datos.get("timeout_segundos", 15.0)),
        max_resultados_por_sitio=int(datos.get("max_resultados_por_sitio", 20)),
    )
