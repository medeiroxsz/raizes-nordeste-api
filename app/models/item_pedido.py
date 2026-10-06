"""Entidade ItemPedido — linha de um pedido (parte de RF03)."""
from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, Numeric
from sqlalchemy.orm import relationship

from app.database.connection import Base


class ItemPedido(Base):
    __tablename__ = "itens_pedido"
    __table_args__ = (CheckConstraint("quantidade > 0", name="ck_item_quantidade_positiva"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade = Column(Integer, nullable=False)
    preco_unitario = Column(Numeric(10, 2), nullable=False)

    pedido = relationship("Pedido", back_populates="itens")
    produto = relationship("Produto", back_populates="itens_pedido")
