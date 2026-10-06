"""Implementa RF06 (fidelização) — RN09 (consentimento) e RN10 (saldo)."""
from sqlalchemy.orm import Session

from app.exceptions.custom_exceptions import (
    ConsentimentoLgpdAusenteError,
    SaldoPontosInsuficienteError,
)
from app.models.fidelidade import Fidelidade
from app.repositories.fidelidade_repository import FidelidadeRepository


class FidelidadeService:
    def __init__(self, db: Session):
        self.repo = FidelidadeRepository(db)

    def obter_ou_criar(self, cliente_id: int) -> Fidelidade:
        fidelidade = self.repo.get_by_cliente_id(cliente_id)
        if fidelidade is None:
            fidelidade = self.repo.create(Fidelidade(cliente_id=cliente_id, pontos_saldo=0))
        return fidelidade

    def atualizar_consentimento(self, cliente_id: int, consentimento: bool) -> Fidelidade:
        """RN09 — registro explícito de consentimento LGPD."""
        fidelidade = self.obter_ou_criar(cliente_id)
        fidelidade.consentimento_lgpd = consentimento
        return self.repo.save(fidelidade)

    def resgatar_pontos(self, cliente_id: int, pontos: int) -> Fidelidade:
        """RN10 — resgate não pode exceder o saldo disponível."""
        fidelidade = self.obter_ou_criar(cliente_id)
        if not fidelidade.consentimento_lgpd:
            raise ConsentimentoLgpdAusenteError(
                "É necessário consentimento LGPD para participar do programa de fidelidade."
            )
        if fidelidade.pontos_saldo < pontos:
            raise SaldoPontosInsuficienteError(
                "Saldo de pontos insuficiente para o resgate.",
                details=[{"field": "pontos", "issue": f"Saldo atual: {fidelidade.pontos_saldo}"}],
            )
        fidelidade.pontos_saldo -= pontos
        return self.repo.save(fidelidade)
