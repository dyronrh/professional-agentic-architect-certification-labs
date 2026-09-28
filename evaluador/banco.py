"""Banco de preguntas: carga, quiz interactivo y calificación determinista."""

from __future__ import annotations

import json
import random
import time
from dataclasses import dataclass, field
from pathlib import Path

from .config import SEGUNDOS_POR_PREGUNTA, Sesion


@dataclass
class Pregunta:
    id: str
    sesion: int
    objetivo: str
    concepto: str
    pregunta: str
    opciones: dict[str, str]
    respuesta: list[str]
    explicacion: str
    dificultad: str = "media"

    @property
    def multiple(self) -> bool:
        return len(self.respuesta) > 1


@dataclass
class ResultadoQuiz:
    total: int
    correctas: int
    sin_responder: int
    por_objetivo: dict[str, list[int]] = field(default_factory=dict)  # obj -> [ok, total]
    falladas: list[tuple[Pregunta, list[str]]] = field(default_factory=list)

    @property
    def porcentaje(self) -> float:
        return 100.0 * self.correctas / self.total if self.total else 0.0


def cargar_preguntas(s: Sesion) -> list[Pregunta]:
    datos = json.loads(s.preguntas.read_text(encoding="utf-8"))
    return [
        Pregunta(sesion=s.numero, **{k: v for k, v in p.items() if k != "sesion"})
        for p in datos["preguntas"]
    ]


def normalizar(respuesta: str | list[str]) -> list[str]:
    if isinstance(respuesta, list):
        letras = respuesta
    else:
        letras = respuesta.replace(" ", "").replace(";", ",").split(",")
        if len(letras) == 1 and len(letras[0]) > 1:  # "AC" -> ["A","C"]
            letras = list(letras[0])
    return sorted({x.strip().upper() for x in letras if x.strip()})


def calificar(preguntas: list[Pregunta], respuestas: dict[str, list[str]]) -> ResultadoQuiz:
    r = ResultadoQuiz(total=len(preguntas), correctas=0, sin_responder=0)
    for p in preguntas:
        dada = normalizar(respuestas.get(p.id, []))
        ok = dada == sorted(p.respuesta)
        obj = r.por_objetivo.setdefault(p.objetivo, [0, 0])
        obj[1] += 1
        if not dada:
            r.sin_responder += 1
        if ok:
            r.correctas += 1
            obj[0] += 1
        else:
            r.falladas.append((p, dada))
    return r


def archivo_respuestas(s: Sesion) -> Path:
    return s.respuestas / "quiz.json"


def cargar_respuestas(ruta: Path) -> dict[str, list[str]]:
    if not ruta.exists():
        return {}
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    return {k: normalizar(v) for k, v in datos.get("respuestas", datos).items()}


def _mostrar(p: Pregunta, i: int, n: int) -> None:
    print(f"\n[{i}/{n}] ({p.id} · objetivo {p.objetivo})")
    print(p.pregunta)
    for letra, texto in p.opciones.items():
        print(f"   {letra}. {texto}")
    if p.multiple:
        print(f"   (Elige {len(p.respuesta)}; ej. A,C)")


def quiz_interactivo(
    preguntas: list[Pregunta],
    *,
    modo_estudio: bool,
    barajar: bool = True,
    semilla: int | None = None,
) -> tuple[dict[str, list[str]], float]:
    """Hace las preguntas por consola. En modo estudio muestra la explicación al instante."""
    orden = list(preguntas)
    if barajar:
        random.Random(semilla).shuffle(orden)
    respuestas: dict[str, list[str]] = {}
    limite = SEGUNDOS_POR_PREGUNTA * len(orden)
    inicio = time.time()
    print(f"{len(orden)} preguntas · tiempo objetivo {limite / 60:.0f} min "
          f"(ritmo del examen real: {SEGUNDOS_POR_PREGUNTA / 60:.2f} min/pregunta)")
    print("Escribe la letra (o letras separadas por coma). 'm' = marcar y saltar, 'q' = terminar.")
    pendientes: list[Pregunta] = []
    for ronda in (orden, None):
        lista = ronda if ronda is not None else pendientes
        if ronda is None and pendientes:
            print(f"\n--- Revisando {len(pendientes)} preguntas marcadas ---")
        for i, p in enumerate(lista, 1):
            _mostrar(p, i, len(lista))
            try:
                valor = input("> ").strip()
            except EOFError:
                valor = "q"
            if valor.lower() == "q":
                return respuestas, time.time() - inicio
            if valor.lower() == "m":
                if ronda is not None:
                    pendientes.append(p)
                continue
            respuestas[p.id] = normalizar(valor)
            if modo_estudio:
                ok = respuestas[p.id] == sorted(p.respuesta)
                print(("✅ Correcto" if ok else f"❌ Incorrecto. Respuesta: {','.join(p.respuesta)}"))
                print(f"   {p.explicacion}")
        if ronda is None:
            break
    transcurrido = time.time() - inicio
    if transcurrido > limite:
        print(f"\n⏰ Te pasaste del tiempo objetivo por {(transcurrido - limite) / 60:.1f} min.")
    return respuestas, transcurrido


def guardar_respuestas(ruta: Path, respuestas: dict[str, list[str]], segundos: float) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(
        json.dumps(
            {"segundos": round(segundos), "respuestas": respuestas},
            ensure_ascii=False, indent=2,
        ),
        encoding="utf-8",
    )
