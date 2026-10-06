"""Schemas de Estoque — RF05."""
from pydantic import Field

from app.models.enums import TipoMovimentoEstoqueEnum
from app.schemas.base import CamelModel


class MovimentoEstoqueCreate(CamelModel):
    unidade_id: int = Field(examples=[1])
    produto_id: int = Field(examples=[1])
    quantidade: int = Field(gt=0, examples=[10])
    tipo_movimento: TipoMovimentoEstoqueEnum = Field(examples=["ENTRADA"])


class EstoqueResponse(CamelModel):
    id: int
    unidade_id: int
    produto_id: int
    quantidade: int
