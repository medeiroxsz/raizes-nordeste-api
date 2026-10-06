"""Acesso a dados de Fidelidade e LogAuditoria — camada Infrastructure."""
from sqlalchemy.orm import Session

from app.models.fidelidade import Fidelidade
from app.models.log_auditoria import LogAuditoria


class FidelidadeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_cliente_id(self, cliente_id: int) -> Fidelidade | None:
        return self.db.query(Fidelidade).filter(Fidelidade.cliente_id == cliente_id).first()

    def create(self, fidelidade: Fidelidade) -> Fidelidade:
        self.db.add(fidelidade)
        self.db.commit()
        self.db.refresh(fidelidade)
        return fidelidade

    def save(self, fidelidade: Fidelidade) -> Fidelidade:
        self.db.commit()
        self.db.refresh(fidelidade)
        return fidelidade


class LogAuditoriaRepository:
    """[DECISÃO DE IMPLEMENTAÇÃO] suporte a RNF02."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, log: LogAuditoria) -> LogAuditoria:
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def list_by_entidade(self, entidade: str, entidade_id: int) -> list[LogAuditoria]:
        return (
            self.db.query(LogAuditoria)
            .filter(LogAuditoria.entidade == entidade, LogAuditoria.entidade_id == entidade_id)
            .order_by(LogAuditoria.id.desc())
            .all()
        )
