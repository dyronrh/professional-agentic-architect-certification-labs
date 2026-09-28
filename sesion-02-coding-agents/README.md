# Sesión 2 · Usar agentes de código para desarrollar aplicaciones (~17 %)

> *Section 2: Using coding agents for application development*

| Objetivo | Qué evalúan |
|---|---|
| **2.1** Usar agentes de código de forma efectiva | Configurar agentes de código (Antigravity, Claude Code en Google Cloud) con servidores MCP, skills y herramientas; ejecutarlos en sandboxes seguros (GKE, Cloud Run) |
| **2.2** Integrarlos al ciclo de desarrollo *(numeración aproximada)* | Inner loop (agente escribe código) → outer loop (Agents CLI / `adk`: evaluar, desplegar, publicar), CI/CD, contexto y convenciones |

**Plan (≈ 5-6 h):** teoría → quiz modo estudio → Lab 2.1 → Lab 2.2 → caso práctico → evaluación.

---

## 1. Teoría esencial

### Las 7 primitivas de personalización (pregunta segura en el examen)

| Necesidad (palabras clave del enunciado) | Primitiva | Claude Code | Antigravity / Gemini CLI* |
|---|---|---|---|
| Convenciones, contexto, "guía" | **Regla / memoria** | `CLAUDE.md`, `.claude/rules/` | `AGENTS.md`, `.agents/rules/*.md` |
| Procedimiento repetible con scripts, `/comando` | **Skill** | `.claude/skills/<n>/SKILL.md` | `.agents/skills/<n>/SKILL.md` |
| "Garantizar", "bloquear", "nunca", auditar | **Hook** (+ permisos deny) | `hooks` en `.claude/settings.json` | `.agents/hooks.json` |
| Contexto aislado, herramientas restringidas, paralelo | **Subagente** | `.claude/agents/<n>.md` | `.agents/agents/<n>.md` |
| Datos vivos / acciones en sistemas externos | **Servidor MCP** | `.mcp.json` | `mcp_config.json` |
| Distribuir todo junto a N equipos | **Plugin** | marketplace de plugins | `.agents/plugins/` |
| Qué puede hacer sin preguntar | **Permisos** | `permissions.allow/ask/deny` | `action(target)`, Deny > Ask > Allow |

\* Rutas de Antigravity según guías comunitarias de 2026: **verifícalas en la documentación oficial**.

**Hooks: cuál bloquea**

| Evento | Momento | ¿Bloquea? | Uso típico |
|---|---|---|---|
| `PreToolUse` | antes de la herramienta | ✅ | impedir comandos/lecturas peligrosas |
| `PostToolUse` | después | ❌ (ya ocurrió) | lint, auditoría |
| `Stop` | cuando el agente quiere terminar | ✅ (lo hace continuar) | "no terminar hasta que pasen los tests" |
| `UserPromptSubmit` / `SessionStart` | antes del turno / inicio | inyectan contexto | recordatorios, setup |

> Claude Code: el hook bloquea con **exit code 2** (stderr vuelve al modelo) o con JSON de decisión.
> Antigravity: devuelve JSON `{"decision": "deny"}`. La idea que evalúan: **hooks y permisos = determinista; reglas = orientativo**.

### Claude Code sobre Google Cloud

```bash
export CLAUDE_CODE_USE_VERTEX=1
export ANTHROPIC_VERTEX_PROJECT_ID=mi-proyecto    # facturación/cuotas
export CLOUD_ML_REGION=global                      # o una región por residencia de datos
gcloud auth application-default login              # ADC; en CI: Workload Identity Federation
```

- IAM mínimo: `roles/aiplatform.user`. Sin API keys de Anthropic.
- Fija versiones de modelo (`ANTHROPIC_MODEL`, `ANTHROPIC_DEFAULT_*_MODEL`) para costo/comportamiento predecibles.
- Prompt caching activado por defecto; políticas comunes vía *managed settings* de la organización.

### Dónde ejecutar código del agente (aislamiento)

| Opción | Unidad | Aislamiento | Cuándo |
|---|---|---|---|
| Sandbox local del agente | comando | namespaces/seatbelt del SO | laptop del dev |
| **Cloud Workstations** privadas | desarrollador | contenedor en VM + **VPC-SC**, sin IP pública, proxy de egress | "el código no sale del perímetro" |
| **GKE Agent Sandbox** (gVisor) | sesión | kernel en espacio de usuario, warm pools (<1 s) | código **no confiable** a escala |
| Cloud Run | request/instancia | contenedor gestionado (sandbox gVisor de 1ª gen / microVM de 2ª gen) | servicios/MCP propios; SA dedicada, nunca la default |

Manifest seguro: `runtimeClassName: gvisor`, `automountServiceAccountToken: false`, `runAsNonRoot`,
`allowPrivilegeEscalation: false`, `limits`, egress restringido.

### Inner loop → outer loop

`agente de código escribe ADK` → `adk eval` / Agents CLI `eval` → `deploy` (Agent Runtime, Cloud Run, GKE)
→ registro (Agent Registry) → publicar en Gemini Enterprise. En CI: modo no interactivo, allowlist de
comandos, cuentas de servicio con mínimo privilegio. **Nunca** "saltar todos los permisos" en máquinas compartidas.

---

## 2. Práctica

| Actividad | Dónde | Se califica |
|---|---|---|
| Quiz (16 preguntas) | `preguntas.json` | `python -m evaluador quiz 2` |
| Lab 2.1 – Workspace seguro de Claude Code | [`labs/lab-2.1-workspace/`](labs/lab-2.1-workspace/README.md) | tests |
| Lab 2.2 – Pod sandbox gVisor | [`labs/lab-2.2-agent-sandbox/`](labs/lab-2.2-agent-sandbox/README.md) | tests |
| Caso práctico | [`caso-practico.md`](caso-practico.md) | juez LLM |

**Práctica real sugerida:** usa este mismo repo con Claude Code (o Antigravity) configurado contra tu
proyecto de Google Cloud durante todo el estudio. Es la mejor forma de interiorizar el dominio.

## 3. Evaluación final

```bash
python -m evaluador sesion 2     # o en Claude Code: /evaluar-sesion 2
```
