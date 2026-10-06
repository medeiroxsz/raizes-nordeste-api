"""Endpoints de autenticação e cadastro de usuários — RF01."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.usuario import LoginRequest, TokenResponse, UsuarioCreate, UsuarioResponse
from app.services.usuario_service import UsuarioService

router = APIRouter(tags=["Autenticação e Usuários"])


@router.post(
    "/usuarios",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar usuário",
    description=(
        "Atende ao requisito funcional **RF01**. Cadastra um usuário com perfil "
        "(CLIENTE, ATENDENTE, COZINHA, GERENTE ou ADMIN). A senha é armazenada "
        "com hash (RN02) e o e-mail deve ser único (RN01)."
    ),
    responses={409: {"description": "E-mail já cadastrado (RN01)"}},
)
def cadastrar_usuario(dados: UsuarioCreate, db: Session = Depends(get_db)):
    usuario = UsuarioService(db).cadastrar(dados)
    return usuario


@router.post(
    "/auth/login",
    response_model=TokenResponse,
    summary="Autenticar usuário",
    description="Atende ao requisito funcional **RF01**. Retorna um token JWT Bearer.",
    responses={401: {"description": "Credenciais inválidas"}},
)
def login(dados: LoginRequest, db: Session = Depends(get_db)):
    usuario, token = UsuarioService(db).autenticar(dados)
    return TokenResponse(access_token=token, usuario=usuario)
