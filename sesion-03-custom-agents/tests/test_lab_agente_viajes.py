"""Checks del Lab 3.1: agente multi-agente con ADK (workflow agents, estado, herramientas, callbacks)."""

import importlib
import inspect
import sys
from pathlib import Path

import pytest

pytest.importorskip("google.adk", reason="Instala google-adk: pip install -r requirements.txt")

from google.adk.agents import LlmAgent, LoopAgent, ParallelAgent, SequentialAgent  # noqa: E402
from google.adk.tools.agent_tool import AgentTool  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "labs"))


class _Tool:
    def __init__(self, name):
        self.name = name


class _Ctx:
    """Doble de ToolContext: solo expone .state como dict."""

    def __init__(self, state=None):
        self.state = dict(state or {})


@pytest.fixture(scope="module")
def m():
    return importlib.import_module("agente_viajes.agent")


@pytest.fixture(scope="module")
def tools():
    return importlib.import_module("agente_viajes.tools")


@pytest.fixture(scope="module")
def callbacks():
    return importlib.import_module("agente_viajes.callbacks")


def _nombres_tools(agente):
    nombres = []
    for t in agente.tools:
        nombres.append(getattr(t, "__name__", None) or getattr(t, "name", type(t).__name__))
    return nombres


# ---------- herramientas ----------

def test_contrato_buscar_vuelos(tools):
    """buscar_vuelos tiene parámetros tipados (origen, destino, fecha) y docstring con Args."""
    firma = inspect.signature(tools.buscar_vuelos)
    params = firma.parameters
    assert list(params)[:3] == ["origen", "destino", "fecha"], "Parámetros esperados: origen, destino, fecha"
    assert all(params[p].annotation is str for p in ("origen", "destino", "fecha")), "Tipa los parámetros como str"
    assert not any(p.kind == p.VAR_KEYWORD for p in params.values()), "Nada de **kwargs: el modelo no sabe qué enviar"
    assert "Args:" in (tools.buscar_vuelos.__doc__ or ""), "Documenta los argumentos (ADK usa el docstring)"


def test_buscar_vuelos_respuesta_estructurada(tools):
    """buscar_vuelos devuelve status success/error con datos o mensaje."""
    ok = tools.buscar_vuelos("SCL", "LIM", "2026-11-02")
    assert ok["status"] == "success" and len(ok["vuelos"]) == 2
    sin_ruta = tools.buscar_vuelos("SCL", "MAD", "2026-11-02")
    assert sin_ruta["status"] == "error" and sin_ruta.get("error_message")
    invalido = tools.buscar_vuelos("Santiago", "LIM", "2026-11-02")
    assert invalido["status"] == "error", "Valida que los códigos sean IATA de 3 letras"


def test_preferencia_persiste_entre_sesiones(tools):
    """guardar_preferencia usa el prefijo user: (persiste en todas las sesiones del usuario)."""
    ctx = _Ctx()
    r = tools.guardar_preferencia("asiento", "ventana", ctx)
    assert r["status"] == "success"
    assert ctx.state.get("user:asiento") == "ventana", f"Estado resultante: {ctx.state}"


# ---------- callback ----------

def test_callback_bloquea_sobre_presupuesto(callbacks):
    """validar_presupuesto bloquea reservar_hotel si el total supera user:presupuesto."""
    ctx = _Ctx({"user:presupuesto": 500.0})
    r = callbacks.validar_presupuesto(_Tool("reservar_hotel"), {"hotel": "X", "precio_noche": 200.0, "noches": 3}, ctx)
    assert isinstance(r, dict) and r.get("status") == "error", "Debe devolver un dict de error para omitir la herramienta"


