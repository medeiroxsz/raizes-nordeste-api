"""Acesso a dados de Pedido — camada Infrastructure."""
from sqlalchemy.orm import Session, joinedload

from app.models.enums import CanalPedidoEnum
from app.models.pedido import Pedido


class PedidoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, pedido_id: int) -> Pedido | None:
        return (
            self.db.query(Pedido)
            .options(joinedload(Pedido.itens))
            .filter(Pedido.id == pedido_id)
            .first()
        )

    def list(self, canal_pedido: CanalPedidoEnum | None = None) -> list[Pedido]:
        """RF09 — permite filtrar por canalPedido."""
        query = self.db.query(Pedido).options(joinedload(Pedido.itens))
        if canal_pedido is not None:
            query = query.filter(Pedido.canal_pedido == canal_pedido)
        return query.order_by(Pedido.id.desc()).all()

    def create(self, pedido: Pedido) -> Pedido:
        self.db.add(pedido)
        self.db.commit()
        self.db.refresh(pedido)
        return pedido

    def save(self, pedido: Pedido) -> Pedido:
        self.db.commit()
        self.db.refresh(pedido)
        return pedido
