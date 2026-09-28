# Caso práctico · Sesión 5 — Gobierno de una flota de agentes

**Objetivos:** 5.1 y 5.2 · **Tiempo sugerido:** 40 min · Responde en `respuestas/caso-practico.md`.

## Contexto

*Banco Austral* tendrá **25 agentes** en Agent Runtime y Cloud Run (atención, fraude, cobranzas, RR. HH.):

- Hoy todos usan la misma service account con `roles/editor`.
- El agente de atención lee correos y páginas web de clientes (riesgo de inyección indirecta) y puede
  emitir reembolsos y enviar correos.
- El agente de RR. HH. responde con documentos internos; cada empleado debe ver solo lo que ya puede ver.
- Cobranzas llama un CRM SaaS: acciones en nombre del ejecutivo conectado y un batch nocturno sin usuario.
  Un proveedor de scoring solo entrega una API key estática.
- Un MCP interno en Cloud Run expone `consultar_cliente`, `actualizar_cliente` y `borrar_cliente`.
- Regulador: datos de clientes no pueden salir del perímetro; auditoría de **qué agente** hizo **qué** y
  **en nombre de quién**; reglas comerciales que cambian cada trimestre.
- El CISO quiere protecciones mínimas contra prompt injection y PII que ningún equipo pueda rebajar.

## Entregable

1. Identidad de los agentes y modelo de permisos (incluye límites que ningún rol pueda superar).
2. Autenticación hacia cada destino (Google APIs, MCP en Cloud Run, SaaS delegado, SaaS batch, API key).
3. Control de herramientas MCP y del tráfico saliente; registro y auditoría.
4. Guardrails de contenido en capas (entrada, salida, herramientas) y acciones que requieren humano.
5. Protección de datos: perímetro, PII, propagación de identidad para RR. HH.
6. Plan de despliegue de las políticas sin romper producción.
