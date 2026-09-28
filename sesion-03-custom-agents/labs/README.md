# Lab 3.1 · Agente de viajes multi-agente con ADK

**Objetivo del examen:** 3.1 (y parte de 3.3) — elegir el bloque de construcción correcto: workflow
agents, herramientas, estado de sesión, callbacks, `AgentTool`, selección de modelo.

Abre `agente_viajes/` y completa los **TODO 1-10** en `tools.py`, `callbacks.py` y `agent.py`.
El docstring de `agent.py` tiene el diagrama objetivo.

## Verificar (sin costo, no llama al LLM)

```bash
python -m evaluador labs 3
```

## Ejecutarlo de verdad (opcional, requiere proyecto GCP)

```bash
cp sesion-03-custom-agents/labs/agente_viajes/.env.example sesion-03-custom-agents/labs/agente_viajes/.env
cd sesion-03-custom-agents/labs
adk web            # abre http://localhost:8000 y elige agente_viajes
```

Prueba: *"Mi presupuesto es 400 USD. Prefiero ventana. Quiero ir de SCL a LIM el 2 de noviembre,
3 noches."* y luego pide reservar un hotel de 200 USD/noche. En la pestaña **Trace** observa
`invoke_agent` → `call_llm` → `execute_tool`, cómo el callback bloquea la reserva, y en **State**
la clave `user:asiento`.

## Retos extra (no calificados)

1. Cambia `InMemorySessionService` por Agent Platform Sessions (`adk web --session_service_uri agentengine://...`).
2. Añade Memory Bank con `preload_memory` para recordar preferencias entre sesiones.
3. Reescribe el proceso de reserva como **grafo** (`google.adk.workflow.Workflow`) con un nodo de
   aprobación humana.
4. Expón `buscar_vuelos` como servidor MCP y consúmelo con `McpToolset`.
