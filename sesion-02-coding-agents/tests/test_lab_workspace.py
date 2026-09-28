"""Checks del Lab 2.1: personalizar un agente de código (Claude Code) de forma segura."""

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

WS = Path(__file__).resolve().parents[1] / "labs" / "lab-2.1-workspace"
CLAUDE = WS / ".claude"
PATRONES_SECRETO = re.compile(r"(sk-ant-|AIza[0-9A-Za-z_-]{10,}|-----BEGIN|ghp_[0-9A-Za-z]{10,}|\"private_key\")")


def _frontmatter(ruta: Path) -> tuple[dict, str]:
    texto = ruta.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", texto, re.S)
    assert m, f"{ruta.name} debe empezar con frontmatter YAML entre líneas ---"
    import yaml

    return yaml.safe_load(m.group(1)) or {}, m.group(2)


@pytest.fixture(scope="module")
def settings():
    return json.loads((CLAUDE / "settings.json").read_text(encoding="utf-8"))


# ---------- settings.json ----------

def test_usa_vertex_sin_api_key(settings):
    """settings.json enruta Claude Code a Google Cloud (CLAUDE_CODE_USE_VERTEX) y no guarda API keys."""
    env = settings.get("env", {})
    assert env.get("CLAUDE_CODE_USE_VERTEX") == "1", "Falta env.CLAUDE_CODE_USE_VERTEX = \"1\""
    assert env.get("ANTHROPIC_VERTEX_PROJECT_ID"), "Falta env.ANTHROPIC_VERTEX_PROJECT_ID"
    assert env.get("CLOUD_ML_REGION"), "Falta env.CLOUD_ML_REGION (p. ej. global o us-east5)"
    assert "ANTHROPIC_API_KEY" not in env, "Elimina ANTHROPIC_API_KEY: en Google Cloud se usa ADC"
    assert not PATRONES_SECRETO.search(json.dumps(settings)), "settings.json contiene algo que parece un secreto"


def test_modelo_fijado(settings):
    """El modelo está fijado a una versión concreta (costo y comportamiento predecibles)."""
    env = settings.get("env", {})
    modelo = env.get("ANTHROPIC_MODEL") or env.get("ANTHROPIC_DEFAULT_SONNET_MODEL") or env.get("ANTHROPIC_DEFAULT_OPUS_MODEL")
    assert modelo, "Fija el modelo con ANTHROPIC_MODEL o ANTHROPIC_DEFAULT_*_MODEL"
    assert modelo.lower() not in {"opus", "sonnet", "haiku", "default"}, "Usa un ID de versión, no un alias"


def test_permisos_minimo_privilegio(settings):
    """Nada de Bash(*) en allow; deny cubre secrets/, .env y terraform destroy."""
    perms = settings.get("permissions", {})
    allow = perms.get("allow", [])
    assert not any(a.strip() in {"Bash", "Bash(*)", "Bash(:*)"} for a in allow), "Bash(*) permite cualquier comando"
    deny = " ".join(perms.get("deny", []))
    assert re.search(r"Read\([^)]*secrets", deny), "Añade una regla deny de Read para ./secrets/**"
    assert re.search(r"Read\([^)]*\.env", deny), "Añade una regla deny de Read para ./.env"
    assert "terraform destroy" in deny, "Añade una regla deny para Bash(terraform destroy ...)"


def test_hooks_configurados(settings):
    """Hay un hook PreToolUse (Bash y Read) que ejecuta bloquear_peligrosos.py y un hook Stop."""
    hooks = settings.get("hooks", {})
    pre = hooks.get("PreToolUse", [])
    matchers = " ".join(h.get("matcher", "") for h in pre)
    comandos = " ".join(c.get("command", "") for h in pre for c in h.get("hooks", []))
    assert "Bash" in matchers and "Read" in matchers, "El matcher de PreToolUse debe cubrir Bash y Read (p. ej. \"Bash|Read\")"
    assert "bloquear_peligrosos.py" in comandos, "PreToolUse debe ejecutar .claude/hooks/bloquear_peligrosos.py"
    assert hooks.get("Stop"), "Añade un hook Stop (definition of done: correr tests antes de terminar)"


# ---------- hook ----------

def _ejecutar_hook(tool: str, entrada: dict) -> int:
    evento = {"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": entrada}
    proc = subprocess.run([sys.executable, str(CLAUDE / "hooks" / "bloquear_peligrosos.py")],
                          input=json.dumps(evento), capture_output=True, text=True, timeout=10)
    return proc.returncode


