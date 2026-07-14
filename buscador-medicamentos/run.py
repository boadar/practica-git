"""Arranque rapido de la aplicacion.

Uso:
    python run.py

Equivale a: uvicorn app.main:app --host 0.0.0.0 --port 8000
El host 0.0.0.0 permite acceder desde otros dispositivos de la red local
(ademas de http://127.0.0.1:8000 en la misma maquina).
"""
from __future__ import annotations

import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
