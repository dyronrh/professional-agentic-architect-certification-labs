# Sesión 3 · Desarrollar agentes personalizados (~33 %) ⭐ el dominio más pesado

> *Section 3: Developing custom agents*

| Objetivo | Qué evalúan |
|---|---|
| **3.1** Construir agentes con ADK *(numeración aproximada)* | Modelos, herramientas, workflow agents/grafos, sesiones, estado, memoria, callbacks, plugins |
| **3.2** Integrar conocimiento del dominio empresarial | Diseñar, configurar y gestionar pipelines RAG y sistemas de retrieval vectorial |
| **3.3** Sistemas multi-agente e interoperabilidad *(numeración aproximada)* | MCP, A2A, Agent Registry, Agent Identity, gobierno multi-agente |

**Plan (≈ 8-10 h, dedícale 2 días):** teoría → quiz modo estudio → Lab 3.1 (tests + `adk web`) →
retos extra → caso práctico → evaluación.

---

## 1. Teoría esencial

### Bloques de ADK

| Pieza | Para qué | Trampa típica |
|---|---|---|
| `LlmAgent` (`Agent`) | razonar, usar herramientas | instrucciones largas ≠ determinismo |
| `SequentialAgent` | A → B → C fijo | sin ramas |
| `ParallelAgent` | tareas independientes a la vez | `output_key` iguales se pisan |
| `LoopAgent` | iterar hasta calidad | **sin `max_iterations` + `exit_loop` = loop infinito** |
| Grafo (`Workflow`, ADK 2.x) | procesos deterministas, ramas en código, pausas HITL | diseñarlo por adelantado |
| `sub_agents` + transfer | el LLM decide a quién pasar la conversación | no determinista; depende de buenas `description` |
| `AgentTool(agente)` | el padre llama al hijo y **conserva el control** | un salto LLM extra |
| Callbacks (`before/after_model`, `before/after_tool`, `before/after_agent`) | reglas deterministas por agente | devolver `None` = continuar; devolver objeto = reemplazar/omitir |
| Plugins (en el Runner/App) | el mismo guardrail para **todos** los agentes | — |
| `output_key` | guarda la respuesta final del agente en `state[clave]` | — |
| `{clave}` en `instruction` | inyecta estado en el prompt | — |

**Herramientas:** firma **tipada** + **docstring con Args** → ADK genera la declaración.
Devuelve `dict` con `status`. `ToolContext` da acceso a `state`, artefactos, auth y memoria.
Tipos: FunctionTool, `LongRunningFunctionTool`, `AgentTool`, `McpToolset`, OpenAPI, built-in
(Google Search, code execution, Agent Search), `require_confirmation` para HITL.

### Estado, sesiones y memoria

| Prefijo | Alcance |
|---|---|
| *(ninguno)* | esta sesión |
| `user:` | todas las sesiones de este usuario |
| `app:` | todos los usuarios de la app |
| `temp:` | solo esta invocación (nunca se persiste) |

- `InMemorySessionService` → se pierde al reiniciar. Producción: **Agent Platform Sessions**
  (`VertexAiSessionService`, `agentengine://`) o `DatabaseSessionService`.
- **Memory Bank**: memoria de largo plazo (extrae, consolida, deduplica). `preload_memory` (cada turno)
  vs `load_memory` (el LLM decide).
- Latencia que crece por turno → limitar eventos recientes (`GetSessionConfig(num_recent_events)`) + context caching.

### Modelos (right-sizing)

Flash-Lite → alto volumen/triage · Flash → general · Pro / thinking → planificación compleja ·
Gemma/Model Garden autodesplegado → pesos propios, edge, control total · vLLM en GKE → requiere
`--enable-auto-tool-choice` + parser para tool calling · LiteLLM para modelos de terceros.

### RAG y retrieval (3.2)

| Opción | Mejor para | Ojo |
|---|---|---|
| **Agent Search** (ex Vertex AI Search) | búsqueda empresarial gestionada, rápido | menos control fino |
| **RAG Engine** | RAG gestionado con control de chunking/embeddings | **modelo de embeddings inmutable por corpus** |
| **Vector Search** / **Agent Retrieval** (VS 2.0) | escala masiva, baja latencia | más operación |
| **AlloyDB** (pgvector/ScaNN) | datos transaccionales + filtros SQL | BD operacional |
| **BigQuery** `VECTOR_SEARCH` | analítica / batch | no es serving de baja latencia |

Calidad: códigos exactos → **híbrida** (densa + sparse, RRF) · mal orden → **reranking** ·
tablas partidas → **layout parser** + chunking por layout · grounding y citas.

### Multi-agente, interoperabilidad y gobierno (3.3)

- **MCP** = agente ↔ herramientas/datos. **A2A** = agente ↔ agente (otro equipo/framework, Agent Card).
  A2A para sub-agentes en el mismo proceso es overhead innecesario.
- **Agent Registry**: catálogo de MCP servers y agentes; descubrimiento en vez de URLs hardcodeadas;
  resolver al arranque y cachear; base de las políticas del gateway.
- **Agent Identity**: principal por agente (SPIFFE), ligado al ciclo de vida; roles mínimos por agente,
  roles base a un *principal set*. **Borrar y recrear = principal nuevo** (bindings huérfanos).

---

## 2. Práctica

| Actividad | Dónde | Se califica |
|---|---|---|
| Quiz (20 preguntas) | `preguntas.json` | `python -m evaluador quiz 3` |
| Lab 3.1 – Agente de viajes ADK | [`labs/`](labs/README.md) | tests (requiere `google-adk`) |
| Caso práctico | [`caso-practico.md`](caso-practico.md) | juez LLM |

Recomendado: los codelabs oficiales de ADK y el *learning path* de Google Skills para este dominio.

## 3. Evaluación final

```bash
python -m evaluador sesion 3     # o /evaluar-sesion 3 en Claude Code
```
