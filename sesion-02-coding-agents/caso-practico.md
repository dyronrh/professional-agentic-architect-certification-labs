# Caso práctico · Sesión 2 — Agentes de código en un banco regulado

**Objetivos:** 2.1 y 2.2 · **Tiempo sugerido:** 30-40 min · Responde en `respuestas/caso-practico.md`.

## Contexto

*Banco Austral* quiere que **300 desarrolladores** (40 repos) usen agentes de código
(Claude Code y Antigravity) a partir del próximo trimestre. Condiciones:

- El código fuente **no puede salir** del perímetro de Google Cloud del banco.
- No se permiten API keys personales; todo el consumo se factura y audita en Google Cloud.
- Seguridad exige que ningún agente pueda leer `secrets/`, borrar infraestructura ni hacer `push --force`,
  **aunque el modelo sea engañado por prompt injection** en un README de una dependencia.
- Los equipos quieren que el agente consulte esquemas de BigQuery y errores recientes de Cloud Logging.
- Un producto nuevo ejecutará **código Python generado por un LLM** enviado por clientes (miles de sesiones concurrentes).
- Plataforma quiere un camino estándar desde "el agente escribió un agente ADK" hasta
  "está desplegado, evaluado y publicado en Gemini Enterprise".

## Entregable

1. Entorno de desarrollo y red (dónde corre el agente, perímetro, egress).
2. Configuración de Claude Code / Antigravity sobre Google Cloud: autenticación, modelos, costos.
3. Controles deterministas vs orientativos: qué va en reglas/memoria, skills, hooks, permisos, subagentes.
4. Integración MCP con mínimo privilegio y sin secretos.
5. Distribución y gobierno a escala (40 repos, actualizaciones).
6. Sandbox para el código de clientes.
7. Inner loop → outer loop (evaluar, desplegar, publicar) en CI/CD.
