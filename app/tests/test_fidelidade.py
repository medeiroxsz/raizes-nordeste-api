"""RF06 — Fidelização. RN09 — consentimento LGPD. RN10 — saldo de pontos."""


def test_consultar_fidelidade_propria(client, auth_cliente):
    headers, cliente_id = auth_cliente
    resp = client.get(f"/fidelidade/{cliente_id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["pontosSaldo"] == 0
    assert resp.json()["consentimentoLgpd"] is False


def test_consultar_fidelidade_de_outro_cliente_retorna_403(client, auth_cliente):
    headers, _ = auth_cliente
    resp = client.get("/fidelidade/9999", headers=headers)
    assert resp.status_code == 403


def test_resgate_sem_consentimento_retorna_409(client, auth_cliente):
    """RN09: sem consentimento LGPD, não é possível nem resgatar pontos."""
    headers, _ = auth_cliente
    resp = client.post("/fidelidade/resgate", json={"pontos": 10}, headers=headers)
    assert resp.status_code == 409
    assert resp.json()["error"] == "CONSENTIMENTO_LGPD_AUSENTE"


def test_pontos_creditados_apos_pagamento_com_consentimento(
    client, auth_cliente, unidade_com_estoque
):
    """RN09: com consentimento, pagamento aprovado credita pontos (1 ponto por R$1)."""
    headers, cliente_id = auth_cliente
    client.put(
        f"/fidelidade/{cliente_id}/consentimento", json={"consentimento_lgpd": True}, headers=headers
    )

    dados = unidade_com_estoque
    pedido_id = client.post(
        "/pedidos",
        json={
            "unidade_id": dados["unidade_id"],
            "canal_pedido": "APP",
            "itens": [{"produto_id": dados["produto_id"], "quantidade": 1}],
        },
        headers=headers,
    ).json()["id"]
    client.post(f"/pagamentos/{pedido_id}/simular", json={"forma_pagamento": "PIX"}, headers=headers)

    resp = client.get(f"/fidelidade/{cliente_id}", headers=headers)
    assert resp.json()["pontosSaldo"] == 12  # preco 12.90 -> int(12.90) = 12 pontos


def test_resgate_maior_que_saldo_retorna_409(client, auth_cliente):
    """RN10: resgate maior que o saldo disponível é rejeitado."""
    headers, cliente_id = auth_cliente
    client.put(
        f"/fidelidade/{cliente_id}/consentimento", json={"consentimento_lgpd": True}, headers=headers
    )
    resp = client.post("/fidelidade/resgate", json={"pontos": 500}, headers=headers)
    assert resp.status_code == 409
    assert resp.json()["error"] == "SALDO_PONTOS_INSUFICIENTE"
