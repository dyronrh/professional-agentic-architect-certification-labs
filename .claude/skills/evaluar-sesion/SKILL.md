---
name: evaluar-sesion
description: Evalúa una sesión de práctica (1-5) de la certificación Professional Agentic Architect al terminarla - quiz, labs y caso práctico - delegando en el subagente evaluador-certificacion. Úsala cuando el usuario diga "evalúame", "califica la sesión N" o "/evaluar-sesion N".
---

# Evaluar sesión

El argumento es el número de sesión (1-5). Si no lo dan, pregúntalo.

1. Comprueba el estado sin revelar respuestas:
   - ¿Existe `sesion-0N-*/respuestas/quiz.json`? Si no, dile al usuario que primero haga el quiz en su
     terminal (es interactivo): `python -m evaluador quiz N`. Puedes continuar igualmente si lo pide
     (el quiz contará 0).
   - ¿`respuestas/caso-practico.md` tiene contenido más allá de la plantilla? Si no, avísale.
2. Delega la evaluación en el subagente **evaluador-certificacion** con el prompt:
   "Evalúa la sesión N siguiendo tu procedimiento."
3. Muestra al usuario el resumen del subagente tal cual y ofrece:
   - repasar en modo tutor los conceptos fallados (explicación + 2 preguntas nuevas de práctica
     sobre cada uno, sin dar la respuesta hasta que conteste), o
   - pasar a la siguiente sesión.

No modifiques archivos de `respuestas/` ni de `labs/` durante la evaluación.
