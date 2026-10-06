"""RF05 — Controle de estoque. RN08 — saldo não pode ficar negativo."""


def test_movimentar_estoque_entrada(client, auth_gerente):
    headers, _ = auth_gerente
    unidade_id = client.post("/unidades", json={"nome": "U1", "cidade": "Recife"}, headers=headers).json()["id"]
    produto_id = client.post("/produtos", json={"nome": "Suco", "preco": 6.5}, headers=headers).json()["id"]

    resp = client.post(
        "/estoque/movimentacoes",
        json={"unidade_id": unidade_id, "produto_id": produto_id, "quantidade": 10, "tipo_movimento": "ENTRADA"},
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json()["quantidade"] == 10


def test_estoque_saida_maior_que_saldo(client, auth_gerente):
    """RN08: saída maior que o saldo disponível deve retornar 409."""
    headers, _ = auth_gerente
    unidade_id = client.post("/unidades", json={"nome": "U2", "cidade": "Recife"}, headers=headers).json()["id"]
    produto_id = client.post("/produtos", json={"nome": "Bolo", "preco": 15.0}, headers=headers).json()["id"]

    client.post(
        "/estoque/movimentacoes",
        json={"unidade_id": unidade_id, "produto_id": produto_id, "quantidade": 2, "tipo_movimento": "ENTRADA"},
        headers=headers,
    )
    resp = client.post(
        "/estoque/movimentacoes",
        json={"unidade_id": unidade_id, "produto_id": produto_id, "quantidade": 5, "tipo_movimento": "SAIDA"},
        headers=headers,
    )
    assert resp.status_code == 409
    assert resp.json()["error"] == "ESTOQUE_INSUFICIENTE"


def test_movimentar_estoque_produto_inexistente(client, auth_gerente):
    headers, _ = auth_gerente
    unidade_id = client.post("/unidades", json={"nome": "U3", "cidade": "Olinda"}, headers=headers).json()["id"]
    resp = client.post(
        "/estoque/movimentacoes",
        json={"unidade_id": unidade_id, "produto_id": 9999, "quantidade": 1, "tipo_movimento": "ENTRADA"},
        headers=headers,
    )
    assert resp.status_code == 404
