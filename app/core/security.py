"""
Segurança da aplicação — atende RNF01 (LGPD/segurança) e sustenta RF01.

- Hash de senha (RN02): nunca armazenamos senha em texto puro.
- JWT: autenticação stateless.
- require_roles: autorização por perfil, usada nos routers (RF04, RF05 etc.).
"""
from datetime import datetime, timedelta, timezone

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.connection import get_db
from app.exceptions.custom_exceptions import ForbiddenError, UnauthorizedError
from app.models.enums import PerfilEnum
from app.models.usuario import Usuario

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def hash_senha(senha_plana: str) -> str:
    """RN02 — a senha nunca é persistida em texto puro."""
    return pwd_context.hash(senha_plana)


def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    return pwd_context.verify(senha_plana, senha_hash)


def criar_access_token(subject: str, perfil: str) -> str:
    expira_em = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": subject, "perfil": perfil, "exp": expira_em}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def _decodificar_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError:
        raise UnauthorizedError("Token inválido ou expirado.")


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    """Dependência usada em todos os endpoints protegidos (RNF01)."""
    if not token:
        raise UnauthorizedError("Autenticação obrigatória. Envie um Bearer token.")
    payload = _decodificar_token(token)
    usuario_id = payload.get("sub")
    usuario = db.query(Usuario).filter(Usuario.id == int(usuario_id)).first()
    if usuario is None:
        raise UnauthorizedError("Usuário do token não existe mais.")
    return usuario


def require_roles(*perfis_permitidos: PerfilEnum):
    """
    Fábrica de dependência para autorização por perfil.

    Usado, por exemplo, em `PATCH /pedidos/{id}/status` (RF04, perfis
    COZINHA/GERENTE/ADMIN) e em `POST /estoque/movimentacoes` (RF05,
    perfis GERENTE/ADMIN).
    """

    def _checker(usuario: Usuario = Depends(get_current_user)) -> Usuario:
        if usuario.perfil not in perfis_permitidos:
            raise ForbiddenError(
                f"Perfil '{usuario.perfil}' não tem permissão para esta ação."
            )
        return usuario

    return _checker
