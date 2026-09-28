#!/usr/bin/env bash
# Comandos de despliegue del agente de soporte (Lab 4.2). NO se ejecutan en los tests: se revisan.
# TODO: corrige ambos comandos siguiendo el README del lab.
set -euo pipefail
PROJECT="${PROJECT:?define PROJECT}"
REGION="${REGION:-us-central1}"
AGENT_RUNTIME_ID="${AGENT_RUNTIME_ID:-}"

desplegar_cloud_run() {
  adk deploy cloud_run \
    --project="$PROJECT" --region="$REGION" \
    --service_name=agente-soporte \
    --with_ui \
    sesion-04-evaluate-deploy/labs/agente_soporte
}

desplegar_agent_runtime() {
  adk deploy agent_engine \
    --project="$PROJECT" --region="$REGION" \
    sesion-04-evaluate-deploy/labs/agente_soporte
}

"${1:-desplegar_agent_runtime}"
