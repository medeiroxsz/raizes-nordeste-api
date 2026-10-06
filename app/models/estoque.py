"""Entidade Estoque — saldo de um produto em uma unidade (RF05, RN08)."""
from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Estoque(Base):
    __tablename__ = "estoques"
    __table_args__ = (
        UniqueConstraint("unidade_id", "produto_id", name="uq_estoque_unidade_produto"),
        CheckConstraint("quantidade >= 0", name="ck_estoque_quantidade_nao_negativa"),  # RN08
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    unidade_id = Column(Integer, ForeignKey("unidades.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade = Column(Integer, nullable=False, default=0)

    unidade = relationship("Unidade", back_populates="estoques")
    produto = relationship("Produto", back_populates="estoques")
