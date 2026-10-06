"""
RNF02 — Logs/auditoria de ações sensíveis.

Testado no nível de repository/service (não há endpoint público de consulta
de logs neste MVP — ver ANALISE_TECNICA.md, Checklist), mas o registro em si
é verificado diretamente no banco.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.connection import Base
from app.models.enums import PerfilEnum, TipoMovimentoEstoqueEnum
from app.models.log_auditoria import LogAuditoria
from app.models.usuario import Usuario
from app.schemas.estoque import MovimentoEstoqueCreate
from app.services.catalogo_service import CatalogoService
from app.services.estoque_service import EstoqueService
from app.schemas.unidade import ProdutoCreate, UnidadeCreate


def _nova_sessao():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def test_movimentacao_de_estoque_gera_log_auditoria():
    """RNF02: ajuste de estoque (ação sensível) deve gerar um LogAuditoria."""
    db = _nova_sessao()

    usuario = Usuario(nome="Gerente", email="g@x.com", senha_hash="x", perfil=PerfilEnum.GERENTE)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    catalogo = CatalogoService(db)
    unidade = catalogo.criar_unidade(UnidadeCreate(nome="U1", cidade="Recife"))
    produto = catalogo.criar_produto(ProdutoCreate(nome="Suco", preco=5))

    EstoqueService(db).movimentar(
        MovimentoEstoqueCreate(
            unidade_id=unidade.id,
            produto_id=produto.id,
            quantidade=10,
            tipo_movimento=TipoMovimentoEstoqueEnum.ENTRADA,
        ),
        usuario_id=usuario.id,
    )

    logs = db.query(LogAuditoria).filter(LogAuditoria.entidade == "Estoque").all()
    assert len(logs) == 1
    assert logs[0].usuario_id == usuario.id
    assert "MOVIMENTO_ESTOQUE_ENTRADA" == logs[0].acao
