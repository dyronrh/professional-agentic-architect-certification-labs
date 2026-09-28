# Lab 2.1 · Configurar un agente de código seguro (Claude Code en Google Cloud)

**Objetivo del examen:** 2.1 — configurar agentes de código con MCP, skills, herramientas y controles.

Este directorio simula el repositorio de un equipo. Tu trabajo es dejarlo listo para que 300
desarrolladores usen Claude Code **facturado y gobernado desde Google Cloud**, con controles
deterministas. (En Antigravity / Gemini CLI los conceptos son los mismos, cambian rutas y formatos.)

## Tareas

1. **`.claude/settings.json`**
   - Quita la API key de Anthropic. Enruta a Google Cloud: `CLAUDE_CODE_USE_VERTEX=1`,
     `ANTHROPIC_VERTEX_PROJECT_ID`, `CLOUD_ML_REGION`.
   - Fija el modelo con un ID de versión (`ANTHROPIC_MODEL` o `ANTHROPIC_DEFAULT_*_MODEL`).
   - Permisos: elimina `Bash(*)`; añade `deny` para `Read(./secrets/**)`, `Read(./.env)` y
     `Bash(terraform destroy:*)`. Opcional: `allow` para `Bash(pytest:*)`.
   - Hooks: `PreToolUse` con matcher `"Bash|Read"` que ejecute
     `python3 .claude/hooks/bloquear_peligrosos.py`, y un hook `Stop` que corra los tests.
2. **`.claude/hooks/bloquear_peligrosos.py`** — implementa el TODO (exit 2 = bloquear).
3. **`.claude/agents/revisor-seguridad.md`** — subagente con `name`, `description` y `tools: Read, Grep, Glob`.
4. **`.claude/skills/desplegar-cloud-run/SKILL.md`** — skill con frontmatter `name`/`description` y
   un procedimiento que use `gcloud run deploy ... --no-allow-unauthenticated --service-account=...`.
5. **`.mcp.json`** — al menos un servidor MCP (p. ej. uno remoto de Google Cloud o uno local stdio);
   cualquier credencial debe ir como `${VARIABLE}`, nunca literal.
6. **`CLAUDE.md`** — reemplaza el TODO con las convenciones reales (tests con `pytest`, etc.).

Referencia de formato de hooks:

```json
{"hooks": {"PreToolUse": [{"matcher": "Bash|Read",
  "hooks": [{"type": "command", "command": "python3 .claude/hooks/bloquear_peligrosos.py"}]}]}}
```

## Verificar

```bash
python -m evaluador labs 2
# Prueba real: abre Claude Code dentro de este directorio y pídele "lee secrets/x.json".
```

## Preguntas de reflexión

- ¿Por qué un `PostToolUse` no sirve para *impedir* algo?
- ¿Qué pasa si el subagente no declara `tools`?
- ¿Cómo distribuirías esta configuración a 30 repos? (plugin + managed settings)
