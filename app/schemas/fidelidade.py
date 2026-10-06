"""Schemas de Fidelidade — RF06 (pontos + consentimento LGPD)."""
from pydantic import Field

from app.schemas.base import CamelModel


class FidelidadeResponse(CamelModel):
    cliente_id: int
    pontos_saldo: int
    consentimento_lgpd: bool


class ConsentimentoUpdate(CamelModel):
    consentimento_lgpd: bool = Field(examples=[True])


class ResgatePontosRequest(CamelModel):
    pontos: int = Field(gt=0, examples=[100])
