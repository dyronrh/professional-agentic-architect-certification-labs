"""Servicio de ejemplo sobre el que trabaja el agente de código."""


def total_pedido(items: list[dict]) -> float:
    """Suma precio * cantidad de cada item."""
    return round(sum(i["precio"] * i["cantidad"] for i in items), 2)
