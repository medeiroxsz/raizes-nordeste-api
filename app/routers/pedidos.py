"""Endpoints de Pedido — RF03 (criação), RF04 (status), RF09 (multicanalidade)."""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_roles
from app.database.connection import get_db
from app.models.enums import CanalPedidoEnum, PerfilEnum
from app.models.usuario import Usuario
from app.schemas.pedido import PedidoCreate, PedidoResponse, PedidoStatusUpdate
from app.services.pedido_service import PedidoService

router = APIRouter(tags=["Pedidos"])


@router.post(
    "/pedidos",
    response_model=PedidoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar pedido",
    description=(
        "Atende aos requisitos funcionais **RF03** e **RF09** (multicanalidade). "
        "**RN04**: `canal_pedido` é obrigatório e deve ser um dos valores "
        "APP, TOTEM, BALCAO, PICKUP, WEB. **RN05**: o pedido só é criado se "
        "houver estoque suficiente para todos os itens na unidade informada."
    ),
    responses={
        404: {"description": "Unidade ou produto não encontrado"},
        409: {"description": "Estoque insuficiente (RN05)"},
        422: {"description": "Payload inválido (ex.: canal ausente/ inválido, sem itens)"},
    },
)
def criar_pedido(
    dados: PedidoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_roles(PerfilEnum.CLIENTE, PerfilEnum.ATENDENTE, PerfilEnum.ADMIN)
    ),
):
    return PedidoService(db).criar_pedido(dados, cliente_id=usuario.id)


@router.get(
    "/pedidos",
    response_model=list[PedidoResponse],
    summary="Listar pedidos (com filtro por canal)",
    description=(
        "Atende ao requisito funcional **RF09**: permite filtrar por "
        "`?canalPedido=TOTEM`, por exemplo, para consolidação operacional."
    ),
)
def listar_pedidos(
    canalPedido: CanalPedidoEnum | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return PedidoService(db).listar_pedidos(canal_pedido=canalPedido)


@router.get(
    "/pedidos/{pedido_id}",
    response_model=PedidoResponse,
    summary="Consultar um pedido",
    description="Atende ao requisito funcional **RF03**.",
    responses={404: {"description": "Pedido não encontrado"}},
)
def obter_pedido(
    pedido_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)
):
    return PedidoService(db).obter_pedido(pedido_id)


@router.patch(
    "/pedidos/{pedido_id}/status",
    response_model=PedidoResponse,
    summary="Atualizar status do pedido",
    description=(
        "Atende ao requisito funcional **RF04**. **RN06**: só permite "
        "transições válidas da máquina de estados "
        "(AGUARDANDO_PAGAMENTO → EM_PREPARO → PRONTO → ENTREGUE, ou CANCELADO "
        "a qualquer momento antes de ENTREGUE)."
    ),
    responses={
        404: {"description": "Pedido não encontrado"},
        409: {"description": "Transição de status inválida (RN06)"},
    },
)
def atualizar_status_pedido(
    pedido_id: int,
    dados: PedidoStatusUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_roles(PerfilEnum.COZINHA, PerfilEnum.GERENTE, PerfilEnum.ADMIN)
    ),
):
    return PedidoService(db).atualizar_status(pedido_id, dados.novo_status, usuario_id=usuario.id)
