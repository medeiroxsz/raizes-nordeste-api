"""Entidade Produto — item do cardápio (RF02)."""
from sqlalchemy import Boolean, Column, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(120), nullable=False)
    descricao = Column(String(255), nullable=True)
    preco = Column(Numeric(10, 2), nullable=False)
    categoria = Column(String(60), nullable=True)
    sazonal = Column(Boolean, nullable=False, default=False)

    estoques = relationship("Estoque", back_populates="produto")
    itens_pedido = relationship("ItemPedido", back_populates="produto")
