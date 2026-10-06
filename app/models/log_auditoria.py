"""
Entidade LogAuditoria — [DECISÃO DE IMPLEMENTAÇÃO] criada para atender
RNF02 (logs/auditoria de ações sensíveis: cancelamentos, mudanças de status,
ajustes de estoque), exigido de forma textual no estudo de caso (item 3) e
no roteiro da trilha (seção "Segurança, LGPD, Logs e Auditoria").
"""
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.database.connection import Base


class LogAuditoria(Base):
    __tablename__ = "logs_auditoria"

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    acao = Column(String(60), nullable=False)
    entidade = Column(String(60), nullable=False)
    entidade_id = Column(Integer, nullable=False)
    detalhes = Column(String(255), nullable=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    usuario = relationship("Usuario", back_populates="logs")
