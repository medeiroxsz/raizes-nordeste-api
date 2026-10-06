"""Implementa RF02 (cardápio por unidade) e RN03 (só exibe produto disponível)."""
from sqlalchemy.orm import Session

from app.exceptions.custom_exceptions import NotFoundError
from app.models.estoque import Estoque
from app.models.produto import Produto
from app.models.unidade import Unidade
from app.repositories.catalogo_repository import (
    EstoqueRepository,
    ProdutoRepository,
    UnidadeRepository,
)
from app.schemas.unidade import ProdutoCreate, UnidadeCreate


class CatalogoService:
    def __init__(self, db: Session):
        self.unidade_repo = UnidadeRepository(db)
        self.produto_repo = ProdutoRepository(db)
        self.estoque_repo = EstoqueRepository(db)

    def criar_unidade(self, dados: UnidadeCreate) -> Unidade:
        unidade = Unidade(nome=dados.nome, cidade=dados.cidade, tipo_cozinha=dados.tipo_cozinha)
        return self.unidade_repo.create(unidade)

    def listar_unidades(self) -> list[Unidade]:
        return self.unidade_repo.list_all()

    def criar_produto(self, dados: ProdutoCreate) -> Produto:
        produto = Produto(**dados.model_dump())
        return self.produto_repo.create(produto)

    def cardapio_por_unidade(self, unidade_id: int) -> list[tuple[Produto, int]]:
        """RF02 + RN03."""
        if self.unidade_repo.get_by_id(unidade_id) is None:
            raise NotFoundError(f"Unidade {unidade_id} não encontrada.")
        return self.produto_repo.listar_disponiveis_por_unidade(unidade_id)

    def obter_produto(self, produto_id: int) -> Produto:
        produto = self.produto_repo.get_by_id(produto_id)
        if produto is None:
            raise NotFoundError(f"Produto {produto_id} não encontrado.")
        return produto

    def obter_unidade(self, unidade_id: int) -> Unidade:
        unidade = self.unidade_repo.get_by_id(unidade_id)
        if unidade is None:
            raise NotFoundError(f"Unidade {unidade_id} não encontrada.")
        return unidade

    def obter_estoque(self, unidade_id: int, produto_id: int) -> Estoque | None:
        return self.estoque_repo.get(unidade_id, produto_id)

    def listar_estoque_por_unidade(self, unidade_id: int) -> list[Estoque]:
        return self.estoque_repo.list_by_unidade(unidade_id)
