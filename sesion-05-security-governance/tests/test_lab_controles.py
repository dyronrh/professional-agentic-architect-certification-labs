"""Checks del Lab 5.2: matriz de controles de seguridad y gobierno."""

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

SESION = Path(__file__).resolve().parents[1]
CLAVES = json.loads((Path(__file__).parent / "_claves.json").read_text(encoding="utf-8"))


# ---------- Lab 5.2: matriz de controles (no requiere ADK) ----------

@pytest.fixture(scope="module")
def matriz():
    return json.loads((SESION / "labs" / "controles" / "matriz_controles.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("clave", [f"C{i}" for i in range(1, 14)])
def test_matriz_control(matriz, clave):
    """Elegiste el control de seguridad/gobierno correcto para el escenario."""
    r = matriz[clave]["respuesta"].strip()
    assert r in matriz["_opciones"], f"{clave}: responde con una opción válida"
    assert hashlib.sha256(f"{clave}:{r}".encode()).hexdigest()[:16] == CLAVES[clave], f"{clave}: control incorrecto"
