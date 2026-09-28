"""Agente evaluador construido con ADK (práctica del dominio 3 usando tu propio evaluador).

Uso:
  adk web evaluador          # y elige "agente_evaluador"
  adk run evaluador/agente_evaluador

Requiere credenciales de Gemini (ver README: GOOGLE_GENAI_USE_VERTEXAI + GOOGLE_CLOUD_PROJECT, o GOOGLE_API_KEY).
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # raíz del repo, para `import evaluador`

from google.adk.agents import LlmAgent  # noqa: E402

from evaluador import banco, juez, labs, reporte  # noqa: E402
from evaluador.config import sesion  # noqa: E402


def calificar_quiz_y_labs(numero: int) -> dict:
    """Califica de forma determinista el quiz y los laboratorios de una sesión.

    Args:
      numero: número de sesión, de 1 a 5.
    """
    s = sesion(numero)
    q = banco.calificar(banco.cargar_preguntas(s), banco.cargar_respuestas(banco.archivo_respuestas(s)))
    l = labs.ejecutar_labs(s)
    return {
        "status": "success",
        "quiz": {"porcentaje": round(q.porcentaje, 1), "correctas": q.correctas, "total": q.total,
                 "por_objetivo": q.por_objetivo,
                 "conceptos_fallados": sorted({p.concepto for p, _ in q.falladas})},
        "labs": {"porcentaje": round(l.porcentaje, 1),
                 "fallidos": [f"{c.descripcion or c.nombre}: {c.detalle}" for c in l.checks if c.estado != "ok"]},
    }


def obtener_caso_practico(numero: int) -> dict:
    """Devuelve el enunciado, la rúbrica y la respuesta del candidato para el caso práctico.

    Args:
      numero: número de sesión, de 1 a 5.
    """
    s = sesion(numero)
    ruta = juez.archivo_respuesta(s)
    respuesta = ruta.read_text(encoding="utf-8") if ruta.exists() else ""
    return {
        "status": "success",
        "enunciado": s.enunciado_caso.read_text(encoding="utf-8"),
        "rubrica": juez.cargar_rubrica(s),
        "respuesta": respuesta,
        "respuesta_vacia": juez.respuesta_vacia(respuesta),
    }


def registrar_calificacion_caso(numero: int, calificacion_json: str) -> dict:
    """Guarda la calificación del caso práctico y genera el reporte final de la sesión.

    Args:
      numero: número de sesión, de 1 a 5.
      calificacion_json: JSON con {"criterios": [{"id": str, "puntos": number, "justificacion": str}],
        "retroalimentacion": str}. Los ids deben coincidir con los de la rúbrica.
    """
    s = sesion(numero)
    try:
        datos = json.loads(calificacion_json)
    except json.JSONDecodeError as e:
        return {"status": "error", "error_message": f"JSON inválido: {e}"}
    ids = {c["id"] for c in juez.cargar_rubrica(s)["criterios"]}
    faltan = ids - {c.get("id") for c in datos.get("criterios", [])}
    if faltan:
        return {"status": "error", "error_message": f"Faltan criterios: {sorted(faltan)}"}
    juez.guardar_calificacion(s, datos, fuente="adk:agente_evaluador")
    q = banco.calificar(banco.cargar_preguntas(s), banco.cargar_respuestas(banco.archivo_respuestas(s)))
    l = labs.ejecutar_labs(s)
    c = juez.evaluar_caso(s, "archivo")
    nota = reporte.calcular_nota(q, l, c)
    ruta = reporte.guardar_reporte(s, reporte.generar_reporte(s, q, l, c, nota))
    reporte.registrar_sesion(s, nota)
    return {"status": "success", "nota": nota.total, "aprobado": nota.aprobado, "caso": nota.caso,
            "reporte": str(ruta)}


def ver_progreso() -> dict:
    """Devuelve la tabla de avance de todas las sesiones y simulacros."""
    return {"status": "success", "progreso": reporte.resumen_progreso()}


root_agent = LlmAgent(
    name="agente_evaluador",
    model=os.environ.get("JUEZ_MODELO", "gemini-flash-latest"),
    description="Examinador de la certificación Professional Agentic Architect.",
    instruction="""Eres el examinador estricto de la certificación Google Cloud Professional Agentic Architect.
Hablas en español. Cuando el candidato pida evaluar la sesión N:
1. Llama a calificar_quiz_y_labs(N) y a obtener_caso_practico(N).
2. Si respuesta_vacia es true, no califiques el caso: explica que falta y resume quiz y labs.
3. Si no, califica cada criterio de la rúbrica (0..puntos, medios puntos permitidos) solo por lo escrito y
   justificado; usa los indicadores como checklist; penaliza controles no deterministas donde se exigen
   garantías y productos incorrectos. Llama a registrar_calificacion_caso(N, calificacion_json).
4. Responde con: nota y si aprueba (umbral 70), desglose, objetivos débiles, conceptos fallados, labs en
   rojo y 3 próximos pasos concretos. No reveles respuestas de los labs.
Si piden su avance general, usa ver_progreso.""",
    tools=[calificar_quiz_y_labs, obtener_caso_practico, registrar_calificacion_caso, ver_progreso],
)
