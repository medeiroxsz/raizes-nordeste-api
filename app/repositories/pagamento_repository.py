"""Acesso a dados de Pagamento — camada Infrastructure."""
from sqlalchemy.orm import Session

from app.models.pagamento import Pagamento


class PagamentoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_pedido_id(self, pedido_id: int) -> Pagamento | None:
        return self.db.query(Pagamento).filter(Pagamento.pedido_id == pedido_id).first()

    def create(self, pagamento: Pagamento) -> Pagamento:
        self.db.add(pagamento)
        self.db.commit()
        self.db.refresh(pagamento)
        return pagamento
