"""Acesso a dados de Unidade, Produto e Estoque — camada Infrastructure."""
from sqlalchemy.orm import Session

from app.models.estoque import Estoque
from app.models.produto import Produto
from app.models.unidade import Unidade


class UnidadeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, unidade_id: int) -> Unidade | None:
        return self.db.query(Unidade).filter(Unidade.id == unidade_id).first()

    def list_all(self) -> list[Unidade]:
        return self.db.query(Unidade).all()

    def create(self, unidade: Unidade) -> Unidade:
        self.db.add(unidade)
        self.db.commit()
        self.db.refresh(unidade)
        return unidade


class ProdutoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, produto_id: int) -> Produto | None:
        return self.db.query(Produto).filter(Produto.id == produto_id).first()

    def create(self, produto: Produto) -> Produto:
        self.db.add(produto)
        self.db.commit()
        self.db.refresh(produto)
        return produto

    def listar_disponiveis_por_unidade(self, unidade_id: int) -> list[tuple[Produto, int]]:
        """RN03 — só retorna produtos com estoque > 0 na unidade."""
        resultados = (
            self.db.query(Produto, Estoque.quantidade)
            .join(Estoque, Estoque.produto_id == Produto.id)
            .filter(Estoque.unidade_id == unidade_id, Estoque.quantidade > 0)
            .all()
        )
        return resultados


class EstoqueRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, unidade_id: int, produto_id: int) -> Estoque | None:
        return (
            self.db.query(Estoque)
            .filter(Estoque.unidade_id == unidade_id, Estoque.produto_id == produto_id)
            .first()
        )

    def list_by_unidade(self, unidade_id: int) -> list[Estoque]:
        return self.db.query(Estoque).filter(Estoque.unidade_id == unidade_id).all()

    def upsert(self, estoque: Estoque) -> Estoque:
        self.db.add(estoque)
        self.db.commit()
        self.db.refresh(estoque)
        return estoque
