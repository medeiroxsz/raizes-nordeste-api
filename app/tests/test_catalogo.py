"""RF02 — Consulta de cardápio por unidade. RN03 — só exibe produto com estoque."""


def test_listar_cardapio_unidade(client, unidade_com_estoque):
    """RF02 + RN03: produto com estoque aparece no cardápio."""
    unidade_id = unidade_com_estoque["unidade_id"]
    resp = client.get(f"/unidades/{unidade_id}/produtos")
    assert resp.status_code == 200
    produtos = resp.json()
    assert len(produtos) == 1
    assert produtos[0]["quantidadeDisponivel"] == 5


def test_cardapio_unidade_inexistente(client):
    """RF02: unidade inexistente retorna 404."""
    resp = client.get("/unidades/9999/produtos")
    assert resp.status_code == 404


def test_produto_sem_estoque_nao_aparece_no_cardapio(client, auth_gerente):
    """RN03: produto cadastrado mas sem movimentação de estoque não aparece."""
    headers, _ = auth_gerente
    resp_unidade = client.post(
        "/unidades", json={"nome": "Unidade Sem Estoque", "cidade": "Salvador"}, headers=headers
    )
    unidade_id = resp_unidade.json()["id"]
    client.post("/produtos", json={"nome": "Cuscuz", "preco": 9.90}, headers=headers)

    resp = client.get(f"/unidades/{unidade_id}/produtos")
    assert resp.status_code == 200
    assert resp.json() == []
