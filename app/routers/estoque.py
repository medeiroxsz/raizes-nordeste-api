"""Endpoints de Estoque — RF05."""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.security import require_roles
from app.database.connection import get_db
from app.models.enums import PerfilEnum
from app.models.usuario import Usuario
from app.schemas.estoque import EstoqueResponse, MovimentoEstoqueCreate
from app.services.catalogo_service import CatalogoService
from app.services.estoque_service import EstoqueService

router = APIRouter(tags=["Estoque"])


@router.post(
    "/estoque/movimentacoes",
    response_model=EstoqueResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar movimentação de estoque",
    description=(
        "Atende ao requisito funcional **RF05**. Registra entrada ou saída de "
        "estoque de um produto em uma unidade. **RN08**: a saída não pode "
        "deixar o saldo negativo."
    ),
    responses={
        404: {"description": "Unidade ou produto não encontrado"},
        409: {"description": "Saldo insuficiente para saída (RN08)"},
    },
)
def movimentar_estoque(
    dados: MovimentoEstoqueCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_roles(PerfilEnum.ADMIN, PerfilEnum.GERENTE)),
):
    return EstoqueService(db).movimentar(dados, usuario_id=usuario.id)


@router.get(
    "/estoque",
    response_model=list[EstoqueResponse],
    summary="Consultar estoque por unidade",
    description="Atende ao requisito funcional **RF05**.",
)
def listar_estoque(
    unidade_id: int = Query(..., description="ID da unidade"),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_roles(PerfilEnum.ADMIN, PerfilEnum.GERENTE, PerfilEnum.COZINHA)
    ),
):
    return CatalogoService(db).listar_estoque_por_unidade(unidade_id)
