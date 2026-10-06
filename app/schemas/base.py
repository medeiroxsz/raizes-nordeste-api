"""
Base para schemas cujo contrato JSON deve usar camelCase — exigido
explicitamente pelo PDF (seção 5.5: "inclua explicitamente o campo
canalPedido"; exemplos com `produtoId`, `clienteId`, `formaPagamento`).

Internamente o código Python continua em snake_case (PEP 8); o
`alias_generator` converte para camelCase apenas na borda HTTP.
`populate_by_name=True` permite que requests aceitem tanto o alias
(camelCase) quanto o nome do campo em snake_case.
"""
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )
