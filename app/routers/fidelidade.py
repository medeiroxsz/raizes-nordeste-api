"""Endpoints de Fidelidade — RF06 (pontos e consentimento LGPD)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_roles
from app.database.connection import get_db
from app.exceptions.custom_exceptions import ForbiddenError
from app.models.enums import PerfilEnum
from app.models.usuario import Usuario
from app.schemas.fidelidade import ConsentimentoUpdate, FidelidadeResponse, ResgatePontosRequest
from app.services.fidelidade_service import FidelidadeService

router = APIRouter(tags=["Fidelidade"])


@router.get(
    "/fidelidade/{cliente_id}",
    response_model=FidelidadeResponse,
    summary="Consultar saldo de pontos",
    description="Atende ao requisito funcional **RF06**. Só o próprio cliente ou GERENTE/ADMIN podem consultar.",
)
def obter_fidelidade(
    cliente_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)
):
    if usuario.id != cliente_id and usuario.perfil not in (PerfilEnum.GERENTE, PerfilEnum.ADMIN):
        raise ForbiddenError("Você só pode consultar o próprio saldo de fidelidade.")
    return FidelidadeService(db).obter_ou_criar(cliente_id)


@router.put(
    "/fidelidade/{cliente_id}/consentimento",
    response_model=FidelidadeResponse,
    summary="Registrar consentimento LGPD",
    description=(
        "**RN09** — o cliente precisa registrar consentimento explícito antes "
        "de acumular pontos de fidelidade (LGPD, estudo de caso item 4)."
    ),
)
def atualizar_consentimento(
    cliente_id: int,
    dados: ConsentimentoUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    if usuario.id != cliente_id:
        raise ForbiddenError("Você só pode alterar o próprio consentimento.")
    return FidelidadeService(db).atualizar_consentimento(cliente_id, dados.consentimento_lgpd)


@router.post(
    "/fidelidade/resgate",
    response_model=FidelidadeResponse,
    summary="Resgatar pontos",
    description="Atende ao requisito funcional **RF06**. **RN10**: não pode exceder o saldo.",
    responses={409: {"description": "Saldo de pontos insuficiente (RN10) ou sem consentimento (RN09)"}},
)
def resgatar_pontos(
    dados: ResgatePontosRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_roles(PerfilEnum.CLIENTE)),
):
    return FidelidadeService(db).resgatar_pontos(usuario.id, dados.pontos)
