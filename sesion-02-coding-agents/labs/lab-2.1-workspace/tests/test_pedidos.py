from app.pedidos import total_pedido


def test_total_pedido():
    assert total_pedido([{"precio": 10.0, "cantidad": 2}, {"precio": 0.5, "cantidad": 3}]) == 21.5
