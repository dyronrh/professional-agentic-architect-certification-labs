"""Callbacks del agente de viajes (Lab 3.1).

Un before_tool_callback recibe (tool, args, tool_context):
  - devuelve None  → la herramienta se ejecuta normalmente.
  - devuelve dict  → se OMITE la herramienta y ese dict se usa como su resultado.
Es un control determinista: el LLM no puede "convencerlo".
"""

from typing import Any, Optional

from google.adk.tools import BaseTool, ToolContext


# TODO 3: si la herramienta es `reservar_hotel` y precio_noche * noches supera
# tool_context.state["user:presupuesto"], bloquea devolviendo
# {"status": "error", "error_message": "..."}; en cualquier otro caso devuelve None.
# Si no hay presupuesto registrado, permite la reserva.
def validar_presupuesto(tool: BaseTool, args: dict[str, Any], tool_context: ToolContext) -> Optional[dict]:
    return None
