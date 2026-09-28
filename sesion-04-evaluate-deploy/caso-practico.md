# Caso práctico · Sesión 4 — De piloto a producción

**Objetivos:** 4.1 y 4.2 · **Tiempo sugerido:** 40 min · Responde en `respuestas/caso-practico.md`.

## Contexto

*Tienda Nube* tiene un agente ADK de postventa en piloto (1 mes, 3.000 conversaciones reales en BigQuery).
Debe pasar a producción para **40.000 conversaciones/día** con picos de 10× en Cyber Day.

- Algunos flujos requieren un orden estricto de herramientas (verificar identidad → consultar pedido → reembolsar).
- Las respuestas abiertas ("recomiéndame un producto") no tienen una única respuesta correcta.
- En el piloto hubo: loops de varios minutos; pérdida de contexto al redeploy en Cloud Run; errores
  429 en Cyber Day de prueba; latencia creciente en conversaciones largas; una API de inventario solo
  accesible dentro de la VPC (conectada a on-prem).
- El equipo es de Python, pequeño y sin experiencia en Kubernetes. Negocio quiere poder hacer
  *canary* de nuevas versiones.

## Entregable

1. Estrategia de evaluación: fuentes del golden set, métricas por tipo de pregunta, umbrales.
2. Cómo integras la evaluación en CI/CD (qué corre en cada PR, qué en nightly, qué bloquea un release).
3. Monitoreo en producción y cómo cierras el ciclo con los datos reales.
4. Runtime elegido y configuración clave (escalado, concurrencia, sesiones/memoria, red privada, revisiones/canary).
5. Diagnóstico y corrección de cada problema del piloto (perilla específica).
6. Observabilidad: qué señales/trazas/métricas mirarías y dónde.
