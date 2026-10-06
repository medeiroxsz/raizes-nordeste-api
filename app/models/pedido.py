"""Entidade Pedido — RF03 (pedidos) e RF09 (multicanalidade / canalPedido)."""
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Numeric, func
from sqlalchemy.orm import relationship

from app.database.connection import Base
from app.models.enums import CanalPedidoEnum, StatusPedidoEnum


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    unidade_id = Column(Integer, ForeignKey("unidades.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    canal_pedido = Column(Enum(CanalPedidoEnum), nullable=False)  # RF09 - requisito mínimo de multicanalidade
    status = Column(
        Enum(StatusPedidoEnum), nullable=False, default=StatusPedidoEnum.AGUARDANDO_PAGAMENTO
    )
    total = Column(Numeric(10, 2), nullable=False, default=0)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    unidade = relationship("Unidade", back_populates="pedidos")
    cliente = relationship("Usuario", back_populates="pedidos")
    itens = relationship("ItemPedido", back_populates="pedido", cascade="all, delete-orphan")
    pagamento = relationship("Pagamento", back_populates="pedido", uselist=False)
