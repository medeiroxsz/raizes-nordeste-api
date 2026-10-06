"""Endpoints de Pagamento — RF08 (integração simulada de pagamento)."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.connection import get_db
from app.models.usuario import Usuario
from app.schemas.pagamento import PagamentoResponse, PagamentoSimularRequest
from app.services.pagamento_service import PagamentoService

router = APIRouter(tags=["Pagamentos (mock)"])


@router.post(
    "/pagamentos/{pedido_id}/simular",
    response_model=PagamentoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Simular pagamento de um pedido",
    description=(
        "Atende ao requisito funcional **RF08**. O sistema **não processa "
        "pagamento real** — apenas solicita ao serviço externo (mock), recebe "
        "a confirmação/negativa e registra o resultado (**RN12**), atualizando "
        "o status do pedido conforme **RN06/RN07**. "
        "Use `formaPagamento=RECUSAR` para simular um pagamento negado."
    ),
    responses={
        404: {"description": "Pedido não encontrado"},
        409: {"description": "Pedido não está aguardando pagamento"},
    },
)
def simular_pagamento(
    pedido_id: int,
    dados: PagamentoSimularRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return PagamentoService(db).simular_pagamento(
        pedido_id, dados.forma_pagamento, usuario_id=usuario.id
    )