def test_callback_permite_casos_validos(callbacks):
    """validar_presupuesto devuelve None dentro del presupuesto, sin presupuesto o para otras herramientas."""
    ctx = _Ctx({"user:presupuesto": 500.0})
    assert callbacks.validar_presupuesto(_Tool("reservar_hotel"), {"hotel": "X", "precio_noche": 900.0, "noches": 3}, ctx), (
        "Primero implementa el bloqueo")
    assert callbacks.validar_presupuesto(_Tool("reservar_hotel"), {"hotel": "X", "precio_noche": 100.0, "noches": 3}, ctx) is None
    assert callbacks.validar_presupuesto(_Tool("reservar_hotel"), {"hotel": "X", "precio_noche": 900.0, "noches": 3}, _Ctx()) is None
    assert callbacks.validar_presupuesto(_Tool("buscar_vuelos"), {"origen": "SCL"}, ctx) is None


# ---------- composición ----------

def test_busqueda_paralela(m):
    """busqueda_paralela es un ParallelAgent con los dos investigadores y output_keys distintos."""
    bp = getattr(m, "busqueda_paralela", None)
    assert isinstance(bp, ParallelAgent), "Define busqueda_paralela = ParallelAgent(...)"
    nombres = {a.name for a in bp.sub_agents}
    assert nombres == {"investigador_vuelos", "investigador_hoteles"}
    claves = {a.name: a.output_key for a in bp.sub_agents}
    assert claves == {"investigador_vuelos": "vuelos", "investigador_hoteles": "hoteles"}, (
        f"output_keys actuales {claves}: en paralelo, claves iguales se pisan (race condition)"
    )


def test_redactor_lee_estado(m):
    """El redactor inyecta {vuelos} y {hoteles} y escribe en output_key 'borrador'."""
    assert "{vuelos}" in m.redactor.instruction and "{hoteles}" in m.redactor.instruction
    assert m.redactor.output_key == "borrador"


def test_loop_con_tope_y_salida(m):
    """refinamiento es un LoopAgent [critico, refinador] con max_iterations 1-5 y el crítico puede salir con exit_loop."""
    loop = getattr(m, "refinamiento", None)
    assert isinstance(loop, LoopAgent), "Define refinamiento = LoopAgent(...)"
    assert [a.name for a in loop.sub_agents] == ["critico", "refinador"]
    assert loop.max_iterations and 1 <= loop.max_iterations <= 5, "Sin max_iterations el loop puede no terminar"
    assert "exit_loop" in _nombres_tools(m.critico), "El crítico necesita la herramienta exit_loop"


def test_pipeline_secuencial(m):
    """planificador es un SequentialAgent: busqueda_paralela → redactor → refinamiento."""
    p = getattr(m, "planificador", None)
    assert isinstance(p, SequentialAgent), "Define planificador = SequentialAgent(...)"
    assert [a.name for a in p.sub_agents] == ["busqueda_paralela", "redactor", "refinamiento"]


def test_root_agent(m):
    """concierge usa AgentTool(planificador), las herramientas de estado/reserva y el callback de presupuesto."""
    root = m.root_agent
    assert isinstance(root, LlmAgent) and root.name == "concierge"
    agent_tools = [t for t in root.tools if isinstance(t, AgentTool)]
    assert agent_tools and agent_tools[0].agent is m.planificador, "Envuelve el planificador con AgentTool"
    nombres = set(_nombres_tools(root))
    assert {"guardar_preferencia", "registrar_presupuesto", "reservar_hotel"} <= nombres
    assert root.before_tool_callback is m.validar_presupuesto or root.before_tool_callback == [m.validar_presupuesto]
    assert len(root.instruction.split()) >= 25, "Escribe instrucciones claras: rol, cuándo usar cada herramienta, formato"


def test_modelo_segun_tarea(m):
    """Los investigadores usan el modelo rápido; redactor y crítico, el de razonamiento."""
    assert m.investigador_vuelos.model == m.MODELO_RAPIDO == m.investigador_hoteles.model
    assert m.redactor.model == m.MODELO_RAZONAMIENTO == m.critico.model
