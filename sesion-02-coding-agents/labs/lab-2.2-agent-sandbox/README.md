# Lab 2.2 · Sandbox para código generado por el agente (GKE + gVisor)

**Objetivo del examen:** 2.1 — usar agentes de código en sandboxes seguros (GKE, Cloud Run).

`sandbox-pod.yaml` ejecuta código Python **generado por un LLM**. Endurécelo:

| Requisito | Pista |
|---|---|
| Kernel aislado | `runtimeClassName: gvisor` + `nodeSelector: {sandbox.gke.io/runtime: gvisor}` |
| Sin credenciales | `automountServiceAccountToken: false` + KSA dedicada (no `default`) |
| Sin acceso al host | quita `hostNetwork` y `privileged`; `allowPrivilegeEscalation: false` |
| No root | `runAsNonRoot: true`, `readOnlyRootFilesystem: true`, `capabilities.drop: [ALL]` |
| Recursos | `resources.limits.cpu` y `memory` |
| Reproducible | imagen con versión o digest, nunca `:latest` |
| Tiempo máximo | `activeDeadlineSeconds` ≤ 300 |

Extra (no calificado): añade un `NetworkPolicy` que deniegue todo el egress salvo un proxy
permitido, y lee sobre **Agent Sandbox** (`SandboxTemplate`, `SandboxWarmPool`) para arranques
sub-segundo a escala.

```bash
python -m evaluador labs 2
```

**En la nube (opcional):** crea un clúster GKE con un node pool GKE Sandbox, aplica el manifest y
confirma con `kubectl get pod -o yaml` que corre con `gvisor`. Borra el clúster al terminar.
