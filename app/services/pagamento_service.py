"""
Implementa RF08 (solicitação de pagamento via serviço externo mock + registro).
RN06/RN07: resultado do pagamento move o pedido para EM_PREPARO (aprovado) ou
PAGAMENTO_RECUSADO (recusado). RN12: toda tentativa gera um registro.
"""
from sqlalchemy.orm import Session

from app.exceptions.custom_exceptions import ConflictError, NotFoundError
from app.models.enums import StatusPagamentoEnum, StatusPedidoEnum
from app.models.log_auditoria import LogAuditoria
from app.models.pagamento import Pagamento
from app.repositories.fidelidade_repository import FidelidadeRepository, LogAuditoriaRepository
from app.repositories.pagamento_repository import PagamentoRepository
from app.services.pagamento_mock import PagamentoGatewayMock
from app.services.pedido_service import PedidoService


class PagamentoService:
    def __init__(self, db: Session):
        self.db = db
        self.pagamento_repo = PagamentoRepository(db)
        self.pedido_service = PedidoService(db)
        self.fidelidade_repo = FidelidadeRepository(db)
        self.log_repo = LogAuditoriaRepository(db)

    def simular_pagamento(self, pedido_id: int, forma_pagamento: str, usuario_id: int) -> Pagamento:
        pedido = self.pedido_service.obter_pedido(pedido_id)
        if pedido is None:
            raise NotFoundError(f"Pedido {pedido_id} não encontrado.")
        if pedido.status != StatusPedidoEnum.AGUARDANDO_PAGAMENTO:
            raise ConflictError(
                f"Pedido {pedido_id} não está aguardando pagamento (status atual: {pedido.status.value})."
            )

        # RF08 — solicita ao "gateway" externo (mock) e SEMPRE registra o resultado (RN12)
        status_pagamento, payload = PagamentoGatewayMock.solicitar_pagamento(
            pedido.total, forma_pagamento
        )
        pagamento = self.pagamento_repo.create(
            Pagamento(
                pedido_id=pedido_id,
                status=status_pagamento,
                forma_pagamento=forma_pagamento,
                payload_resposta=payload,
            )
        )

        # RN06/RN07 — atualiza o pedido conforme o resultado
        if status_pagamento == StatusPagamentoEnum.APROVADO:
            self.pedido_service._forcar_status_interno(pedido, StatusPedidoEnum.EM_PREPARO)
            self._creditar_fidelidade(pedido.cliente_id, pedido.total)
        else:
            self.pedido_service._forcar_status_interno(pedido, StatusPedidoEnum.PAGAMENTO_RECUSADO)

        self.log_repo.create(
            LogAuditoria(
                usuario_id=usuario_id,
                acao=f"PAGAMENTO_{status_pagamento.value}",
                entidade="Pedido",
                entidade_id=pedido_id,
                detalhes=f"forma_pagamento={forma_pagamento}",
            )
        )
        return pagamento

    def _creditar_fidelidade(self, cliente_id: int, total) -> None:
        """RN09 — só credita pontos se houver consentimento LGPD explícito."""
        fidelidade = self.fidelidade_repo.get_by_cliente_id(cliente_id)
        if fidelidade is None or not fidelidade.consentimento_lgpd:
            return  # "O PDF não especifica" pontuação sem consentimento -> não credita (LGPD)
        pontos_ganhos = int(total)  # [DECISÃO DE IMPLEMENTAÇÃO] 1 ponto por unidade monetária
        fidelidade.pontos_saldo += pontos_ganhos
        self.fidelidade_repo.save(fidelidade)
