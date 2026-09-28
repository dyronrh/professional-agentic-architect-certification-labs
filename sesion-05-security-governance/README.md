# Sesión 5 · Asegurar y gobernar flujos agénticos (~15 %)

> *Section 5: Securing and governing agentic workflows*

| Objetivo | Qué evalúan |
|---|---|
| **5.1** Configurar la seguridad y el gobierno de agentes | Autenticación agente → herramienta (OAuth), Agent Identity, PAB, Agent Gateway, Agent Registry, Model Armor, VPC-SC |
| **5.2** Implementar comportamiento y ejecución seguros | Frameworks de seguridad y guardrails, acceso seguro a datos, propagación de identidad, HITL |

**Plan (≈ 5-6 h):** teoría → quiz modo estudio → Lab 5.1 → Lab 5.2 → caso práctico → evaluación.

---

## 1. Teoría esencial

### Regla de oro del dominio

> Si el enunciado dice **"nunca", "garantizar", "sin importar"** → control **determinista** (IAM, PAB,
> políticas de gateway, callbacks, validación en la herramienta, HITL). "Ponerlo en el system prompt"
> es siempre el distractor.

### Identidad y autorización

| Control | Qué hace | Trampa |
|---|---|---|
| **Agent Identity** | principal por agente (SPIFFE, certificados, tokens ligados), ciclo de vida del recurso | recrear = principal nuevo |
| **IAM allow/deny** | concede / niega permisos | no uses SA compartidas ni Owner/Editor |
| **Principal Access Boundary (PAB)** | límite de *a qué recursos puede llegar* un conjunto de principales | **no concede** acceso |
| **VPC Service Controls** | perímetro contra exfiltración | el proyecto dentro **antes** de desplegar |
| **Workload Identity (GKE)** | identidad sin llaves para pods | — |

### Autenticación hacia herramientas

| Destino | Método |
|---|---|
| Google APIs | identidad del agente + ADC |
| MCP privado en Cloud Run | **ID token** firmado por Google (`aud` = URL) + `roles/run.invoker` |
| SaaS como el usuario | **OAuth 3LO** (consentimiento; tokens en bóveda del auth manager; ADK solicita credenciales) |
| SaaS máquina a máquina | **OAuth 2LO** (client credentials) |
| API key estática | proveedor de API keys / bóveda gestionada (Secret Manager), nunca en código |
| Agente → agente (A2A) | identidad del agente llamante + IAM sobre el agente destino |

### Gobierno del tráfico: Agent Registry + Agent Gateway

- **Registry** = inventario/allowlist de MCP servers y agentes (anotaciones de herramientas: read-only, destructive…).
- **Gateway** = punto de control del egress de los agentes: políticas de acceso (quién → qué herramienta),
  filtros de contenido (Model Armor, **gobierno semántico** en lenguaje natural), logs por agente.
- Rollout: **DRY_RUN / INSPECT_ONLY → revisar logs → ENFORCE**. Destinos no registrados = denegados.

### Guardrails en capas (5.2)

| Capa | Herramienta | ¿Determinista? |
|---|---|---|
| Modelo | safety settings de Gemini | sí |
| Plataforma | **Model Armor**: prompt injection/jailbreak, RAI, PII/SDP, URLs maliciosas; **floor settings** org/carpeta | sí |
| Código del agente | callbacks (`before_model`, `before/after_tool`), plugins globales | sí |
| Herramienta | validación de argumentos/políticas dentro de la tool | sí |
| Juez LLM / gobierno semántico | intención vs acción, reglas de negocio | **no** |
| Humano | confirmación de herramientas, pausas HITL | humano |

- **Inyección indirecta** llega por **salidas de herramientas** → filtra `function_response` (after_tool_callback/plugin o gateway).
- **Datos**: minimiza lo que devuelven las herramientas, redacta PII, **propaga la identidad del usuario**
  (evita el *confused deputy*).
- **HITL**: `FunctionTool(require_confirmation=predicado)`; en sesiones gestionadas considera
  `LongRunningFunctionTool` o pausa de grafo (`RequestInput`).

---

## 2. Práctica

| Actividad | Dónde | Se califica |
|---|---|---|
| Quiz (16 preguntas) | `preguntas.json` | `python -m evaluador quiz 5` |
| Lab 5.1 – Guardrails ADK | [`labs/guardrails/`](labs/README.md) | tests |
| Lab 5.2 – Matriz de controles | [`labs/controles/`](labs/README.md) | tests |
| Caso práctico | [`caso-practico.md`](caso-practico.md) | juez LLM |

## 3. Evaluación final

```bash
python -m evaluador sesion 5     # o /evaluar-sesion 5
```

Después: `python -m evaluador simulacro -n 50` 🎯
