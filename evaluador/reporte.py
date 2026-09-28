"""Cálculo de la nota de sesión, reporte Markdown y registro de progreso."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .banco import ResultadoQuiz
from .config import (
    ARCHIVO_PROGRESO, PESO_CASO, PESO_LABS, PESO_QUIZ, SESIONES, UMBRAL_APROBADO, Sesion,
)
from .juez import ResultadoCaso
from .labs import ResultadoLabs


@dataclass
class Nota:
    quiz: float
    labs: float
    caso: float | None  # None = pendiente
    total: float
    provisional: bool

    @property
    def aprobado(self) -> bool:
        return self.total >= UMBRAL_APROBADO and not self.provisional


def calcular_nota(q: ResultadoQuiz, l: ResultadoLabs, c: ResultadoCaso) -> Nota:
    caso = c.porcentaje if c.calificado else None
    if caso is None:
        total = (q.porcentaje * PESO_QUIZ + l.porcentaje * PESO_LABS) / (PESO_QUIZ + PESO_LABS)
    else:
        total = q.porcentaje * PESO_QUIZ + l.porcentaje * PESO_LABS + caso * PESO_CASO
    return Nota(q.porcentaje, l.porcentaje, caso, round(total, 1), caso is None)


def _barra(pct: float, ancho: int = 20) -> str:
    llenos = round(pct / 100 * ancho)
    return "█" * llenos + "░" * (ancho - llenos)


def generar_reporte(s: Sesion, q: ResultadoQuiz, l: ResultadoLabs, c: ResultadoCaso, n: Nota) -> str:
    estado = "✅ APROBADA" if n.aprobado else ("🟡 PROVISIONAL" if n.provisional else "❌ NO APROBADA")
    lineas = [
        f"# Reporte · Sesión {s.numero}: {s.dominio_es}",
        f"_{s.dominio} · ~{s.peso_examen}% del examen · {datetime.now():%Y-%m-%d %H:%M}_",
        "",
        f"## Nota: **{n.total:.1f}/100** — {estado} (umbral {UMBRAL_APROBADO:.0f})",
        "",
        "| Componente | Peso | Resultado |",
        "|---|---|---|",
        f"| Quiz estilo examen | {PESO_QUIZ:.0%} | {n.quiz:.1f}% ({q.correctas}/{q.total}) `{_barra(n.quiz)}` |",
        f"| Laboratorios | {PESO_LABS:.0%} | {n.labs:.1f}% ({l.aprobados}/{l.total} checks) `{_barra(n.labs)}` |",
        f"| Caso práctico | {PESO_CASO:.0%} | "
        + (f"{n.caso:.1f}% (juez: {c.fuente}) `{_barra(n.caso)}`" if n.caso is not None else "pendiente")
        + " |",
        "",
    ]
    if n.provisional:
        lineas += ["> Nota provisional: el caso práctico no está calificado, se reponderó quiz + labs.", ""]

    lineas += ["## Quiz por objetivo del examen", "", "| Objetivo | Aciertos | % |", "|---|---|---|"]
    for obj, (ok, tot) in sorted(q.por_objetivo.items()):
        pct = 100 * ok / tot
        marca = " ⚠️" if pct < UMBRAL_APROBADO else ""
        lineas.append(f"| {obj} | {ok}/{tot} | {pct:.0f}%{marca} |")
    if q.sin_responder:
        lineas += ["", f"> {q.sin_responder} preguntas sin responder (cuentan como incorrectas)."]
    if q.falladas:
        lineas += ["", "### Preguntas falladas", ""]
        for p, dada in q.falladas:
            lineas += [
                f"<details><summary><b>{p.id}</b> ({p.concepto}) — tu respuesta: "
                f"{','.join(dada) or '—'} · correcta: {','.join(p.respuesta)}</summary>",
                "",
                p.pregunta,
                "",
                *[f"- **{k}.** {v}" for k, v in p.opciones.items()],
                "",
                f"**Por qué:** {p.explicacion}",
                "</details>",
                "",
            ]

    lineas += ["", "## Laboratorios", ""]
    if l.error:
        lineas += ["```", l.error, "```"]
    for ch in l.checks:
        icono = {"ok": "✅", "fallo": "❌", "omitido": "⏭️"}[ch.estado]
        texto = ch.descripcion or ch.nombre
        lineas.append(f"- {icono} {texto}" + (f"  \n  ↳ `{ch.detalle}`" if ch.detalle else ""))

    lineas += ["", "## Caso práctico", ""]
    if c.criterios and c.fuente != "sin_respuesta":
        lineas += ["| Criterio | Puntos | Justificación |", "|---|---|---|"]
        for cr in c.criterios:
            lineas.append(f"| {cr.id} | {cr.puntos_obtenidos:g}/{cr.puntos_max:g} | {cr.justificacion} |")
        lineas.append("")
    if c.retroalimentacion:
        lineas += [c.retroalimentacion, ""]

    lineas += ["## Siguientes pasos", ""]
    debiles = [o for o, (ok, t) in q.por_objetivo.items() if 100 * ok / t < UMBRAL_APROBADO]
    if debiles:
        lineas.append(f"- Repasa la teoría de los objetivos {', '.join(sorted(debiles))} en el README de la sesión.")
    if l.porcentaje < 100:
        lineas.append("- Termina los checks de laboratorio en rojo: `python -m evaluador labs "
                      f"{s.numero}` muestra el detalle.")
    if q.falladas:
        lineas.append(f"- Repite el quiz en modo estudio: `python -m evaluador quiz {s.numero} --estudio`.")
    if n.aprobado:
        lineas.append("- ¡Bien! Pasa a la siguiente sesión y al final haz un `simulacro`.")
    return "\n".join(lineas) + "\n"


def guardar_reporte(s: Sesion, contenido: str) -> Path:
    s.resultados.mkdir(parents=True, exist_ok=True)
    ruta = s.resultados / f"reporte-{datetime.now():%Y%m%d-%H%M%S}.md"
    ruta.write_text(contenido, encoding="utf-8")
    (s.resultados / "ultimo-reporte.md").write_text(contenido, encoding="utf-8")
    return ruta


def _leer_progreso() -> dict:
    if ARCHIVO_PROGRESO.exists():
        return json.loads(ARCHIVO_PROGRESO.read_text(encoding="utf-8"))
    return {"sesiones": {}, "simulacros": []}


def _escribir_progreso(datos: dict) -> None:
    ARCHIVO_PROGRESO.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")


def registrar_sesion(s: Sesion, n: Nota) -> None:
    datos = _leer_progreso()
    datos["sesiones"].setdefault(str(s.numero), []).append({
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "nota": n.total, "quiz": round(n.quiz, 1), "labs": round(n.labs, 1),
        "caso": None if n.caso is None else round(n.caso, 1),
        "provisional": n.provisional, "aprobado": n.aprobado,
    })
    _escribir_progreso(datos)


def registrar_simulacro(pct: float, n: int, minutos: float, por_dominio: dict) -> None:
    datos = _leer_progreso()
    datos["simulacros"].append({
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "porcentaje": round(pct, 1), "preguntas": n, "minutos": round(minutos, 1),
        "por_dominio": por_dominio,
    })
    _escribir_progreso(datos)


def resumen_progreso() -> str:
    datos = _leer_progreso()
    lineas = ["Sesión | Dominio (peso) | Intentos | Última nota | Mejor | Estado", "-" * 78]
    preparacion = 0.0
    for num, s in SESIONES.items():
        intentos = datos["sesiones"].get(str(num), [])
        if intentos:
            ultima = intentos[-1]
            mejor = max(i["nota"] for i in intentos)
            estado = "✅" if ultima["aprobado"] else ("🟡" if ultima["provisional"] else "❌")
            preparacion += ultima["nota"] * s.peso_examen / 100
            lineas.append(f"  {num}    | {s.dominio_es[:34]:34} ({s.peso_examen}%) | {len(intentos):^8} "
                          f"| {ultima['nota']:>6.1f}      | {mejor:>5.1f} | {estado}")
        else:
            lineas.append(f"  {num}    | {s.dominio_es[:34]:34} ({s.peso_examen}%) |    0     |   —         |   —   | ⬜")
    lineas += ["", f"Preparación ponderada por el peso real del examen: {preparacion:.1f}/100"]
    if datos["simulacros"]:
        ult = datos["simulacros"][-1]
        lineas.append(f"Último simulacro: {ult['porcentaje']}% en {ult['preguntas']} preguntas "
                      f"({ult['minutos']} min) · {ult['fecha']}")
    else:
        lineas.append("Aún no haces un simulacro: python -m evaluador simulacro")
    return "\n".join(lineas)
