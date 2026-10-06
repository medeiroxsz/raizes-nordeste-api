"""Endpoints de Unidade e Produto — RF02 (cardápio por unidade)."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import require_roles
from app.database.connection import get_db
from app.models.enums import PerfilEnum
from app.schemas.unidade import (
    ProdutoCreate,
    ProdutoDisponivelResponse,
    ProdutoResponse,
    UnidadeCreate,
    UnidadeResponse,
)
from app.services.catalogo_service import CatalogoService

router = APIRouter(tags=["Catálogo (Unidades e Produtos)"])


@router.post(
    "/unidades",
    response_model=UnidadeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar unidade",
    description="[DECISÃO DE IMPLEMENTAÇÃO] necessário para dar suporte a RF02/RF05.",
    dependencies=[Depends(require_roles(PerfilEnum.ADMIN, PerfilEnum.GERENTE))],
)
def criar_unidade(dados: UnidadeCreate, db: Session = Depends(get_db)):
    return CatalogoService(db).criar_unidade(dados)


@router.get(
    "/unidades",
    response_model=list[UnidadeResponse],
    summary="Listar unidades",
    description="Lista as unidades da rede (público, sem autenticação).",
)
def listar_unidades(db: Session = Depends(get_db)):
    return CatalogoService(db).listar_unidades()


@router.post(
    "/produtos",
    response_model=ProdutoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar produto",
    description="[DECISÃO DE IMPLEMENTAÇÃO] cadastro de produto no catálogo global.",
    dependencies=[Depends(require_roles(PerfilEnum.ADMIN, PerfilEnum.GERENTE))],
)
def criar_produto(dados: ProdutoCreate, db: Session = Depends(get_db)):
    return CatalogoService(db).criar_produto(dados)


@router.get(
    "/unidades/{unidade_id}/produtos",
    response_model=list[ProdutoDisponivelResponse],
    summary="Consultar cardápio de uma unidade",
    description=(
        "Atende ao requisito funcional **RF02**. Aplica **RN03**: só retorna "
        "produtos com saldo de estoque maior que zero na unidade informada."
    ),
    responses={404: {"description": "Unidade não encontrada"}},
)
def cardapio_por_unidade(unidade_id: int, db: Session = Depends(get_db)):
    resultados = CatalogoService(db).cardapio_por_unidade(unidade_id)
    return [
        ProdutoDisponivelResponse(
            id=produto.id,
            nome=produto.nome,
            descricao=produto.descricao,
            preco=produto.preco,
            categoria=produto.categoria,
            sazonal=produto.sazonal,
            quantidade_disponivel=quantidade,
        )
        for produto, quantidade in resultados
    ]
