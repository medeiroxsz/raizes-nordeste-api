"""Entidade Usuario — RF01 (cadastro e autenticação com perfis)."""
from sqlalchemy import Column, DateTime, Enum, Integer, String, func
from sqlalchemy.orm import relationship

from app.database.connection import Base
from app.models.enums import PerfilEnum


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(120), nullable=False)
    email = Column(String(160), nullable=False, unique=True, index=True)  # RN01
    senha_hash = Column(String(255), nullable=False)  # RN02 - nunca texto puro
    perfil = Column(Enum(PerfilEnum), nullable=False, default=PerfilEnum.CLIENTE)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    pedidos = relationship("Pedido", back_populates="cliente")
    fidelidade = relationship("Fidelidade", back_populates="cliente", uselist=False)
    logs = relationship("LogAuditoria", back_populates="usuario")
