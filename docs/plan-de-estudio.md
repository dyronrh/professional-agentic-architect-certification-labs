# Plan de estudio sugerido (5 semanas, ~8-10 h/semana)

El orden sigue el **peso** de cada dominio y sus dependencias (ADK primero, porque la evaluación,
el despliegue y la seguridad se construyen sobre él).

| Semana | Foco | Actividades | Meta |
|---|---|---|---|
| 0 (2 h) | Preparación | Crear proyecto GCP de pruebas + presupuesto con alertas, `pip install -r requirements.txt`, leer el [glosario](glosario-y-renombres.md), hacer las *sample questions* oficiales **sin estudiar** (línea base) | saber de dónde partes |
| 1 | **Sesión 3** – Agentes custom (33 %) | teoría, quiz modo estudio, Lab 3.1 + `adk web`, codelabs de ADK | sesión 3 ≥ 70 |
| 2 | **Sesión 4** – Evaluar y desplegar (22 %) | Lab 4.1/4.2, desplegar el agente de viajes en Agent Runtime y Cloud Run, ver trazas | sesión 4 ≥ 70 |
| 3 | **Sesión 2** – Agentes de código (17 %) + **Sesión 5** – Seguridad (15 %) | configurar Claude Code/Antigravity sobre GCP para todo tu estudio; Labs 2.x y 5.x | ambas ≥ 70 |
| 4 | **Sesión 1** – Low-code (13 %) | Workflow Builder, CX Agent Studio, data stores con ACL en consola | sesión 1 ≥ 70 |
| 5 | Repaso y simulacros | `simulacro -n 50` × 3 (días alternos), repasar reportes, *learning path* oficial en Google Skills, labs prácticos | simulacros ≥ 80 % |

## Rutina por sesión

```
README (teoría) ─► quiz --estudio ─► labs (tests) ─► lab en consola (opcional)
      ─► caso práctico ─► quiz (modo examen) ─► /evaluar-sesion N ─► repasar reporte
```

1. **Lee la teoría activamente**: tapa la columna derecha de cada tabla e intenta predecirla.
2. **Quiz en modo estudio** (`--estudio`): aprendes de cada explicación, incluidos los distractores.
3. **Labs**: intenta sin pistas 20 min; luego usa la skill `tutor-examen` para pistas graduales.
4. **Caso práctico**: escribe como si defendieras la arquitectura ante un comité; justifica lo que descartas.
5. **Quiz en modo examen** (sin `--estudio`) el día siguiente → mide retención real.
6. **Evaluación** → el reporte dice qué objetivos repasar. Repite la sesión si no llegas a 70.

## Presupuesto de nube

Casi todo el repo funciona **sin costo** (los tests no llaman a modelos). Para los extras en la nube:
- usa créditos del free trial, alertas de presupuesto y **borra los recursos al terminar cada lab**;
- `min_instances=0` en Agent Runtime/Cloud Run mientras estudias;
- clústeres GKE: créalos y bórralos el mismo día.
