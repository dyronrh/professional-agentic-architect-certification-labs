# Caso práctico · Sesión 1 — Conocimiento empresarial en Gemini Enterprise

**Objetivos:** 1.1 y 1.2 · **Tiempo sugerido:** 30-40 min · Responde en `respuestas/caso-practico.md`.

## Contexto

*Andes Seguros* (4.000 empleados) quiere un asistente interno en **Gemini Enterprise**:

- **Identidad:** usan Microsoft Entra ID; el correo es Gmail/Google Workspace.
- **SharePoint Online:** 1,2 M documentos. Jurídico exige que los contratos de la sección *Litigios*
  **no salgan de Microsoft 365**. El resto sí puede copiarse a Google Cloud.
- **Pólizas escaneadas:** 300.000 PDFs de imagen con tablas y dos columnas, algunos de 700 páginas.
- **BigQuery:** tabla de siniestros; cada ajustador solo puede ver los siniestros de su región.
  Se actualiza cada hora.
- **Videos:** 1.500 h de capacitación; quieren preguntas del tipo "¿cómo se tasa un daño por granizo?"
  con cita del minuto exacto.
- **Proceso:** los analistas de negocio (sin programar) quieren automatizar: "cuando llegue un correo
  con un reclamo, crear el caso en el CRM, resumirlo y **pedir aprobación del supervisor** antes de
  responder al cliente".

## Entregable

Diseña la solución justificando cada decisión (qué eliges **y por qué descartas** la alternativa):

1. Configuración de identidad (IdP) y en qué orden hacerla.
2. Estrategia por fuente: federado vs. ingesta, conector, parser y chunking.
3. Cómo garantizas los permisos por usuario/región en cada fuente (incluye las trampas de ACL que conoces).
4. Pipeline para los videos.
5. Superficie low-code para la automatización de reclamos y cómo garantizas la aprobación humana.
6. Dos riesgos o límites del diseño y cómo los mitigas.
