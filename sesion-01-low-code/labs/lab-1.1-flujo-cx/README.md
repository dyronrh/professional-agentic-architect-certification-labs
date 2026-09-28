# Lab 1.1 · Flujo determinista estilo CX Agent Studio

**Objetivo del examen:** 1.1 — configurar flujos basados en estados (pages, transition routes, event handlers).

En CX Agent Studio / Dialogflow CX un *flow* es una máquina de estados. Aquí la representamos en
`flujo.json` con un formato simplificado para que los tests puedan validarla sin consola.

## Escenario

Un banco quiere un agente de voz para **reponer tarjetas**. Requisitos de negocio:

1. Nadie llega a la página `SolicitarTarjeta` sin pasar por `Autenticacion`, **también** si dice "me robaron la tarjeta".
2. El `pin` es obligatorio y **nunca** debe aparecer en logs (redacción de parámetros sensibles).
3. `Autenticacion` llama al webhook `validar_cliente`, que fija `$session.params.autenticado` (`true`/`false`).
   Indícalo con el campo `"fija_parametro": "autenticado"` en esa ruta.
4. `Validacion` enruta **según el resultado del webhook**:
   `$session.params.autenticado = true` → `SolicitarTarjeta`; `$session.params.autenticado = false` → `Escalamiento`.
5. Si el webhook falla, la página debe manejar el evento `webhook.error`.
6. El flujo maneja `sys.no-match-default` y `sys.no-input-default`.
7. Al tercer no-match (`sys.no-match-3`) se transfiere a la página `Escalamiento`, que hace handoff a
   un agente humano (`"handoff_agente_humano": true`).
8. El flujo termina en `END_SESSION`.

## Formato

```jsonc
{
  "pagina_inicial": "Start",
  "event_handlers_flujo": [{"evento": "sys.no-input-default", "respuesta": "...", "destino": null}],
  "paginas": {
    "NombrePagina": {
      "parametros": [{"nombre": "x", "entidad": "@sys.any", "requerido": true, "redactar": false}],
      "rutas": [
        {"tipo": "intent", "intent": "nombre_intent", "destino": "OtraPagina"},
        {"tipo": "condicion", "condicion": "$session.params.x = true", "destino": "OtraPagina",
         "webhook": "opcional", "fija_parametro": "opcional"}
      ],
      "event_handlers": [{"evento": "webhook.error", "respuesta": "...", "destino": "Escalamiento"}],
      "handoff_agente_humano": false
    }
  }
}
```

`destino` puede ser una página, `END_SESSION`, `END_FLOW` o `null` (se queda en la página actual).

## Cómo verificar

```bash
python -m evaluador labs 1
```

## Para pensar (sale en el examen)

- ¿Por qué la ruta de condición `true` en `Validacion` es un agujero de seguridad?
- Si pusieras la ruta `$session.params.fraude = true` a nivel de flujo, ¿se evaluaría estando en
  `SolicitarTarjeta`? (Pista: scope de rutas del flujo fuera de la start page.)
- ¿Qué ganas modelando esto como flujo en lugar de instrucciones de un agente generativo? ¿Qué pierdes?

## Extra en la nube (recomendado)

Reproduce este flujo en la consola de CX Agent Studio (o Dialogflow CX) dentro de tu proyecto de
prueba, pruébalo en el simulador y exporta el agente. El examen incluye **labs prácticos en Google Skills**,
así que la soltura en consola cuenta.
