# Sesión 4 · Evaluar y desplegar flujos agénticos (~22 %)

> *Section 4: Evaluating and deploying agentic workflows*

| Objetivo | Qué evalúan |
|---|---|
| **4.1** Evaluar agentes en desarrollo y en producción | Test sets (golden data, prompts, casos borde), pipelines de evaluación continua, elegir framework (evalsets de ADK, Gen AI evaluation service, autoraters propios) |
| **4.2** Desplegar y operar *(numeración aproximada)* | Elegir runtime (Agent Runtime / Cloud Run / GKE), configurarlo, observabilidad y troubleshooting |

**Plan (≈ 6-8 h):** teoría → quiz modo estudio → Lab 4.1 → Lab 4.2 → caso práctico → evaluación.

---

## 1. Teoría esencial

### Qué medir

- **Trayectoria** (el *cómo*): herramientas, argumentos, orden.
- **Respuesta final** (el *qué*): corrección, grounding, seguridad, formato.

| Situación | Instrumento |
|---|---|
| Gate por PR, barato y determinista | `tool_trajectory_avg_score` + `response_match_score` |
| Hay referencia pero se parafrasea | `final_response_match_v2` (juez semántico) |
| No hay referencia, sí criterios de "bueno" | rúbricas: `rubric_based_final_response_quality_v1`, `rubric_based_tool_use_quality_v1` |
| Afirmaciones sin respaldo | `hallucinations_v1` |
| Diálogos con caminos variables | simulación de usuario (`ConversationScenario`) + `multi_turn_task_success_v1` |
| Seguridad | `safety_v1` |
| Degradación semanas después | **monitores online** sobre trazas de producción |

**Match de trayectoria:** `EXACT` (idéntica, sin extras) · `IN_ORDER` (requeridas en orden, extras ok) · `ANY_ORDER`.
En el Gen AI evaluation service: `trajectory_precision` (penaliza extras), `trajectory_recall` (penaliza faltantes).

**Cómo se corre:** `adk web` (crear casos desde sesiones), `pytest` + `AgentEvaluator.evaluate()` (CI),
`adk eval` (nightly/CLI), Gen AI evaluation service (escala, autoraters, monitores).
Datos: sesiones reales → trazas curadas → sintéticos → adversariales. Jueces LLM: temperatura 0,
varias muestras, **calibrados contra humanos**. No uses ROUGE/BLEU para corrección semántica.

### Dónde desplegar

| Requisito | Runtime |
|---|---|
| Python/ADK, sesiones y memoria gestionadas, mínima operación, Agent Identity, revisiones | **Agent Runtime** (ex Agent Engine) |
| Cualquier lenguaje, HTTP/eventos, scale-to-zero, LB/IAP existentes | **Cloud Run** |
| Código no confiable (gVisor), GPUs/modelos propios, carga alta estable (CUDs), control total, tareas muy largas | **GKE** |

Claves de configuración:
- **Agent Runtime:** `min_instances`/`max_instances`, CPU/memoria, concurrencia por instancia (agentes async
  aprovechan más), revisiones y división de tráfico, **PSC interface** para redes privadas (no conector VPC),
  cuota de consultas por región.
- **Cloud Run:** sesiones **externas** (`--session_service_uri=agentengine://…` o base de datos) —la afinidad
  de sesión es best-effort—; timeout máx. 60 min; concurrencia por instancia; nunca `--with_ui` en prod.
- **GKE:** Agent Sandbox, vLLM/Gemma en GPUs, HPA, node pools, Workload Identity.

### Operar y diagnosticar

| Síntoma | Perilla |
|---|---|
| Loops largos, picos de tokens | `RunConfig(max_llm_calls=N)` (0 = ilimitado), `max_iterations`, mejores descripciones |
| p95 alto solo en picos | `min_instances`, concurrencia |
| Latencia crece por turno | historial reciente (`GetSessionConfig(num_recent_events)`), compactación, context caching |
| Errores transitorios de herramientas | `ReflectAndRetryToolPlugin(max_retries=…)` |
| 429 `RESOURCE_EXHAUSTED` | aumento de cuota / Provisioned Throughput |
| Pérdida de sesiones tras deploy | servicio de sesiones persistente |
| No llega a API privada | PSC interface + DNS peering |
| Calidad cae en producción | monitores online, fijar versiones de modelo, casos al golden set |

Telemetría: **Cloud Trace** (`invoke_agent`, `call_llm`, `execute_tool`), métricas `gen_ai.*` en
Cloud Monitoring, Cloud Logging, **BigQuery Agent Analytics** (plugin) para análisis de eventos.

---

## 2. Práctica

| Actividad | Dónde | Se califica |
|---|---|---|
| Quiz (16 preguntas) | `preguntas.json` | `python -m evaluador quiz 4` |
| Lab 4.1 – Evalset y criterios | [`labs/`](labs/README.md) | tests |
| Lab 4.2 – RunConfig, deploy, decisiones | [`labs/`](labs/README.md) | tests |
| Caso práctico | [`caso-practico.md`](caso-practico.md) | juez LLM |

## 3. Evaluación final

```bash
python -m evaluador sesion 4     # o /evaluar-sesion 4
```
