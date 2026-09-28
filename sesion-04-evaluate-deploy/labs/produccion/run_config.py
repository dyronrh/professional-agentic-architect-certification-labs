"""Configuración de ejecución para producción (Lab 4.2).

Síntomas observados en producción (ver Cloud Trace):
  - Algunas invocaciones repiten call_llm → execute_tool decenas de veces durante minutos.
  - Errores transitorios del backend abortan la ejecución completa.
  - La latencia crece con cada turno porque se envía todo el historial.
"""

from google.adk.agents import RunConfig


# TODO 1: limita las llamadas al LLM por invocación (entero positivo razonable, ≤ 50).
#         Ojo: 0 o negativo significa SIN límite.
# TODO 2: carga solo los eventos recientes de la sesión con GetSessionConfig(num_recent_events=...),
#         entre 5 y 50 (google.adk.sessions.base_session_service.GetSessionConfig).
def crear_run_config() -> RunConfig:
    return RunConfig(max_llm_calls=0)


# TODO 3: devuelve los plugins globales: ReflectAndRetryToolPlugin con max_retries entre 1 y 5
#         (google.adk.plugins.reflect_retry_tool_plugin).
def crear_plugins() -> list:
    return []
