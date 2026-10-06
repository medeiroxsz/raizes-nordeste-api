"""Schemas de Pagamento — RF08 (mock)."""
from pydantic import Field

from app.models.enums import StatusPagamentoEnum
from app.schemas.base import CamelModel


class PagamentoSimularRequest(CamelModel):
    forma_pagamento: str = Field(default="PIX", examples=["PIX"])


class PagamentoResponse(CamelModel):
    id: int
    pedido_id: int
    status: StatusPagamentoEnum
    forma_pagamento: str
    payload_resposta: str | None
