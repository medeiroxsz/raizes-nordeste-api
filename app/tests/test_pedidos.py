"""
RF03 — Criação de pedidos.
RF04 — Atualização de status.
RF09 — Multicanalidade (canalPedido).
RN04, RN05, RN06.
"""


def test_criar_pedido_valido(client, auth_cliente, unidade_com_estoque):
    """RF03 + RF09: pedido criado com canal válido e estoque suficiente."""
    headers, _ = auth_cliente
    dados = unidade_com_estoque
    resp = client.post(
        "/pedidos",
        json={
            "unidade_id": dados["unidade_id"],
            "canal_pedido": "TOTEM",
            "itens": [{"produto_id": dados["produto_id"], "quantidade": 2}],
        },
        headers=headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "AGUARDANDO_PAGAMENTO"
    assert body["canalPedido"] == "TOTEM"
    assert float(body["total"]) == 25.80


def test_criar_pedido_sem_canal_retorna_422(client, auth_cliente, unidade_com_estoque):
    """RN04: canal_pedido é obrigatório."""
    headers, _ = auth_cliente
    dados = unidade_com_estoque
    resp = client.post(
        "/pedidos",
        json={"unidade_id": dados["unidade_id"], "itens": [{"produto_id": dados["produto_id"], "quantidade": 1}]},
        headers=headers,
    )
    assert resp.status_code == 422


def test_criar_pedido_canal_invalido_retorna_422(client, auth_cliente, unidade_com_estoque):
    """RN04: canal_pedido deve pertencer ao Enum."""
    headers, _ = auth_cliente
    dados = unidade_com_estoque
    resp = client.post(
        "/pedidos",
        json={
            "unidade_id": dados["unidade_id"],
            "canal_pedido": "DRIVE_THRU",
            "itens": [{"produto_id": dados["produto_id"], "quantidade": 1}],
        },
        headers=headers,
    )
    assert resp.status_code == 422


def test_criar_pedido_estoque_insuficiente(client, auth_cliente, unidade_com_estoque):
    """RN05: pedido maior que o estoque disponível (5 unidades) retorna 409."""
    headers, _ = auth_cliente
    dados = unidade_com_estoque
    resp = client.post(
        "/pedidos",
        json={
            "unidade_id": dados["unidade_id"],
            "canal_pedido": "APP",
            "itens": [{"produto_id": dados["produto_id"], "quantidade": 999}],
        },
        headers=headers,
    )
    assert resp.status_code == 409
    assert resp.json()["error"] == "ESTOQUE_INSUFICIENTE"


def test_criar_pedido_produto_inexistente(client, auth_cliente, unidade_com_estoque):
    headers, _ = auth_cliente
    dados = unidade_com_estoque
    resp = client.post(
        "/pedidos",
        json={
            "unidade_id": dados["unidade_id"],
            "canal_pedido": "APP",
            "itens": [{"produto_id": 9999, "quantidade": 1}],
        },
        headers=headers,
    )
    assert resp.status_code == 404


def test_filtrar_pedidos_por_canal(client, auth_cliente, unidade_com_estoque):
    """RF09: GET /pedidos?canalPedido=TOTEM retorna só pedidos daquele canal."""
    headers, _ = auth_cliente
    dados = unidade_com_estoque
    client.post(
        "/pedidos",
        json={
            "unidade_id": dados["unidade_id"],
            "canal_pedido": "TOTEM",
            "itens": [{"produto_id": dados["produto_id"], "quantidade": 1}],
        },
        headers=headers,
    )
    client.post(
        "/pedidos",
        json={
            "unidade_id": dados["unidade_id"],
            "canal_pedido": "APP",
            "itens": [{"produto_id": dados["produto_id"], "quantidade": 1}],
        },
        headers=headers,
    )
    resp = client.get("/pedidos?canalPedido=TOTEM", headers=headers)
    assert resp.status_code == 200
    pedidos = resp.json()
    assert len(pedidos) == 1
    assert pedidos[0]["canalPedido"] == "TOTEM"


def test_atualizar_status_pedido_transicao_valida(client, auth_cliente, auth_cozinha, unidade_com_estoque):
    """RF04: COZINHA avança pedido de AGUARDANDO_PAGAMENTO para CANCELADO (transição válida)."""
    headers_cliente, _ = auth_cliente
    headers_cozinha, _ = auth_cozinha
    dados = unidade_com_estoque
    pedido_id = client.post(
        "/pedidos",
        json={
            "unidade_id": dados["unidade_id"],
            "canal_pedido": "BALCAO",
            "itens": [{"produto_id": dados["produto_id"], "quantidade": 1}],
        },
        headers=headers_cliente,
    ).json()["id"]

    resp = client.patch(
        f"/pedidos/{pedido_id}/status", json={"novo_status": "CANCELADO"}, headers=headers_cozinha
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "CANCELADO"


def test_atualizar_status_transicao_invalida(client, auth_cliente, auth_cozinha, unidade_com_estoque):
    """RN06: não é possível ir direto de AGUARDANDO_PAGAMENTO para ENTREGUE."""
    headers_cliente, _ = auth_cliente
    headers_cozinha, _ = auth_cozinha
    dados = unidade_com_estoque
    pedido_id = client.post(
        "/pedidos",
        json={
            "unidade_id": dados["unidade_id"],
            "canal_pedido": "WEB",
            "itens": [{"produto_id": dados["produto_id"], "quantidade": 1}],
        },
        headers=headers_cliente,
    ).json()["id"]

    resp = client.patch(
        f"/pedidos/{pedido_id}/status", json={"novo_status": "ENTREGUE"}, headers=headers_cozinha
    )
    assert resp.status_code == 409
    assert resp.json()["error"] == "TRANSICAO_STATUS_INVALIDA"


def test_atualizar_status_sem_permissao(client, auth_cliente, unidade_com_estoque):
    """RNF01: CLIENTE não pode atualizar status (só COZINHA/GERENTE/ADMIN)."""
    headers_cliente, _ = auth_cliente
    dados = unidade_com_estoque
    pedido_id = client.post(
        "/pedidos",
        json={
            "unidade_id": dados["unidade_id"],
            "canal_pedido": "PICKUP",
            "itens": [{"produto_id": dados["produto_id"], "quantidade": 1}],
        },
        headers=headers_cliente,
    ).json()["id"]

    resp = client.patch(
        f"/pedidos/{pedido_id}/status", json={"novo_status": "CANCELADO"}, headers=headers_cliente
    )
    assert resp.status_code == 403
