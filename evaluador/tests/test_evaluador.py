"""Tests del propio evaluador y de la integridad del contenido (bancos de preguntas y rúbricas)."""

import json

import pytest

from evaluador import banco, juez, reporte
from evaluador.config import SESIONES
from evaluador.labs import ResultadoLabs, Check


@pytest.mark.parametrize("n", list(SESIONES))
def test_banco_de_preguntas_integro(n):
    s = SESIONES[n]
    preguntas = banco.cargar_preguntas(s)
    assert len(preguntas) >= 15
    ids = [p.id for p in preguntas]
    assert len(ids) == len(set(ids))
    for p in preguntas:
        assert p.id.startswith(f"S{n}-Q")
        assert p.objetivo.startswith(f"{n}.")
        assert len(p.opciones) >= 4
        assert set(p.respuesta) <= set(p.opciones), p.id
        assert p.explicacion.strip()
        if p.multiple:
            assert f"Choose {len(p.respuesta)}" in p.pregunta, p.id


def test_ids_unicos_entre_sesiones():
    ids = [p.id for s in SESIONES.values() for p in banco.cargar_preguntas(s)]
    assert len(ids) == len(set(ids))


def test_respuestas_correctas_bien_distribuidas():
    """Evita que siempre sea la misma letra (sesgo que se aprende sin estudiar)."""
    letras = [p.respuesta[0] for s in SESIONES.values() for p in banco.cargar_preguntas(s) if not p.multiple]
    assert max(letras.count(x) for x in set(letras)) / len(letras) < 0.8


@pytest.mark.parametrize("n", list(SESIONES))
def test_rubrica_y_caso(n):
    s = SESIONES[n]
    rub = juez.cargar_rubrica(s)
    ids = [c["id"] for c in rub["criterios"]]
    assert len(ids) == len(set(ids)) and all(c["puntos"] > 0 for c in rub["criterios"])
    assert s.enunciado_caso.exists()
    plantilla = (s.respuestas / "caso-practico.md").read_text(encoding="utf-8")
    assert juez.respuesta_vacia(plantilla), "La plantilla vacía no debe contar como respuesta"


@pytest.mark.parametrize("entrada,esperado", [("a", ["A"]), ("a, c", ["A", "C"]), ("CA", ["A", "C"]), (["b"], ["B"]), ("", [])])
def test_normalizar(entrada, esperado):
    assert banco.normalizar(entrada) == esperado


def test_calificar_quiz():
    s = SESIONES[1]
    preguntas = banco.cargar_preguntas(s)[:3]
    respuestas = {preguntas[0].id: preguntas[0].respuesta, preguntas[1].id: ["Z"]}
    r = banco.calificar(preguntas, respuestas)
    assert (r.correctas, r.total, r.sin_responder, len(r.falladas)) == (1, 3, 1, 2)


def test_juez_limita_puntos():
    rub = {"criterios": [{"id": "a", "puntos": 3}, {"id": "b", "puntos": 2}]}
    r = juez._desde_json({"criterios": [{"id": "a", "puntos": 9, "justificacion": ""}]}, rub, "archivo")
    assert [c.puntos_obtenidos for c in r.criterios] == [3, 0]
    assert r.porcentaje == 60


def _q(pct):
    return banco.ResultadoQuiz(total=10, correctas=int(pct / 10), sin_responder=0)


def _l(ok, total):
    return ResultadoLabs(checks=[Check(str(i), "", "ok" if i < ok else "fallo") for i in range(total)])


def test_nota_completa_y_provisional():
    caso = juez._desde_json({"criterios": [{"id": "a", "puntos": 1, "justificacion": ""}]},
                            {"criterios": [{"id": "a", "puntos": 1}]}, "archivo")
    n = reporte.calcular_nota(_q(80), _l(5, 10), caso)
    assert n.total == pytest.approx(80 * .5 + 50 * .3 + 100 * .2) and not n.provisional
    p = reporte.calcular_nota(_q(80), _l(5, 10), juez.ResultadoCaso("pendiente"))
    assert p.provisional and p.total == pytest.approx((80 * .5 + 50 * .3) / .8, abs=0.1) and not p.aprobado


def test_reporte_se_genera():
    s = SESIONES[2]
    preguntas = banco.cargar_preguntas(s)
    q = banco.calificar(preguntas, {})
    texto = reporte.generar_reporte(s, q, _l(1, 2), juez.ResultadoCaso("pendiente"),
                                    reporte.calcular_nota(q, _l(1, 2), juez.ResultadoCaso("pendiente")))
    assert "Sesión 2" in texto and "Preguntas falladas" in texto


def test_agente_evaluador_adk():
    pytest.importorskip("google.adk")
    from evaluador.agente_evaluador.agent import root_agent

    nombres = {t.__name__ for t in root_agent.tools}
    assert {"calificar_quiz_y_labs", "obtener_caso_practico", "registrar_calificacion_caso"} <= nombres
