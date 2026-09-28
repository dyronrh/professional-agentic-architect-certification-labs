# 🎯 Labs de preparación · Google Cloud Professional Agentic Architect

Guía práctica en español para preparar la certificación
[Professional Agentic Architect](https://cloud.google.com/learn/certification/agentic-architect/):
**una sesión (carpeta) por dominio del examen**, cada una con teoría, preguntas estilo examen,
laboratorios con verificación automática, un caso práctico de arquitectura y un **agente evaluador**
que te califica al final.

| # | Sesión | Dominio del examen | Peso |
|---|---|---|---|
| 1 | [`sesion-01-low-code`](sesion-01-low-code/README.md) | Building agents using low-code tools | ~13 % |
| 2 | [`sesion-02-coding-agents`](sesion-02-coding-agents/README.md) | Using coding agents for application development | ~17 % |
| 3 | [`sesion-03-custom-agents`](sesion-03-custom-agents/README.md) | Developing custom agents | ~33 % ⭐ |
| 4 | [`sesion-04-evaluate-deploy`](sesion-04-evaluate-deploy/README.md) | Evaluating and deploying agentic workflows | ~22 % |
| 5 | [`sesion-05-security-governance`](sesion-05-security-governance/README.md) | Securing and governing agentic workflows | ~15 % |

📚 [Plan de estudio (5 semanas)](docs/plan-de-estudio.md) · 🧭 [Estrategia de examen](docs/estrategia-examen.md) ·
🔤 [Glosario y renombres 2026](docs/glosario-y-renombres.md)

---

## Estructura de cada sesión

```
sesion-0N-.../
├── README.md            teoría esencial, tablas de decisión y trampas del examen
├── preguntas.json       quiz estilo examen (inglés, explicaciones en español)
├── labs/                laboratorios: archivos con TODO que debes completar
├── tests/               checks automáticos de los labs (pytest)
├── caso-practico.md     escenario de arquitectura (respuesta abierta)
├── rubrica-caso.json    rúbrica con la que el juez califica el caso
├── respuestas/          TU trabajo: quiz.json (auto) + caso-practico.md
└── resultados/          reportes del evaluador (se crean al evaluar)
```

| Sesión | Labs (checks automáticos) |
|---|---|
| 1 | Flujo determinista estilo CX Agent Studio: pages, rutas, event handlers, escalamiento (9) |
| 2 | Workspace de Claude Code seguro sobre Google Cloud: settings, hook PreToolUse, subagente, skill, MCP (21) · Pod sandbox gVisor (7) |
| 3 | Agente multi-agente ADK: Parallel/Sequential/Loop, AgentTool, estado `user:`, callbacks (11) |
| 4 | Evalset y criterios de ADK, RunConfig/plugins de producción, comandos de deploy, decisiones de runtime y troubleshooting (28) |
| 5 | Guardrails ADK: PII, prompt injection directa e indirecta, SQL allowlist, HITL (25) · Matriz de controles de gobierno (13) |

## Puesta en marcha

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt           # pytest, pyyaml, google-adk (incluye google-genai)
python -m evaluador --help
pytest                                    # verifica que el evaluador funciona
```

Los labs y el quiz **no requieren nube ni gastan tokens**. Para los extras en la nube y el juez con
Gemini, configura un proyecto de pruebas (con alerta de presupuesto):

```bash
gcloud auth application-default login
export GOOGLE_GENAI_USE_VERTEXAI=true GOOGLE_CLOUD_PROJECT=mi-proyecto GOOGLE_CLOUD_LOCATION=us-central1
# alternativa: export GOOGLE_API_KEY=...   (AI Studio)
```

## Flujo de trabajo por sesión

```bash
# 1. Estudia sesion-0N/README.md
python -m evaluador quiz N --estudio     # 2. quiz con explicación inmediata
python -m evaluador labs N               # 3. completa labs/ hasta que todo esté en verde
#                                          4. responde respuestas/caso-practico.md
python -m evaluador quiz N               # 5. quiz en modo examen (cronometrado)
python -m evaluador sesion N             # 6. evaluación final → resultados/ultimo-reporte.md
python -m evaluador progreso             # avance global ponderado por el peso del examen
python -m evaluador simulacro -n 50      # al final: examen simulado mezclando dominios
```

## 🤖 El agente evaluador

La nota de cada sesión combina tres fuentes:

| Componente | Peso | Cómo se califica |
|---|---|---|
| Quiz | 50 % | determinista, desglosado por objetivo del examen |
| Labs | 30 % | tests de pytest (`tests/`) |
| Caso práctico | 20 % | **LLM-as-judge con rúbrica** (`rubrica-caso.json`) |

Aprobado = **≥ 70/100** (Google no publica la nota de corte; 70 es una meta de práctica). Si el caso
aún no está calificado, la nota se muestra como *provisional*.

Tres formas de ejecutar el juez del caso práctico — elige la que uses:

1. **Claude Code** (recomendado si estudias con Claude Code): `/evaluar-sesion N`.
   La skill delega en el subagente [`evaluador-certificacion`](.claude/agents/evaluador-certificacion.md),
   que corre el evaluador, califica el caso con la rúbrica y te resume qué estudiar.
   Extra: la skill `tutor-examen` te explica conceptos y te genera preguntas nuevas sobre tus puntos débiles.
2. **Gemini** (CLI): `python -m evaluador sesion N` usa Gemini automáticamente si configuraste
   credenciales (`JUEZ_MODELO` para cambiar el modelo, por defecto `gemini-flash-latest`).
3. **Agente ADK** (¡práctica del dominio 3!): `adk web evaluador` → elige `agente_evaluador`
   y pídele "evalúa mi sesión 3". Código en [`evaluador/agente_evaluador/agent.py`](evaluador/agente_evaluador/agent.py).

> `AGENTS.md` replica las instrucciones para Antigravity / Gemini CLI u otros agentes de código.

## 💡 Sugerencias para prepararte

1. **Empieza por la Sesión 3** (33 %) y la 4 (22 %): son más de la mitad del examen y la base de las demás.
2. **El examen tiene labs prácticos en Google Skills**: haz los extras "en la nube" de cada lab y el
   [learning path oficial](https://www.skills.google/paths/4525); la soltura en consola cuenta.
3. **Estudia con un agente de código** (Claude Code en Google Cloud o Antigravity) todo el tiempo:
   practicas el dominio 2 mientras estudias los demás.
4. **Aprende los renombres de 2026** ([glosario](docs/glosario-y-renombres.md)): el examen no usa "Vertex AI Agent Engine".
5. **Piensa en "determinista vs probabilístico"**: la mitad de las preguntas se resuelven
   descartando "ponlo en las instrucciones" cuando se exige una garantía.
6. **Practica en inglés** y con reloj (~2 min/pregunta). Haz las
   [sample questions oficiales](https://docs.google.com/forms/d/1fi1gqbWsNCFxm1CT9V-JNGff1lyqfU9kNWAaaQMvRi4/preview)
   al inicio (línea base) y al final.
7. **La beta cierra el 30 de septiembre** según la página oficial (consultada el 28-09-2026). Si no
   llegas, aprovecha el tiempo para la versión GA: este repo sigue sirviendo.
8. Comunidad: [Google Cloud Community](https://discuss.google.dev/c/google-cloud/14).

## ⚠️ Fuentes y límites

- Dominios y pesos: [página oficial de la certificación](https://cloud.google.com/learn/certification/agentic-architect/)
  y la [guía oficial del examen (PDF)](https://services.google.com/fh/files/misc/professional_agentic_architect_exam_guide_english.pdf).
  La numeración 1.1, 1.2, 2.1, 3.2, 4.1, 5.1 y 5.2 coincide con la guía oficial; el resto (2.2, 3.1, 3.3, 4.2)
  es una agrupación aproximada de este repo.
- Detalles de productos recientes (Agent Gateway, Agent Identity, Workflow Builder, renombres) provienen
  de guías comunitarias de 2026, p. ej.
  [vishal-bulbule/google-cloud-agentic-architect-exam-guide](https://github.com/vishal-bulbule/google-cloud-agentic-architect-exam-guide).
  **Contrasta con la documentación oficial**: los productos cambian rápido.
- Las preguntas son originales de práctica, no preguntas reales del examen.
- Los labs de ADK se verificaron con `google-adk` 2.10.
