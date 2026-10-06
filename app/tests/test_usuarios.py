"""
RF01 — Cadastro e autenticação de usuários.
RN01 — e-mail único. RN02 — senha nunca em texto puro.
"""


def test_criar_usuario_valido(client):
    """RF01: cadastro válido retorna 201 e nunca expõe a senha."""
    resp = client.post(
        "/usuarios",
        json={"nome": "Maria Souza", "email": "maria@exemplo.com", "senha": "Senha@123", "perfil": "CLIENTE"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "maria@exemplo.com"
    assert "senha" not in body
    assert "senha_hash" not in body


def test_criar_usuario_email_duplicado(client):
    """RN01: dois cadastros com o mesmo e-mail devem falhar com 409."""
    payload = {"nome": "Maria", "email": "dup@exemplo.com", "senha": "Senha@123", "perfil": "CLIENTE"}
    resp1 = client.post("/usuarios", json=payload)
    resp2 = client.post("/usuarios", json=payload)
    assert resp1.status_code == 201
    assert resp2.status_code == 409
    assert resp2.json()["error"] == "EMAIL_DUPLICADO"


def test_login_valido(client):
    """RF01: login com credenciais corretas retorna token JWT."""
    client.post(
        "/usuarios",
        json={"nome": "Maria", "email": "login@exemplo.com", "senha": "Senha@123", "perfil": "CLIENTE"},
    )
    resp = client.post("/auth/login", json={"email": "login@exemplo.com", "senha": "Senha@123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_senha_invalida(client):
    """Credenciais inválidas retornam 401."""
    client.post(
        "/usuarios",
        json={"nome": "Maria", "email": "login2@exemplo.com", "senha": "Senha@123", "perfil": "CLIENTE"},
    )
    resp = client.post("/auth/login", json={"email": "login2@exemplo.com", "senha": "SenhaErrada"})
    assert resp.status_code == 401
    assert resp.json()["error"] == "NAO_AUTENTICADO"


def test_acesso_sem_token(client):
    """RNF01: endpoint protegido sem token retorna 401."""
    resp = client.get("/pedidos")
    assert resp.status_code == 401


def test_acesso_com_perfil_sem_permissao(client, auth_cliente):
    """RNF01: CLIENTE não pode movimentar estoque (só GERENTE/ADMIN) -> 403."""
    headers, _ = auth_cliente
    resp = client.post(
        "/estoque/movimentacoes",
        json={"unidade_id": 1, "produto_id": 1, "quantidade": 5, "tipo_movimento": "ENTRADA"},
        headers=headers,
    )
    assert resp.status_code == 403
    assert resp.json()["error"] == "SEM_PERMISSAO"
