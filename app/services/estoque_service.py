"""Implementa RF05 (controle de estoque por unidade) e RN08 (saldo não-negativo)."""
from sqlalchemy.orm import Session

from app.exceptions.custom_exceptions import EstoqueInsuficienteError, NotFoundError
from app.models.enums import TipoMovimentoEstoqueEnum
from app.models.estoque import Estoque
from app.models.log_auditoria import LogAuditoria
from app.repositories.catalogo_repository import (
    EstoqueRepository,
    ProdutoRepository,
    UnidadeRepository,
)
from app.repositories.fidelidade_repository import LogAuditoriaRepository
from app.schemas.estoque import MovimentoEstoqueCreate


class EstoqueService:
    def __init__(self, db: Session):
        self.estoque_repo = EstoqueRepository(db)
        self.unidade_repo = UnidadeRepository(db)
        self.produto_repo = ProdutoRepository(db)
        self.log_repo = LogAuditoriaRepository(db)

    def movimentar(self, dados: MovimentoEstoqueCreate, usuario_id: int) -> Estoque:
        """RF05: registra entrada/saída. RN08: saída não pode deixar saldo negativo."""
        if self.unidade_repo.get_by_id(dados.unidade_id) is None:
            raise NotFoundError(f"Unidade {dados.unidade_id} não encontrada.")
        if self.produto_repo.get_by_id(dados.produto_id) is None:
            raise NotFoundError(f"Produto {dados.produto_id} não encontrado.")

        estoque = self.estoque_repo.get(dados.unidade_id, dados.produto_id)
        if estoque is None:
            estoque = Estoque(unidade_id=dados.unidade_id, produto_id=dados.produto_id, quantidade=0)

        if dados.tipo_movimento == TipoMovimentoEstoqueEnum.ENTRADA:
            estoque.quantidade += dados.quantidade
        else:  # SAIDA
            if estoque.quantidade < dados.quantidade:
                raise EstoqueInsuficienteError(
                    "Saldo insuficiente para realizar a saída de estoque.",
                    details=[{"field": "quantidade", "issue": f"Disponível: {estoque.quantidade}"}],
                )
            estoque.quantidade -= dados.quantidade

        estoque = self.estoque_repo.upsert(estoque)

        # RNF02 — auditoria de ajuste de estoque (ação sensível)
        self.log_repo.create(
            LogAuditoria(
                usuario_id=usuario_id,
                acao=f"MOVIMENTO_ESTOQUE_{dados.tipo_movimento.value}",
                entidade="Estoque",
                entidade_id=estoque.id,
                detalhes=f"quantidade={dados.quantidade}",
            )
        )
        return estoque

    def verificar_disponibilidade(self, unidade_id: int, produto_id: int, quantidade: int) -> Estoque:
        """Usado pelo PedidoService para validar RN05 antes de criar o pedido."""
        estoque = self.estoque_repo.get(unidade_id, produto_id)
        disponivel = estoque.quantidade if estoque else 0
        if disponivel < quantidade:
            raise EstoqueInsuficienteError(
                "Não há quantidade suficiente para um ou mais itens.",
                details=[{"field": f"produto_{produto_id}", "issue": f"Disponível: {disponivel}"}],
            )
        return estoque

    def debitar(self, estoque: Estoque, quantidade: int) -> Estoque:
        estoque.quantidade -= quantidade
        return self.estoque_repo.upsert(estoque)
