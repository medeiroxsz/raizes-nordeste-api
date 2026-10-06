"""
Entidade Pagamento — RF08: registro do resultado do gateway externo (mock).
O sistema não processa pagamento real (estudo de caso, item 5): apenas
solicita, recebe a confirmação/negativa e registra (RN12).
"""
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.database.connection import Base
from app.models.enums import StatusPagamentoEnum


class Pagamento(Base):
    __tablename__ = "pagamentos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False, unique=True)
    status = Column(Enum(StatusPagamentoEnum), nullable=False)
    forma_pagamento = Column(String(20), nullable=False)
    payload_resposta = Column(String(500), nullable=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    pedido = relationship("Pedido", back_populates="pagamento")
