"""Schemas de Usuario/Auth — RF01."""
from pydantic import BaseModel, EmailStr, Field

from app.models.enums import PerfilEnum
from app.schemas.base import CamelModel


class UsuarioCreate(CamelModel):
    """Payload de criação — RF01."""

    nome: str = Field(min_length=2, max_length=120, examples=["Maria Souza"])
    email: EmailStr = Field(examples=["maria@exemplo.com"])
    senha: str = Field(min_length=6, max_length=100, examples=["Senha@123"])
    perfil: PerfilEnum = Field(default=PerfilEnum.CLIENTE)


class UsuarioResponse(CamelModel):
    """Nunca inclui senha/senha_hash (RNF01)."""

    id: int
    nome: str
    email: EmailStr
    perfil: PerfilEnum


class LoginRequest(CamelModel):
    email: EmailStr = Field(examples=["maria@exemplo.com"])
    senha: str = Field(examples=["Senha@123"])


class TokenResponse(BaseModel):
    """
    Mantido em snake_case (não herda de CamelModel) por convenção do padrão
    OAuth2 (RFC 6749: access_token, token_type) — o PDF não especifica um
    formato de resposta de login, então seguimos a convenção do mercado.
    """

    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioResponse
