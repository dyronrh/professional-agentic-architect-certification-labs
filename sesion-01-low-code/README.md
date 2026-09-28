# Sesión 1 · Construir agentes con herramientas low-code (~13 %)

> *Section 1: Building agents using low-code tools*

| Objetivo | Qué evalúan |
|---|---|
| **1.1** Configurar flujos y comportamiento de agentes con herramientas low-code | Flujos por estados (pages, transition routes, event handlers) en Workflow Builder / CX Agent Studio; moldear comportamiento con instrucciones, ejemplos y variables |
| **1.2** Conectar datos empresariales a Gemini Enterprise | Consultar datos propietarios de forma segura (Gemini Enterprise, Agent Search); ingerir datos multimodales no estructurados (video, audio, imágenes) |

**Plan de la sesión (≈ 4-6 h):** leer teoría (45 min) → quiz en modo estudio → Lab 1.1 → lab en consola
(opcional pero recomendado) → caso práctico → evaluación final.

---

## 1. Teoría esencial

### 1.1 ¿Qué superficie low-code elijo?

| Superficie | Persona | Dónde vive el determinismo | Úsala para |
|---|---|---|---|
| **Workflow Builder** (antes *Agent Designer*) | Usuario de negocio, app web de Gemini Enterprise | Pasos del workflow, condiciones, loops, **aprobación humana** | Automatizar entre apps (Gmail → Jira → aprobación) |
| **Agent Studio** (antes *Vertex AI Studio* / *Agent Builder*) | Desarrollador, consola de Cloud | Diseño multi-agente; **exporta a código ADK** | Prototipar y pasar a código / Agent Runtime |
| **CX Agent Studio** (antes *Dialogflow CX* / CCAI) | Equipos de CX | Flows (pages, routes), handoff rules, callbacks | Voz/chat, telefonía, widget web |

> **Regla de oro:** las **instrucciones** son *probabilísticas*. Lo que "siempre / nunca" debe ocurrir se
> modela en **flujos, rutas, handoff rules o callbacks**.

### Máquina de estados (CX)

- **Page**: estado; recoge **parámetros** (form filling). Parámetros sensibles → *redact in log*.
- **Transition route**: intent route o **condition route** (`$session.params.x = true`). Puede llamar a
  un **webhook** (fulfillment).
- **Event handler**: `sys.no-match-default`, `sys.no-input-default`, `sys.no-match-3`, `webhook.error`,
  `webhook.error.timeout`…
- **Scope**: fuera de la start page, de las rutas **del flujo** solo siguen en scope las de **intent**.
- **Route groups** reutilizan rutas entre páginas.

### Moldear el comportamiento

| Mecanismo | Fortaleza | Costo |
|---|---|---|
| Instrucciones en prosa | Fáciles | Reglas "enterradas" se ignoran |
| Secciones / XML (`<constraints>`) | Mejor adherencia | Más largas |
| Few-shot | Fidelidad de formato | Tokens, sobreajuste |
| Variable **estática** | Máxima adherencia, contenido estable | Cambiarla invalida el cache |
| Variable **dinámica** | Cambia durante la sesión (p. ej. salida de una herramienta) | Menor adherencia |

Arreglar formato ≠ fine-tuning. Primero estructura + ejemplos + salida estructurada.

### 1.2 Datos empresariales en Gemini Enterprise

| | **Federado** | **Ingesta (data store)** |
|---|---|---|
| Frescura | Tiempo real | Según sincronización |
| Calidad de búsqueda | Menor (depende de la fuente) | Mayor (parsing, chunking, ranking) |
| Dónde quedan los datos | En la fuente | Se copian a Google Cloud |
| Permisos | Los aplica la fuente vía OAuth del usuario | ACLs sincronizadas + IdP |

**Trampas de ACL** (muy preguntadas):
- El control de acceso se define **al crear** el data store; no se "activa después".
- Los permisos IAM de la fuente **no se importan**: se envían metadatos de ACL (readers).
- La ingesta **periódica** de BigQuery / Cloud Storage **no aplica ACLs**; la one-time sí.
- Fuentes Microsoft 365 ingestadas → **Workforce Identity Federation** con Entra ID. Cambiar de IdP = recrear data stores.

**Parsers:** digital (texto nativo) · OCR (escaneados) · **layout** (tablas, columnas; chunking consciente del layout) · parsing con Gemini (layouts complejos).

**Multimodal:**
- Videos/audio para Q&A → GCS → Gemini genera transcripción/capítulos con timestamps → ingesta de documentos derivados con URI + ACL.
- Imágenes por descripción → **embeddings multimodales + búsqueda vectorial**.
- Videos largos → menos FPS para reducir tokens.

> ⚠️ Los productos se renombraron en 2026 (ver [glosario](../docs/glosario-y-renombres.md)). El examen usa los nombres nuevos.

---

## 2. Práctica

| Actividad | Archivo | Se califica |
|---|---|---|
| Quiz estilo examen (16 preguntas) | `preguntas.json` | `python -m evaluador quiz 1` |
| Lab 1.1 – Flujo determinista | [`labs/lab-1.1-flujo-cx/`](labs/lab-1.1-flujo-cx/README.md) | tests automáticos |
| Lab 1.2 – Consola (no calificado) | ver abajo | autoevaluación |
| Caso práctico | [`caso-practico.md`](caso-practico.md) → `respuestas/caso-practico.md` | juez LLM con rúbrica |

### Lab 1.2 en la nube (recomendado, ~1 h, costo bajo)

1. Crea una app de Gemini Enterprise en tu proyecto de prueba.
2. Crea un data store de Cloud Storage con **control de acceso**, sube 3 PDFs (uno escaneado) y compara el parser digital vs layout.
3. Crea un workflow en Workflow Builder con un paso de aprobación.
4. Anota en tu caso práctico qué observaste. **Borra los recursos al terminar.**

## 3. Evaluación final

```bash
python -m evaluador quiz 1          # modo examen (sin pistas)
python -m evaluador sesion 1        # quiz + labs + caso → reporte en resultados/
```

O en Claude Code: `/evaluar-sesion 1`.
