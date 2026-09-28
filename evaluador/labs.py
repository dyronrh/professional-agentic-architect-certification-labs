"""Ejecuta los tests de laboratorio de una sesión con pytest y resume el resultado."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

from .config import RAIZ, Sesion


@dataclass
class Check:
    nombre: str
    descripcion: str
    estado: str  # ok | fallo | omitido
    detalle: str = ""


@dataclass
class ResultadoLabs:
    checks: list[Check] = field(default_factory=list)
    error: str = ""

    @property
    def total(self) -> int:
        return len(self.checks)

    @property
    def aprobados(self) -> int:
        return sum(c.estado == "ok" for c in self.checks)

    @property
    def porcentaje(self) -> float:
        # Los tests omitidos (p. ej. falta google-adk) cuentan como no superados.
        return 100.0 * self.aprobados / self.total if self.total else 0.0


def _primera_linea(texto: str) -> str:
    for linea in texto.splitlines():
        linea = linea.strip()
        if linea.startswith("E "):
            return linea[2:].strip()[:300]
    return (texto.strip().splitlines() or [""])[-1][:300]


def ejecutar_labs(s: Sesion) -> ResultadoLabs:
    carpeta_tests = s.ruta / "tests"
    if not carpeta_tests.exists():
        return ResultadoLabs(error="La sesión no tiene carpeta tests/")
    cargar_descripciones(s)
    with tempfile.TemporaryDirectory() as tmp:
        xml = Path(tmp) / "junit.xml"
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", str(carpeta_tests), "-q", "-p", "no:cacheprovider",
             f"--junitxml={xml}", "-o", "junit_family=xunit1"],
            cwd=RAIZ, capture_output=True, text=True,
        )
        if not xml.exists():
            return ResultadoLabs(error=(proc.stdout + proc.stderr)[-2000:])
        arbol = ET.parse(xml)
    resultado = ResultadoLabs()
    for caso in arbol.iter("testcase"):
        nombre = caso.get("name", "")
        doc = _docstrings.get(nombre.split("[")[0], "")
        fallo = caso.find("failure")
        if fallo is None:
            fallo = caso.find("error")
        omitido = caso.find("skipped")
        if fallo is not None:
            detalle = _primera_linea(fallo.get("message", "") + "\n" + (fallo.text or ""))
            resultado.checks.append(Check(nombre, doc, "fallo", detalle))
        elif omitido is not None:
            resultado.checks.append(Check(nombre, doc, "omitido", omitido.get("message", "")))
        else:
            resultado.checks.append(Check(nombre, doc, "ok"))
    if not resultado.checks:
        resultado.error = (proc.stdout + proc.stderr)[-2000:]
    return resultado


# Las descripciones legibles se leen del docstring de cada test.
_docstrings: dict[str, str] = {}


def cargar_descripciones(s: Sesion) -> None:
    import ast

    for archivo in (s.ruta / "tests").glob("test_*.py"):
        arbol = ast.parse(archivo.read_text(encoding="utf-8"))
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.FunctionDef) and nodo.name.startswith("test_"):
                doc = ast.get_docstring(nodo) or ""
                _docstrings[nodo.name] = doc.splitlines()[0] if doc else ""
