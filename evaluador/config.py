"""Configuración central del evaluador: sesiones, pesos y umbrales."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Sesion:
    numero: int
    carpeta: str
    dominio: str
    dominio_es: str
    peso_examen: int  # % aproximado del examen real

    @property
    def ruta(self) -> Path:
        return RAIZ / self.carpeta

    @property
    def preguntas(self) -> Path:
        return self.ruta / "preguntas.json"

    @property
    def rubrica(self) -> Path:
        return self.ruta / "rubrica-caso.json"

    @property
    def enunciado_caso(self) -> Path:
        return self.ruta / "caso-practico.md"

    @property
    def respuestas(self) -> Path:
        return self.ruta / "respuestas"

    @property
    def resultados(self) -> Path:
        return self.ruta / "resultados"


SESIONES: dict[int, Sesion] = {
    s.numero: s
    for s in [
        Sesion(1, "sesion-01-low-code", "Building agents using low-code tools",
               "Construir agentes con herramientas low-code", 13),
        Sesion(2, "sesion-02-coding-agents", "Using coding agents for application development",
               "Usar agentes de código para desarrollar aplicaciones", 17),
        Sesion(3, "sesion-03-custom-agents", "Developing custom agents",
               "Desarrollar agentes personalizados", 33),
        Sesion(4, "sesion-04-evaluate-deploy", "Evaluating and deploying agentic workflows",
               "Evaluar y desplegar flujos agénticos", 22),
        Sesion(5, "sesion-05-security-governance", "Securing and governing agentic workflows",
               "Asegurar y gobernar flujos agénticos", 15),
    ]
}

# Ponderación de la nota de cada sesión.
PESO_QUIZ = 0.50
PESO_LABS = 0.30
PESO_CASO = 0.20

# Google no publica la nota de corte; 70 % es un objetivo conservador de práctica.
UMBRAL_APROBADO = 70.0

# Examen real: ~80 preguntas en 180 minutos.
SEGUNDOS_POR_PREGUNTA = 180 * 60 / 80

ARCHIVO_PROGRESO = RAIZ / "progreso.json"
CARPETA_SIMULACROS = RAIZ / "simulacros"


def sesion(numero: int) -> Sesion:
    if numero not in SESIONES:
        raise SystemExit(f"Sesión {numero} no existe. Usa 1-5.")
    return SESIONES[numero]
