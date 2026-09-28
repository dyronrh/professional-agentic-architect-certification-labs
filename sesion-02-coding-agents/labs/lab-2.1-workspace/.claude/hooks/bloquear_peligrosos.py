#!/usr/bin/env python3
"""Hook PreToolUse de Claude Code: bloquea acciones peligrosas de forma determinista.

Claude Code envía por stdin un JSON como:
  {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": "ls -la"}}
  {"hook_event_name": "PreToolUse", "tool_name": "Read", "tool_input": {"file_path": "/repo/secrets/key.json"}}

Contrato:
  - exit 0            → se permite la herramienta.
  - exit 2 + stderr   → se BLOQUEA; el texto de stderr se devuelve al modelo como motivo.

TODO (Lab 2.1): bloquea
  - Bash: `rm -rf`, `terraform destroy`, `gcloud projects delete`, `git push --force` / `git push -f`,
    y cualquier comando que lea algo dentro de `secrets/` o el archivo `.env`.
  - Read: cualquier file_path dentro de un directorio `secrets/` o que termine en `.env`.
  Todo lo demás debe permitirse (p. ej. `ls`, `pytest -q`, `git push origin feature`).
"""

import json
import sys


def main() -> int:
    evento = json.load(sys.stdin)
    # TODO: implementa la lógica de bloqueo.
    return 0


if __name__ == "__main__":
    sys.exit(main())
