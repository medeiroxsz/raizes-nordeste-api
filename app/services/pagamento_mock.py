"""
Simulação do serviço externo de pagamento (estudo de caso, item 5:
"A Raízes do Nordeste não processa pagamentos diretamente em seu sistema
principal"). Isolado em módulo próprio para atender RNF04 (tolerância a
falhas): se o "gateway" externo mudar, só este arquivo muda.

[DECISÃO DE IMPLEMENTAÇÃO] Regra simples e determinística para fins de
teste: forma de pagamento "RECUSAR" simula negativa; qualquer outra é
aprovada. Isso permite reproduzir os dois cenários exigidos pelo roteiro
(sucesso e falha) sem depender de aleatoriedade.
"""
from app.models.enums import StatusPagamentoEnum


class PagamentoGatewayMock:
    @staticmethod
    def solicitar_pagamento(valor, forma_pagamento: str) -> tuple[StatusPagamentoEnum, str]:
        if forma_pagamento.upper() == "RECUSAR":
            return StatusPagamentoEnum.RECUSADO, '{"motivo": "saldo insuficiente (mock)"}'
        return StatusPagamentoEnum.APROVADO, '{"autorizacao": "MOCK-OK"}'
