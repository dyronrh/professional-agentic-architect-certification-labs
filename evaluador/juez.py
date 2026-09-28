"""Juez del caso práctico: califica una respuesta abierta contra una rúbrica.

Fuentes de calificación (en orden, con --juez auto):
  1. archivo: resultados/caso-practico-calificacion.json escrito por otro juez
     (p. ej. el subagente de Claude Code `evaluador-certificacion` o el agente ADK).
  2. gemini: LLM-as-judge con Gemini vía google-genai (Vertex AI o API key).
  3. pendiente: sin juez disponible; el caso no suma nota y se reporta como pendiente.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

from .config import Sesion

MODELO_POR_DEFECTO = os.environ.get("JUEZ_MODELO", "gemini-flash-latest")


@dataclass
class Criterio:
    id: str
    puntos_obtenidos: float
    puntos_max: float
    justificacion: str


@dataclass
class ResultadoCaso:
    fuente: str  # archivo | gemini | pendiente | sin_respuesta
    criterios: list[Criterio] = field(default_factory=list)
    retroalimentacion: str = ""

    @property
    def calificado(self) -> bool:
        return self.fuente in ("archivo", "gemini", "sin_respuesta")

    @property
    def porcentaje(self) -> float:
        maximo = sum(c.puntos_max for c in self.criterios)
        if self.fuente == "sin_respuesta":
            return 0.0
        return 100.0 * sum(c.puntos_obtenidos for c in self.criterios) / maximo if maximo else 0.0


def archivo_respuesta(s: Sesion):
    return s.respuestas / "caso-practico.md"


def archivo_calificacion(s: Sesion):
    return s.resultados / "caso-practico-calificacion.json"


def cargar_rubrica(s: Sesion) -> dict:
    return json.loads(s.rubrica.read_text(encoding="utf-8"))


def respuesta_vacia(texto: str) -> bool:
    # La plantilla trae comentarios HTML y encabezados; exigimos contenido real.
    import re

    limpio = re.sub(r"<!--.*?-->", "", texto, flags=re.S)
    limpio = "\n".join(l for l in limpio.splitlines() if not l.strip().startswith("#"))
    return len(limpio.split()) < 60


def construir_prompt(s: Sesion, respuesta: str) -> str:
    rubrica = cargar_rubrica(s)
    enunciado = s.enunciado_caso.read_text(encoding="utf-8")
    return f"""Eres un examinador estricto de la certificación Google Cloud Professional Agentic Architect.
Califica la respuesta del candidato al caso práctico usando EXCLUSIVAMENTE la rúbrica.

Reglas:
- Por cada criterio asigna puntos entre 0 y el máximo (se permiten medios puntos).
- Da puntos solo por lo que está escrito y justificado; no infieras intenciones.
- Penaliza respuestas que usen controles no deterministas (p. ej. "ponerlo en el prompt")
  donde el caso exige garantías, o que elijan productos incorrectos para el requisito.
- Justificación breve en español por criterio, citando lo que falta.
- "retroalimentacion": 3-6 viñetas en español con lo más importante a estudiar.

# Caso práctico
{enunciado}

# Rúbrica (JSON)
{json.dumps(rubrica, ensure_ascii=False, indent=2)}

# Respuesta del candidato
{respuesta}
"""


ESQUEMA = {
    "type": "object",
    "properties": {
        "criterios": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "puntos": {"type": "number"},
                    "justificacion": {"type": "string"},
                },
                "required": ["id", "puntos", "justificacion"],
            },
        },
        "retroalimentacion": {"type": "string"},
    },
    "required": ["criterios", "retroalimentacion"],
}


def _desde_json(datos: dict, rubrica: dict, fuente: str) -> ResultadoCaso:
    maximos = {c["id"]: float(c["puntos"]) for c in rubrica["criterios"]}
    dados = {c["id"]: c for c in datos.get("criterios", [])}
    criterios = []
    for cid, maximo in maximos.items():
        c = dados.get(cid, {"puntos": 0, "justificacion": "No evaluado."})
        puntos = max(0.0, min(float(c.get("puntos", 0)), maximo))
        criterios.append(Criterio(cid, puntos, maximo, c.get("justificacion", "")))
    return ResultadoCaso(fuente, criterios, datos.get("retroalimentacion", ""))


def gemini_disponible() -> bool:
    try:
        import google.genai  # noqa: F401
    except ImportError:
        return False
    return bool(
        os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        or (os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "").lower() in ("1", "true")
            and os.environ.get("GOOGLE_CLOUD_PROJECT"))
    )


def calificar_con_gemini(s: Sesion, respuesta: str) -> ResultadoCaso:
    from google import genai
    from google.genai import types

    cliente = genai.Client()
    salida = cliente.models.generate_content(
        model=MODELO_POR_DEFECTO,
        contents=construir_prompt(s, respuesta),
        config=types.GenerateContentConfig(
            temperature=0.0,
            response_mime_type="application/json",
            response_json_schema=ESQUEMA,
        ),
    )
    datos = json.loads(salida.text)
    resultado = _desde_json(datos, cargar_rubrica(s), "gemini")
    guardar_calificacion(s, datos, fuente=f"gemini:{MODELO_POR_DEFECTO}")
    return resultado


def guardar_calificacion(s: Sesion, datos: dict, fuente: str) -> None:
    s.resultados.mkdir(parents=True, exist_ok=True)
    datos = dict(datos, fuente=fuente)
    archivo_calificacion(s).write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")


def evaluar_caso(s: Sesion, modo: str = "auto") -> ResultadoCaso:
    rubrica = cargar_rubrica(s)
    ruta = archivo_respuesta(s)
    texto = ruta.read_text(encoding="utf-8") if ruta.exists() else ""
    if respuesta_vacia(texto):
        vacio = {"criterios": [], "retroalimentacion": "Aún no has respondido el caso práctico "
                 f"en {ruta.relative_to(s.ruta.parent)}."}
        return _desde_json(vacio, rubrica, "sin_respuesta")

    calif = archivo_calificacion(s)
    archivo_vigente = calif.exists() and calif.stat().st_mtime >= ruta.stat().st_mtime
    if modo == "archivo" or (modo == "auto" and archivo_vigente):
        if not calif.exists():
            return ResultadoCaso("pendiente", retroalimentacion=f"No existe {calif}.")
        return _desde_json(json.loads(calif.read_text(encoding="utf-8")), rubrica, "archivo")
    if modo in ("gemini", "auto") and gemini_disponible():
        try:
            return calificar_con_gemini(s, texto)
        except Exception as e:  # red, cuota, modelo no disponible...
            return ResultadoCaso("pendiente", retroalimentacion=f"Falló el juez Gemini: {e}")
    return ResultadoCaso(
        "pendiente",
        retroalimentacion="Caso práctico sin calificar: configura Gemini (ver README) o pide a "
        "Claude Code `/evaluar-sesion` para que el subagente evaluador lo califique.",
    )