@pytest.mark.parametrize("comando", [
    "rm -rf /", "sudo rm -rf ./build", "terraform destroy -auto-approve",
    "gcloud projects delete mi-proyecto", "git push --force origin main", "git push -f",
    "cat secrets/sa.json", "cat .env",
])
def test_hook_bloquea_comandos_peligrosos(comando):
    """El hook bloquea (exit 2) comandos destructivos o que leen secretos."""
    assert _ejecutar_hook("Bash", {"command": comando}) == 2, f"Debería bloquear: {comando}"


@pytest.mark.parametrize("comando", ["ls -la", "pytest -q", "git push origin feature/x", "terraform plan"])
def test_hook_permite_comandos_seguros(comando):
    """El hook permite (exit 0) comandos normales de desarrollo."""
    assert _ejecutar_hook("Bash", {"command": "rm -rf /"}) == 2, "Primero implementa el bloqueo"
    assert _ejecutar_hook("Bash", {"command": comando}) == 0, f"No debería bloquear: {comando}"


def test_hook_bloquea_lectura_de_secretos():
    """El hook bloquea Read sobre secrets/ y .env, y permite código fuente."""
    assert _ejecutar_hook("Read", {"file_path": "/repo/secrets/key.json"}) == 2
    assert _ejecutar_hook("Read", {"file_path": "/repo/.env"}) == 2
    assert _ejecutar_hook("Read", {"file_path": "/repo/app/pedidos.py"}) == 0


# ---------- subagente, skill, MCP, memoria ----------

def test_subagente_revisor_minimo_privilegio():
    """El subagente revisor-seguridad solo puede leer/buscar (sin Edit/Write/Bash)."""
    ruta = CLAUDE / "agents" / "revisor-seguridad.md"
    assert ruta.exists(), "Crea .claude/agents/revisor-seguridad.md"
    fm, cuerpo = _frontmatter(ruta)
    assert fm.get("name") == "revisor-seguridad"
    assert len(str(fm.get("description", ""))) >= 30, "La description debe explicar cuándo usarlo"
    tools = fm.get("tools")
    assert tools, "Define 'tools' explícitamente (si lo omites hereda TODAS las herramientas)"
    tools = {t.strip() for t in (tools.split(",") if isinstance(tools, str) else tools)}
    assert tools <= {"Read", "Grep", "Glob"}, f"Herramientas de más: {tools - {'Read', 'Grep', 'Glob'}}"
    assert len(cuerpo.split()) >= 30, "Escribe el system prompt del revisor (qué revisa y cómo reporta)"


def test_skill_despliegue():
    """La skill desplegar-cloud-run describe un despliegue privado con service account dedicada."""
    ruta = CLAUDE / "skills" / "desplegar-cloud-run" / "SKILL.md"
    assert ruta.exists(), "Crea .claude/skills/desplegar-cloud-run/SKILL.md"
    fm, cuerpo = _frontmatter(ruta)
    assert fm.get("name") == "desplegar-cloud-run"
    assert "cloud run" in str(fm.get("description", "")).lower(), "La description debe mencionar Cloud Run"
    for requisito in ("gcloud run deploy", "--no-allow-unauthenticated", "--service-account"):
        assert requisito in cuerpo, f"El procedimiento debe incluir {requisito}"


def test_mcp_sin_secretos():
    """.mcp.json define al menos un servidor MCP y no contiene secretos en texto plano."""
    ruta = WS / ".mcp.json"
    assert ruta.exists(), "Crea .mcp.json en la raíz del workspace"
    cfg = json.loads(ruta.read_text(encoding="utf-8"))
    servidores = cfg.get("mcpServers", {})
    assert servidores, "Define al menos un servidor en mcpServers"
    assert not PATRONES_SECRETO.search(ruta.read_text(encoding="utf-8")), ".mcp.json contiene un secreto"
    for nombre, s in servidores.items():
        assert s.get("command") or s.get("url"), f"{nombre}: usa command (stdio) o url (http)"
        for seccion in ("env", "headers"):
            for k, v in (s.get(seccion) or {}).items():
                assert "${" in str(v), f"{nombre}.{seccion}.{k} debe referenciar una variable (${{VAR}}), no un valor literal"


def test_memoria_del_proyecto():
    """CLAUDE.md documenta cómo correr los tests del proyecto (pytest)."""
    texto = (WS / "CLAUDE.md").read_text(encoding="utf-8")
    assert "TODO" not in texto, "Completa CLAUDE.md"
    assert "pytest" in texto
