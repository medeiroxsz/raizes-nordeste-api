"""RF08 — Integração simulada de pagamento. RN06/RN07/RN12."""


def _criar_pedido(client, headers, dados, canal="TOTEM"):
    return client.post(
        "/pedidos",
        json={
            "unidade_id": dados["unidade_id"],
            "canal_pedido": canal,
            "itens": [{"produto_id": dados["produto_id"], "quantidade": 1}],
        },
        headers=headers,
    ).json()["id"]


def test_pagamento_aprovado_avanca_status(client, auth_cliente, unidade_com_estoque):
    """RF08 + RN06: pagamento aprovado move o pedido para EM_PREPARO."""
    headers, _ = auth_cliente
    pedido_id = _criar_pedido(client, headers, unidade_com_estoque)

    resp = client.post(
        f"/pagamentos/{pedido_id}/simular", json={"forma_pagamento": "PIX"}, headers=headers
    )
    assert resp.status_code == 201
    assert resp.json()["status"] == "APROVADO"

    pedido = client.get(f"/pedidos/{pedido_id}", headers=headers).json()
    assert pedido["status"] == "EM_PREPARO"


def test_pagamento_recusado_marca_pedido(client, auth_cliente, unidade_com_estoque):
    """RF08 + RN07: pagamento recusado (forma_pagamento=RECUSAR) marca PAGAMENTO_RECUSADO."""
    headers, _ = auth_cliente
    pedido_id = _criar_pedido(client, headers, unidade_com_estoque)

    resp = client.post(
        f"/pagamentos/{pedido_id}/simular", json={"forma_pagamento": "RECUSAR"}, headers=headers
    )
    assert resp.status_code == 201
    assert resp.json()["status"] == "RECUSADO"

    pedido = client.get(f"/pedidos/{pedido_id}", headers=headers).json()
    assert pedido["status"] == "PAGAMENTO_RECUSADO"


def test_pagamento_de_pedido_ja_pago_retorna_conflito(client, auth_cliente, unidade_com_estoque):
    """Pedido que já saiu de AGUARDANDO_PAGAMENTO não pode ser pago novamente."""
    headers, _ = auth_cliente
    pedido_id = _criar_pedido(client, headers, unidade_com_estoque)
    client.post(f"/pagamentos/{pedido_id}/simular", json={"forma_pagamento": "PIX"}, headers=headers)

    resp = client.post(
        f"/pagamentos/{pedido_id}/simular", json={"forma_pagamento": "PIX"}, headers=headers
    )
    assert resp.status_code == 409


def test_pagamento_pedido_inexistente(client, auth_cliente):
    headers, _ = auth_cliente
    resp = client.post("/pagamentos/9999/simular", json={"forma_pagamento": "PIX"}, headers=headers)
    assert resp.status_code == 404
