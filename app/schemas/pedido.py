"""Schemas de Pedido — RF03 (criação), RF04 (status), RF09 (canal)."""
from decimal import Decimal

from pydantic import Field, field_validator

from app.models.enums import CanalPedidoEnum, StatusPedidoEnum
from app.schemas.base import CamelModel


class ItemPedidoCreate(CamelModel):
    produto_id: int = Field(examples=[1])
    quantidade: int = Field(gt=0, examples=[2])


class PedidoCreate(CamelModel):
    """
    RN04: canal_pedido (JSON: canalPedido) é obrigatório e deve pertencer ao
    Enum — exigência literal do PDF, seção 5.5 ("Requisito mínimo").
    """

    unidade_id: int = Field(examples=[1])
    canal_pedido: CanalPedidoEnum = Field(examples=["TOTEM"])
    itens: list[ItemPedidoCreate] = Field(min_length=1)
    forma_pagamento: str = Field(default="MOCK", examples=["PIX"])

    @field_validator("itens")
    @classmethod
    def itens_nao_vazios(cls, v):
        if not v:
            raise ValueError("O pedido deve conter ao menos um item.")
        return v


class ItemPedidoResponse(CamelModel):
    produto_id: int
    quantidade: int
    preco_unitario: Decimal


class PedidoResponse(CamelModel):
    id: int
    unidade_id: int
    cliente_id: int
    canal_pedido: CanalPedidoEnum
    status: StatusPedidoEnum
    total: Decimal
    itens: list[ItemPedidoResponse]


class PedidoStatusUpdate(CamelModel):
    """RN06 — transição de status validada no service."""

    novo_status: StatusPedidoEnum = Field(examples=["EM_PREPARO"])
