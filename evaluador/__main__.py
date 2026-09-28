"""CLI del evaluador.  Uso: python -m evaluador <comando> [opciones]

Comandos:
  quiz N [--estudio]      Quiz interactivo de la sesión N (guarda respuestas/quiz.json).
  labs N                  Ejecuta solo los checks de laboratorio de la sesión N.
  caso N                  Muestra enunciado, rúbrica y tu respuesta (para un juez externo).
  sesion N [--juez ...]   Evaluación final de la sesión: quiz + labs + caso práctico → reporte.
  simulacro [-n 50]       Examen simulado mezclando dominios según su peso real.
  progreso                Tabla de avance y preparación ponderada.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from datetime import datetime

from . import banco, juez, labs, reporte
from .config import CARPETA_SIMULACROS, SESIONES, UMBRAL_APROBADO, sesion


def cmd_quiz(a: argparse.Namespace) -> None:
    s = sesion(a.n)
    preguntas = banco.cargar_preguntas(s)
    respuestas, segundos = banco.quiz_interactivo(preguntas, modo_estudio=a.estudio, semilla=a.semilla)
    ruta = banco.archivo_respuestas(s)
    banco.guardar_respuestas(ruta, respuestas, segundos)
    r = banco.calificar(preguntas, respuestas)
    print(f"\nResultado: {r.correctas}/{r.total} ({r.porcentaje:.0f}%) en {segundos / 60:.1f} min. "
          f"Respuestas guardadas en {ruta.relative_to(s.ruta.parent)}")
    print(f"Cuando termines labs y caso práctico: python -m evaluador sesion {a.n}")


def cmd_labs(a: argparse.Namespace) -> None:
    s = sesion(a.n)
    r = labs.ejecutar_labs(s)
    if r.error:
        print(r.error)
    for ch in r.checks:
        icono = {"ok": "✅", "fallo": "❌", "omitido": "⏭️"}[ch.estado]
        print(f"{icono} {ch.descripcion or ch.nombre}")
        if ch.detalle:
            print(f"     ↳ {ch.detalle}")
    print(f"\nLabs: {r.aprobados}/{r.total} ({r.porcentaje:.0f}%)")


def cmd_caso(a: argparse.Namespace) -> None:
    s = sesion(a.n)
    ruta = juez.archivo_respuesta(s)
    print(json.dumps({
        "sesion": s.numero,
        "enunciado": s.enunciado_caso.read_text(encoding="utf-8"),
        "rubrica": juez.cargar_rubrica(s),
        "respuesta": ruta.read_text(encoding="utf-8") if ruta.exists() else "",
        "archivo_calificacion": str(juez.archivo_calificacion(s)),
    }, ensure_ascii=False, indent=2))


def cmd_sesion(a: argparse.Namespace) -> None:
    s = sesion(a.n)
    preguntas = banco.cargar_preguntas(s)
    rq = banco.calificar(preguntas, banco.cargar_respuestas(banco.archivo_respuestas(s)))
    rl = labs.ejecutar_labs(s)
    rc = juez.evaluar_caso(s, "pendiente" if a.juez == "omitir" else a.juez)
    nota = reporte.calcular_nota(rq, rl, rc)
    contenido = reporte.generar_reporte(s, rq, rl, rc, nota)
    ruta = reporte.guardar_reporte(s, contenido)
    reporte.registrar_sesion(s, nota)
    if a.json:
        print(json.dumps({
            "sesion": s.numero, "nota": nota.total, "quiz": nota.quiz, "labs": nota.labs,
            "caso": nota.caso, "provisional": nota.provisional, "aprobado": nota.aprobado,
            "reporte": str(ruta),
        }, ensure_ascii=False))
    else:
        print(contenido)
        print(f"Reporte guardado en {ruta.relative_to(s.ruta.parent)}")


def cmd_simulacro(a: argparse.Namespace) -> None:
    rng = random.Random(a.semilla)
    numeros = [int(x) for x in a.sesiones.split(",")] if a.sesiones else list(SESIONES)
    pool = {n: banco.cargar_preguntas(sesion(n)) for n in numeros}
    peso_total = sum(SESIONES[n].peso_examen for n in numeros)
    elegidas: list[banco.Pregunta] = []
    for n in numeros:
        cuota = round(a.n * SESIONES[n].peso_examen / peso_total)
        elegidas += rng.sample(pool[n], min(cuota, len(pool[n])))
    respuestas, segundos = banco.quiz_interactivo(elegidas, modo_estudio=False, semilla=a.semilla)
    r = banco.calificar(elegidas, respuestas)
    falladas = {p.id for p, _ in r.falladas}
    por_dominio = {}
    for n in numeros:
        del_dominio = [p for p in elegidas if p.sesion == n]
        por_dominio[str(n)] = [sum(p.id not in falladas for p in del_dominio), len(del_dominio)]
    CARPETA_SIMULACROS.mkdir(exist_ok=True)
    ruta = CARPETA_SIMULACROS / f"simulacro-{datetime.now():%Y%m%d-%H%M%S}.md"
    lineas = [f"# Simulacro · {r.correctas}/{r.total} ({r.porcentaje:.1f}%) · {segundos / 60:.1f} min", "",
              "| Sesión | Aciertos |", "|---|---|"]
    lineas += [f"| {n} {SESIONES[int(n)].dominio_es} | {ok}/{t} |" for n, (ok, t) in por_dominio.items()]
    lineas += ["", "## Falladas", ""]
    for p, dada in r.falladas:
        lineas += [f"- **{p.id}** tu: {','.join(dada) or '—'} · correcta: {','.join(p.respuesta)} — {p.explicacion}"]
    ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    reporte.registrar_simulacro(r.porcentaje, r.total, segundos / 60, por_dominio)
    veredicto = "listo para el examen 🎯" if r.porcentaje >= 80 else (
        "cerca, refuerza dominios débiles" if r.porcentaje >= UMBRAL_APROBADO else "sigue practicando")
    print(f"\nSimulacro: {r.porcentaje:.1f}% → {veredicto}. Detalle en {ruta}")


def cmd_progreso(_: argparse.Namespace) -> None:
    print(reporte.resumen_progreso())


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="python -m evaluador", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    q = sub.add_parser("quiz"); q.add_argument("n", type=int)
    q.add_argument("--estudio", action="store_true", help="muestra la explicación tras cada pregunta")
    q.add_argument("--semilla", type=int); q.set_defaults(f=cmd_quiz)

    l = sub.add_parser("labs"); l.add_argument("n", type=int); l.set_defaults(f=cmd_labs)
    c = sub.add_parser("caso"); c.add_argument("n", type=int); c.set_defaults(f=cmd_caso)

    e = sub.add_parser("sesion"); e.add_argument("n", type=int)
    e.add_argument("--juez", choices=["auto", "gemini", "archivo", "omitir"], default="auto")
    e.add_argument("--json", action="store_true"); e.set_defaults(f=cmd_sesion)

    m = sub.add_parser("simulacro"); m.add_argument("-n", type=int, default=50)
    m.add_argument("--sesiones", help="ej. 3,4"); m.add_argument("--semilla", type=int)
    m.set_defaults(f=cmd_simulacro)

    g = sub.add_parser("progreso"); g.set_defaults(f=cmd_progreso)

    a = p.parse_args(argv)
    a.f(a)


if __name__ == "__main__":
    sys.exit(main())
