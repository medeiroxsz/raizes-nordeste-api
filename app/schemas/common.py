"""Schema de erro padrão, usado apenas para fins de documentação no Swagger."""
from pydantic import BaseModel, Field


class ErroDetalhe(BaseModel):
    field: str
    issue: str


class ErroResponse(BaseModel):
    error: str = Field(examples=["ESTOQUE_INSUFICIENTE"])
    message: str = Field(examples=["Não há quantidade suficiente para um ou mais itens."])
    details: list[ErroDetalhe] = []
    timestamp: str
    path: str
