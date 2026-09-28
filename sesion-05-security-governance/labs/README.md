# Labs de la Sesión 5

## Lab 5.1 · Guardrails deterministas en ADK (objetivo 5.2)

Completa los **TODO 1-6** de [`guardrails/guardrails.py`](guardrails/guardrails.py):

| TODO | Tipo de callback | Defiende contra |
|---|---|---|
| 1 `redactar_pii` | utilidad | fuga de correos, tarjetas, teléfonos |
| 2 `detectar_inyeccion` | utilidad | prompt injection / jailbreak directos |
| 3 `bloquear_inyeccion` | `before_model_callback` | inyección en el mensaje del usuario (no se llama al modelo) |
| 4 `sanear_salida_herramienta` | `after_tool_callback` | **inyección indirecta** en documentos/APIs + PII en resultados |
| 5 `validar_sql` | `before_tool_callback` | DML/DDL y tablas fuera de la allowlist (`app:tablas_permitidas`) |
| 6 `herramienta_reembolso` | `FunctionTool(require_confirmation=...)` | acciones irreversibles sin aprobación humana |

> Los filtros por regex son una **capa**, no la solución completa: en producción súmales Model Armor
> (templates + floor settings), mínimo privilegio en IAM y HITL. Eso es exactamente lo que evalúa el examen.

**Reto extra:** empaqueta los callbacks como un `BasePlugin` y regístralo en el `Runner` para que
aplique a todos los agentes.

## Lab 5.2 · Matriz de controles (objetivo 5.1)

En [`controles/matriz_controles.json`](controles/matriz_controles.json) elige, para 13 escenarios,
el control principal (Agent Identity, PAB, Model Armor floor settings, Agent Gateway, gobierno
semántico, VPC-SC, OAuth 2LO/3LO, bóveda de API keys, ID token + `run.invoker`, HITL, Workload
Identity, dry-run). Respuestas hasheadas en `tests/_claves.json`.

```bash
python -m evaluador labs 5
```
