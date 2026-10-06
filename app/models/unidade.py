"""Entidade Unidade — loja física da rede (contexto do estudo de caso)."""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Unidade(Base):
    __tablename__ = "unidades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(120), nullable=False)
    cidade = Column(String(80), nullable=False)
    tipo_cozinha = Column(String(20), nullable=False, default="COMPLETA")

    estoques = relationship("Estoque", back_populates="unidade")
    pedidos = relationship("Pedido", back_populates="unidade")
