# Estrategia para el día del examen

## Formato (según la página oficial, consultada el 2026-09-28)

- **Dos partes:** examen de opción múltiple supervisado (~80 preguntas, 3 h, Pearson, online u
  onsite) **+ labs prácticos** en Google Skills. Practica en consola, no solo teoría.
- Idioma: **inglés**. Por eso las preguntas de este repo están en inglés.
- Beta: 120 USD (precio normal 200), abierta **hasta el 30 de septiembre**; resultados 4-6 semanas
  después de cerrar las ventanas. Si no alcanzas la beta, prepárate para la versión GA.
- Experiencia recomendada: 3+ años en cloud, 1+ año construyendo soluciones agénticas en Google Cloud.

## Cómo leer una pregunta

1. **Identifica la restricción dominante** (suele estar al final): *"minimize operational overhead"*,
   *"must never"*, *"without redeploying"*, *"least privilege"*, *"lowest latency"*, *"data must not leave"*.
2. **Mapea palabras clave a la primitiva** (tablas "señal → respuesta" de cada README).
3. **Descarta distractores típicos:**
   - "Put it in the system prompt / instructions" cuando se exige garantía.
   - Service account compartida, Owner/Editor, llaves en código o en archivos del repo.
   - Fine-tuning para problemas de formato o de conocimiento que resuelve RAG.
   - Soluciones que funcionan pero con **más operación** de la necesaria (GKE cuando basta Agent Runtime).
   - Productos reales usados fuera de su propósito (A2A para sub-agentes locales, BigQuery para serving de baja latencia).
4. **Entre dos buenas, elige la gestionada y la de mínimo privilegio**, salvo que el enunciado pida control total.
5. **Choose 2**: cada opción debe ser correcta por sí sola.

## Gestión del tiempo

- ~2 min por pregunta. Marca y sigue si pasas de 3 min (el quiz del repo permite `m` para marcar).
- Primera pasada completa → segunda pasada solo marcadas → no cambies respuestas sin una razón concreta.

## Última semana

- Relee los reportes (`sesion-*/resultados/ultimo-reporte.md`) y solo los objetivos < 70 %.
- 2-3 simulacros cronometrados: `python -m evaluador simulacro -n 50`.
- Repasa el [glosario de renombres](glosario-y-renombres.md) el día anterior.
- Haz las *sample questions* oficiales otra vez y compara con tu línea base.
