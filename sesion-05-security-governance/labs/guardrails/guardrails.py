"""Guardrails deterministas para un agente ADK (Lab 5.1).

Cada función tiene la firma exacta de un callback de ADK para que puedas registrarla en un
LlmAgent (o empaquetarla en un Plugin):

  before_model_callback(callback_context, llm_request) -> Optional[LlmResponse]
  before_tool_callback(tool, args, tool_context)        -> Optional[dict]
  after_tool_callback(tool, args, tool_context, tool_response) -> Optional[dict]

Devolver None = continuar normalmente. Devolver un objeto = reemplazar/omitir el paso.
"""

from __future__ import annotations

import re
from typing import Any, Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.adk.tools import BaseTool, FunctionTool, ToolContext
from google.genai import types

MENSAJE_BLOQUEO = "No puedo ayudar con esa solicitud."


# ---------------------------------------------------------------------------
# TODO 1: redacta PII en texto libre.
#   - correos             → [EMAIL]
#   - tarjetas (13-19 dígitos, con o sin espacios/guiones) → [TARJETA]
#   - teléfonos tipo +56 9 1234 5678 / +1 415 555 0100    → [TELEFONO]
# ---------------------------------------------------------------------------
def redactar_pii(texto: str) -> str:
    return texto


# ---------------------------------------------------------------------------
# TODO 2: detecta intentos de prompt injection / jailbreak (español e inglés), p. ej.:
#   "ignora tus instrucciones", "ignora todas las instrucciones anteriores",
#   "ignore previous instructions", "ignore all prior instructions",
#   "revela tu system prompt", "reveal your system prompt", "developer mode", "jailbreak".
# No debe marcar frases normales como "¿puedes ignorar el pedido anterior y ver el nuevo?".
# ---------------------------------------------------------------------------
def detectar_inyeccion(texto: str) -> bool:
    return False


# ---------------------------------------------------------------------------
# TODO 3: before_model_callback. Revisa el ÚLTIMO mensaje del usuario en llm_request.contents;
# si detectar_inyeccion(...) es True, devuelve un LlmResponse con MENSAJE_BLOQUEO (rol "model")
# para que el modelo NO sea llamado. Si no, devuelve None.
# ---------------------------------------------------------------------------
def bloquear_inyeccion(callback_context: CallbackContext, llm_request: LlmRequest) -> Optional[LlmResponse]:
    return None


# ---------------------------------------------------------------------------
# TODO 4: after_tool_callback contra inyección indirecta y fuga de PII.
# Recorre tool_response (dicts/listas anidadas). En cada string:
#   - si contiene una inyección → reemplázalo por "[CONTENIDO BLOQUEADO]"
#   - si no, aplica redactar_pii
# Si algo cambió devuelve el dict saneado; si nada cambió devuelve None.
# ---------------------------------------------------------------------------
def sanear_salida_herramienta(
    tool: BaseTool, args: dict[str, Any], tool_context: ToolContext, tool_response: dict
) -> Optional[dict]:
    return None


# ---------------------------------------------------------------------------
# TODO 5: before_tool_callback para la herramienta "consultar_bigquery" (args["sql"]):
#   - solo SELECT / WITH (bloquea INSERT, UPDATE, DELETE, MERGE, DROP, CREATE, ALTER, TRUNCATE, GRANT)
#   - toda tabla después de FROM/JOIN debe estar en tool_context.state["app:tablas_permitidas"]
#     (compara el último segmento: `proyecto.dataset.sales` → sales; ignora los nombres
#     definidos como CTE en un WITH, p. ej. `WITH t AS (...) SELECT ... FROM t`)
# Si viola algo, devuelve {"status": "error", "error_message": "..."}; si no, None.
# Otras herramientas: None.
# ---------------------------------------------------------------------------
def validar_sql(tool: BaseTool, args: dict[str, Any], tool_context: ToolContext) -> Optional[dict]:
    return None


# ---------------------------------------------------------------------------
# TODO 6: HITL para reembolsos. `requiere_aprobacion` recibe los mismos argumentos que la
# herramienta y devuelve True si monto > 1000. Luego crea `herramienta_reembolso` como
# FunctionTool(emitir_reembolso, require_confirmation=requiere_aprobacion).
# (En despliegues con sesiones gestionadas considera LongRunningFunctionTool o una pausa de grafo.)
# ---------------------------------------------------------------------------
def emitir_reembolso(pedido_id: str, monto: float) -> dict:
    """Emite un reembolso.

    Args:
      pedido_id: pedido a reembolsar.
      monto: monto en USD.
    """
    return {"status": "success", "pedido_id": pedido_id, "monto": monto}


def requiere_aprobacion(pedido_id: str, monto: float) -> bool:
    return False


herramienta_reembolso = FunctionTool(emitir_reembolso)


def _texto_usuario(llm_request: LlmRequest) -> str:
    """Utilidad: texto del último mensaje con rol 'user'."""
    for content in reversed(llm_request.contents or []):
        if content.role == "user":
            return " ".join(p.text or "" for p in (content.parts or []))
    return ""


def _respuesta(texto: str) -> LlmResponse:
    """Utilidad: construye un LlmResponse del modelo con el texto dado."""
    return LlmResponse(content=types.Content(role="model", parts=[types.Part(text=texto)]))
