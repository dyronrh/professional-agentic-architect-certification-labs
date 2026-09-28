"""Herramientas del agente de viajes (Lab 3.1).

ADK construye la *declaración* de cada herramienta a partir de la firma tipada y del docstring.
Un contrato pobre (sin tipos, sin docstring, **kwargs) hace que el modelo elija mal los argumentos.
"""

from google.adk.tools import ToolContext

_VUELOS = {
    ("SCL", "LIM"): [{"vuelo": "LA2401", "precio": 210.0}, {"vuelo": "H24410", "precio": 175.5}],
    ("BOG", "MEX"): [{"vuelo": "AV204", "precio": 320.0}],
}


# TODO 1: reescribe esta herramienta con parámetros tipados (origen: str, destino: str, fecha: str),
# un docstring con sección "Args:" y respuesta estructurada:
#   - {"status": "success", "vuelos": [...]} si hay vuelos
#   - {"status": "error", "error_message": "..."} si los códigos no son IATA de 3 letras
#     o no hay vuelos para esa ruta.
def buscar_vuelos(**kwargs):
    return _VUELOS.get((kwargs.get("origen"), kwargs.get("destino")), [])


# TODO 2: guarda la preferencia para TODAS las sesiones futuras del usuario (elige el prefijo de estado
# correcto) y devuelve {"status": "success"}.
def guardar_preferencia(clave: str, valor: str, tool_context: ToolContext) -> dict:
    """Guarda una preferencia del viajero (p. ej. asiento=ventana).

    Args:
      clave: nombre de la preferencia.
      valor: valor de la preferencia.
    """
    tool_context.state[clave] = valor
    return {"status": "success"}


def registrar_presupuesto(monto: float, tool_context: ToolContext) -> dict:
    """Registra el presupuesto total del viajero en USD para validar reservas.

    Args:
      monto: presupuesto máximo total en USD.
    """
    tool_context.state["user:presupuesto"] = monto
    return {"status": "success", "presupuesto": monto}


def reservar_hotel(hotel: str, precio_noche: float, noches: int, tool_context: ToolContext) -> dict:
    """Reserva un hotel.

    Args:
      hotel: nombre del hotel.
      precio_noche: precio por noche en USD.
      noches: cantidad de noches.
    """
    total = round(precio_noche * noches, 2)
    tool_context.state["ultima_reserva"] = {"hotel": hotel, "total": total}
    return {"status": "success", "hotel": hotel, "total": total}
