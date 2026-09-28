"""Checks del Lab 1.1: flujo determinista estilo CX Agent Studio / Dialogflow CX."""

import json
from pathlib import Path

import pytest

RUTA = Path(__file__).resolve().parents[1] / "labs" / "lab-1.1-flujo-cx" / "flujo.json"
ESPECIALES = {"END_SESSION", "END_FLOW", None}


@pytest.fixture(scope="module")
def flujo():
    return json.loads(RUTA.read_text(encoding="utf-8"))


def _rutas(pagina):
    return pagina.get("rutas", [])


def _destinos(pagina):
    ds = [r.get("destino") for r in _rutas(pagina)]
    ds += [h.get("destino") for h in pagina.get("event_handlers", [])]
    return ds


def _grafo(flujo):
    g = {nombre: set() for nombre in flujo["paginas"]}
    handlers_flujo = [h.get("destino") for h in flujo.get("event_handlers_flujo", [])]
    for nombre, pagina in flujo["paginas"].items():
        for d in _destinos(pagina) + handlers_flujo:
            if d not in ESPECIALES:
                g[nombre].add(d)
    return g


def test_destinos_validos(flujo):
    """Todas las rutas y handlers apuntan a páginas existentes o a END_SESSION/END_FLOW."""
    paginas = set(flujo["paginas"])
    assert flujo["pagina_inicial"] in paginas
    todos = [h.get("destino") for h in flujo.get("event_handlers_flujo", [])]
    for p in flujo["paginas"].values():
        todos += _destinos(p)
    invalidos = [d for d in todos if d not in ESPECIALES and d not in paginas]
    assert not invalidos, f"Destinos que no existen: {invalidos}"


def test_autenticacion_antes_de_datos_de_tarjeta(flujo):
    """Ningún camino llega a SolicitarTarjeta sin pasar por Autenticacion."""
    g = _grafo(flujo)
    assert "SolicitarTarjeta" in g and "Autenticacion" in g
    # BFS desde Start evitando Autenticacion: SolicitarTarjeta no debe ser alcanzable.
    vistos, cola = set(), [flujo["pagina_inicial"]]
    while cola:
        actual = cola.pop()
        if actual in vistos or actual == "Autenticacion":
            continue
        vistos.add(actual)
        cola.extend(g.get(actual, ()))
    assert "SolicitarTarjeta" not in vistos, (
        "Existe un camino Start → SolicitarTarjeta que se salta la autenticación "
        "(revisa la ruta del intent tarjeta_robada)."
    )


def test_pin_es_requerido_y_redactado(flujo):
    """El parámetro pin es requerido y se redacta en logs (dato sensible)."""
    params = {p["nombre"]: p for p in flujo["paginas"]["Autenticacion"].get("parametros", [])}
    assert "pin" in params, "Falta el parámetro pin en Autenticacion"
    assert params["pin"].get("requerido") is True
    assert params["pin"].get("redactar") is True, "El PIN debe marcarse como redactado (redact in log)."


def test_validacion_usa_resultado_del_webhook(flujo):
    """Validacion enruta según $session.params.autenticado: true → SolicitarTarjeta, false → Escalamiento."""
    rutas = _rutas(flujo["paginas"]["Validacion"])
    condiciones = {r.get("condicion", "").replace(" ", ""): r.get("destino") for r in rutas}
    assert condiciones.get("$session.params.autenticado=true") == "SolicitarTarjeta", (
        "Falta la ruta con condición `$session.params.autenticado = true` → SolicitarTarjeta"
    )
    assert condiciones.get("$session.params.autenticado=false") == "Escalamiento", (
        "Falta la ruta con condición `$session.params.autenticado = false` → Escalamiento"
    )
    assert "true" not in condiciones, "Una condición literal `true` salta la validación: elimínala."


def test_handlers_no_match_y_no_input(flujo):
    """El flujo maneja sys.no-match-default y sys.no-input-default."""
    eventos = {h["evento"] for h in flujo.get("event_handlers_flujo", [])}
    faltan = {"sys.no-match-default", "sys.no-input-default"} - eventos
    assert not faltan, f"Faltan event handlers a nivel de flujo: {faltan}"


def test_escalamiento_tras_tres_fallos(flujo):
    """Tras 3 no-match se transfiere a la página Escalamiento con handoff a agente humano."""
    handlers = {h["evento"]: h for h in flujo.get("event_handlers_flujo", [])}
    assert handlers.get("sys.no-match-3", {}).get("destino") == "Escalamiento", (
        "Añade un handler `sys.no-match-3` con destino Escalamiento"
    )
    esc = flujo["paginas"].get("Escalamiento")
    assert esc is not None, "Crea la página Escalamiento"
    assert esc.get("handoff_agente_humano") is True, "Escalamiento debe tener handoff_agente_humano: true"


def test_webhook_con_manejo_de_error(flujo):
    """Toda página que llama un webhook maneja el evento webhook.error."""
    for nombre, pagina in flujo["paginas"].items():
        if any(r.get("webhook") for r in _rutas(pagina)):
            eventos = {h["evento"] for h in pagina.get("event_handlers", [])}
            assert "webhook.error" in eventos, f"La página {nombre} llama un webhook sin handler webhook.error"


def test_webhook_no_transiciona_directo(flujo):
    """La ruta que llama al webhook no salta directo a Validacion sin que el webhook fije el parámetro."""
    for r in _rutas(flujo["paginas"]["Autenticacion"]):
        if r.get("webhook"):
            assert r.get("fija_parametro") == "autenticado", (
                "Documenta que el webhook fija $session.params.autenticado (campo fija_parametro)"
            )


def test_flujo_termina(flujo):
    """Existe al menos una ruta que finaliza la sesión (END_SESSION)."""
    destinos = [d for p in flujo["paginas"].values() for d in _destinos(p)]
    assert "END_SESSION" in destinos
