# Caso práctico · Sesión 3 — Plataforma de agentes para una aseguradora

**Objetivos:** 3.1, 3.2 y 3.3 · **Tiempo sugerido:** 45 min · Responde en `respuestas/caso-practico.md`.

## Contexto

*Andes Seguros* construirá con **ADK** un sistema multi-agente de siniestros:

1. **Recepción** conversa con el cliente (chat y voz), 200.000 conversaciones/día; debe recordar al
   cliente entre conversaciones (vehículos, preferencias de contacto) sin repetir hechos.
2. **Validación de póliza** responde preguntas sobre 80.000 pólizas en PDF (tablas de coberturas) y
   debe encontrar tanto conceptos ("¿cubre granizo?") como códigos exactos ("CL-AUTO-7781").
3. **Proceso de siniestro**: verificación de fraude **siempre primero**, aprobación automática bajo
   USD 500, revisión humana sobre ese monto, notificación final. Hoy es un único LLM con una
   instrucción de 3 páginas que a veces se salta el fraude.
4. **Pagos** es un agente de **otro equipo**, en otro proyecto, escrito en otro framework.
5. Los agentes usan herramientas del CRM (servidor MCP interno en Cloud Run) y BigQuery.
6. Seguridad exige saber **qué agente** accedió a qué dato; hoy todos comparten una service account.
7. El catálogo de repuestos (precio e inventario cambian cada segundo) debe consultarse con búsqueda
   semántica + filtros SQL.

## Entregable

1. Arquitectura de agentes y primitivas ADK (qué es LlmAgent, workflow/grafo, AgentTool, sub-agente) y por qué.
2. Selección de modelos por agente (costo/latencia vs razonamiento).
3. Sesiones, estado y memoria de largo plazo (servicios y prefijos de estado).
4. Estrategia de conocimiento (RAG): producto de retrieval por fuente, parsing/chunking, híbrida, reranking.
5. Interoperabilidad: MCP vs A2A, Agent Registry, cómo se descubren las herramientas y agentes.
6. Identidad y mínimo privilegio por agente (incluye qué pasa al recrear un agente).
7. Dos trade-offs que aceptas conscientemente.
