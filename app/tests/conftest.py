"""
Fixtures compartilhadas.

Cada teste roda contra um banco SQLite em memória isolado (StaticPool),
sobrescrevendo a dependência `get_db`. Isso evita que os testes dependam de
ordem de execução ou sujem o banco de desenvolvimento (`raizes_nordeste.db`).
"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.connection import Base, get_db
from app.main import app

# IMPORTANTE: usar `from app import models` (não `import app.models`).
# `import app.models` vincularia o nome *top-level* `app` (o pacote) ao
# namespace local, sobrescrevendo o `app` importado acima (a instância
# FastAPI) — é assim que `import a.b` funciona em Python: só `a` é
# vinculado ao escopo local, nunca `a.b`. Isso causava
# `AttributeError: module 'app' has no attribute 'dependency_overrides'`,
# pois o `app` usado mais abaixo passava a ser o pacote, não o FastAPI().
from app import models  # noqa: F401  registra todos os models no Base.metadata


@pytest.fixture()
def client():
    # Falha cedo e com mensagem clara se `app` algum dia deixar de ser a
    # instância FastAPI (ex.: reintrodução do bug de shadowing do import) —
    # em vez de um AttributeError genérico lá na frente.
    assert isinstance(app, FastAPI), (
        "`app` em conftest.py deveria ser a instância FastAPI de app.main; "
        f"veio como {type(app)!r}. Verifique se nenhum import posterior "
        "está sobrescrevendo o nome `app` (ex.: `import app.<algo>`)."
    )

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # function-scoped (padrão de @pytest.fixture()): cada teste recebe sua
    # própria chamada desta fixture, então o override é aplicado e limpo a
    # cada teste. O try/finally garante a limpeza mesmo se o teste levantar
    # uma exceção, evitando vazamento de override entre testes.
    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def _cadastrar_e_logar(client: TestClient, email: str, perfil: str) -> dict:
    """Helper: cadastra um usuário com o perfil informado e retorna headers de auth."""
    client.post(
        "/usuarios",
        json={"nome": "Teste", "email": email, "senha": "Senha@123", "perfil": perfil},
    )
    resp = client.post("/auth/login", json={"email": email, "senha": "Senha@123"})
    token = resp.json()["access_token"]
    usuario_id = resp.json()["usuario"]["id"]
    return {"Authorization": f"Bearer {token}"}, usuario_id


@pytest.fixture()
def auth_cliente(client):
    headers, usuario_id = _cadastrar_e_logar(client, "cliente@exemplo.com", "CLIENTE")
    return headers, usuario_id


@pytest.fixture()
def auth_gerente(client):
    headers, usuario_id = _cadastrar_e_logar(client, "gerente@exemplo.com", "GERENTE")
    return headers, usuario_id


@pytest.fixture()
def auth_cozinha(client):
    headers, usuario_id = _cadastrar_e_logar(client, "cozinha@exemplo.com", "COZINHA")
    return headers, usuario_id


@pytest.fixture()
def unidade_com_estoque(client, auth_gerente):
    """Cria 1 unidade + 1 produto + 5 unidades em estoque, pronta para pedidos."""
    headers_gerente, _ = auth_gerente

    resp_unidade = client.post(
        "/unidades",
        json={"nome": "Raízes - Boa Viagem", "cidade": "Recife", "tipo_cozinha": "COMPLETA"},
        headers=headers_gerente,
    )
    unidade_id = resp_unidade.json()["id"]

    resp_produto = client.post(
        "/produtos",
        json={"nome": "Tapioca de Queijo", "preco": 12.90, "categoria": "Salgados"},
        headers=headers_gerente,
    )
    produto_id = resp_produto.json()["id"]

    client.post(
        "/estoque/movimentacoes",
        json={
            "unidade_id": unidade_id,
            "produto_id": produto_id,
            "quantidade": 5,
            "tipo_movimento": "ENTRADA",
        },
        headers=headers_gerente,
    )
    return {"unidade_id": unidade_id, "produto_id": produto_id}
