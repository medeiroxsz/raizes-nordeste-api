"""Entidade Fidelidade — RF06 (pontos e consentimento LGPD, RN09/RN10)."""
from sqlalchemy import Boolean, CheckConstraint, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Fidelidade(Base):
    __tablename__ = "fidelidades"
    __table_args__ = (CheckConstraint("pontos_saldo >= 0", name="ck_pontos_saldo_nao_negativo"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, unique=True)
    pontos_saldo = Column(Integer, nullable=False, default=0)
    consentimento_lgpd = Column(Boolean, nullable=False, default=False)  # RN09

    cliente = relationship("Usuario", back_populates="fidelidade")
