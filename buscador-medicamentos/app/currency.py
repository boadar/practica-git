"""Normalizacion de precios entre Bs. (BOB) y Dolares (USD)."""
from __future__ import annotations

from .config import Config
from .models import Resultado

BOB = "BOB"  # Bolivianos (Bs.)
USD = "USD"  # Dolares (mostrados en algunos sitios como "REF")


def normalizar_moneda(valor: str) -> str:
    """Convierte etiquetas variadas de moneda a "BOB" o "USD".

    Acepta cosas como "Bs", "Bs.", "BOB", "$", "USD", "REF", "$us".
    """
    v = (valor or "").strip().upper().replace(".", "")
    if v in {"BS", "BOB", "BOLIVIANOS", "SUS", "$US"}:
        return BOB
    if v in {"USD", "$", "DOLAR", "DOLARES", "REF", "US$", "$US "}:
        return USD
    # Por defecto asumimos Bs. (moneda local mas comun en los sitios).
    return BOB


def _a_usd(precio: float, moneda: str, tasa: float) -> float:
    return precio if moneda == USD else precio / tasa


def _a_bs(precio: float, moneda: str, tasa: float) -> float:
    return precio if moneda == BOB else precio * tasa


def enriquecer(resultado: Resultado, cfg: Config) -> Resultado:
    """Agrega precio_bs, precio_usd y precio_comparacion a un resultado."""
    moneda = normalizar_moneda(resultado.moneda)
    resultado.moneda = moneda
    tasa = cfg.tasa_bs_por_usd

    resultado.precio_bs = round(_a_bs(resultado.precio, moneda, tasa), 2)
    resultado.precio_usd = round(_a_usd(resultado.precio, moneda, tasa), 2)
    resultado.precio_comparacion = (
        resultado.precio_usd if cfg.moneda_comun == USD else resultado.precio_bs
    )
    return resultado
