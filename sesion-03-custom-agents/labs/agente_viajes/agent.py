"""Agente de viajes multi-agente con ADK (Lab 3.1).

Arquitectura objetivo:

  concierge (LlmAgent, root_agent)
   ├─ tools: guardar_preferencia, registrar_presupuesto, reservar_hotel, AgentTool(planificador)
   └─ before_tool_callback: validar_presupuesto
  planificador (SequentialAgent)
   ├─ busqueda_paralela (ParallelAgent)
   │    ├─ investigador_vuelos  (output_key="vuelos",  tool buscar_vuelos)
   │    └─ investigador_hoteles (output_key="hoteles")
   ├─ redactor    (lee {vuelos} y {hoteles}, output_key="borrador")
   └─ refinamiento (LoopAgent, max_iterations<=5)
        ├─ critico    (tool exit_loop cuando el borrador cumple)
        └─ refinador  (output_key="borrador")
"""

import os

from google.adk.agents import LlmAgent, LoopAgent, ParallelAgent, SequentialAgent
from google.adk.tools import exit_loop
from google.adk.tools.agent_tool import AgentTool

from .callbacks import validar_presupuesto
from .tools import buscar_vuelos, guardar_preferencia, registrar_presupuesto, reservar_hotel

MODELO_RAPIDO = os.environ.get("MODELO_RAPIDO", "gemini-flash-lite-latest")
MODELO_RAZONAMIENTO = os.environ.get("MODELO_RAZONAMIENTO", "gemini-flash-latest")

investigador_vuelos = LlmAgent(
    name="investigador_vuelos",
    model=MODELO_RAPIDO,
    instruction="Busca vuelos para el viaje pedido usando buscar_vuelos. Resume las 2 mejores opciones.",
    tools=[buscar_vuelos],
    output_key="resultados",  # TODO 4: ¿qué pasa si dos agentes en paralelo escriben la misma clave?
)

investigador_hoteles = LlmAgent(
    name="investigador_hoteles",
    model=MODELO_RAPIDO,
    instruction="Propón 2 hoteles adecuados para el destino y fechas pedidas, con precio por noche.",
    output_key="resultados",
)

# TODO 5: busqueda_paralela = ParallelAgent(...) con ambos investigadores.

redactor = LlmAgent(
    name="redactor",
    model=MODELO_RAZONAMIENTO,
    # TODO 6: inyecta el estado con {vuelos} y {hoteles} y guarda la salida en output_key="borrador".
    instruction="Redacta un itinerario.",
)

critico = LlmAgent(
    name="critico",
    model=MODELO_RAZONAMIENTO,
    instruction=(
        "Revisa el itinerario {borrador}. Si incluye vuelo, hotel, costo total y no tiene errores, "
        "llama a exit_loop. Si no, lista exactamente qué corregir."
    ),
    # TODO 7: el crítico necesita una forma de terminar el loop.
)

refinador = LlmAgent(
    name="refinador",
    model=MODELO_RAZONAMIENTO,
    instruction="Corrige el itinerario {borrador} según las observaciones del crítico.",
    output_key="borrador",
)

# TODO 8: refinamiento = LoopAgent(...) con [critico, refinador] y un tope de iteraciones.

# TODO 9: planificador = SequentialAgent(...) en el orden correcto.

# TODO 10: root_agent = LlmAgent(name="concierge", ...) con las herramientas y el callback del diagrama.
root_agent = LlmAgent(
    name="concierge",
    model=MODELO_RAZONAMIENTO,
    instruction="Eres un concierge de viajes.",
)
