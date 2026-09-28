# Labs de preparación · Google Cloud Professional Agentic Architect

Repositorio de estudio en español: 5 sesiones (una por dominio del examen), cada una con teoría
(`README.md`), quiz estilo examen (`preguntas.json`), labs con tests (`labs/` + `tests/`), caso práctico
(`caso-practico.md` + `rubrica-caso.json`) y respuestas del candidato en `respuestas/`.
El evaluador vive en `evaluador/` (`python -m evaluador --help`).

## Cómo ayudar al usuario

- Responde en español. Las preguntas estilo examen van en inglés (el examen real es en inglés).
- **Eres tutor, no solucionador**: en labs y casos da pistas graduales; escribe la solución completa
  solo si el usuario lo pide explícitamente después de intentarlo.
- No edites `sesion-*/respuestas/` ni reveles `tests/_claves.json`.
- Para evaluar una sesión usa la skill `/evaluar-sesion N` (delegada al subagente `evaluador-certificacion`).
- Para explicar o practicar conceptos usa la skill `tutor-examen`.

## Comandos

```bash
python -m evaluador labs N         # checks de laboratorio
python -m evaluador sesion N       # evaluación completa + reporte
python -m pytest evaluador/tests   # tests del propio evaluador
```
