"""Schemas de Unidade e Produto — RF02 (cardápio por unidade)."""
from decimal import Decimal

from pydantic import Field

from app.schemas.base import CamelModel


class UnidadeCreate(CamelModel):
    nome: str = Field(examples=["Raízes do Nordeste - Boa Viagem"])
    cidade: str = Field(examples=["Recife"])
    tipo_cozinha: str = Field(default="COMPLETA", examples=["COMPLETA"])


class UnidadeResponse(CamelModel):
    id: int
    nome: str
    cidade: str
    tipo_cozinha: str


class ProdutoCreate(CamelModel):
    nome: str = Field(examples=["Tapioca de Queijo"])
    descricao: str | None = Field(default=None, examples=["Tapioca recheada com queijo coalho"])
    preco: Decimal = Field(gt=0, examples=[12.90])
    categoria: str | None = Field(default=None, examples=["Salgados"])
    sazonal: bool = Field(default=False)


class ProdutoResponse(CamelModel):
    id: int
    nome: str
    descricao: str | None
    preco: Decimal
    categoria: str | None
    sazonal: bool


class ProdutoDisponivelResponse(ProdutoResponse):
    """Usado em GET /unidades/{id}/produtos — inclui saldo em estoque (RN03)."""

    quantidade_disponivel: int
