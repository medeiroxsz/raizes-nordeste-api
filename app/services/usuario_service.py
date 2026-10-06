"""
Implementa RF01 (cadastro e autenticação de usuários com perfis).
Regras de negócio: RN01 (e-mail único) e RN02 (senha sempre com hash).
"""
from sqlalchemy.orm import Session

from app.core.security import criar_access_token, hash_senha, verificar_senha
from app.exceptions.custom_exceptions import EmailDuplicadoError, UnauthorizedError
from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.usuario import LoginRequest, UsuarioCreate


class UsuarioService:
    def __init__(self, db: Session):
        self.repo = UsuarioRepository(db)

    def cadastrar(self, dados: UsuarioCreate) -> Usuario:
        """RF01 + RN01: bloqueia e-mail duplicado."""
        if self.repo.get_by_email(dados.email) is not None:
            raise EmailDuplicadoError(f"O e-mail '{dados.email}' já está cadastrado.")

        usuario = Usuario(
            nome=dados.nome,
            email=dados.email,
            senha_hash=hash_senha(dados.senha),  # RN02
            perfil=dados.perfil,
        )
        return self.repo.create(usuario)

    def autenticar(self, dados: LoginRequest) -> tuple[Usuario, str]:
        """RF01: login. Retorna o usuário e o token JWT."""
        usuario = self.repo.get_by_email(dados.email)
        if usuario is None or not verificar_senha(dados.senha, usuario.senha_hash):
            raise UnauthorizedError("E-mail ou senha inválidos.")
        token = criar_access_token(subject=str(usuario.id), perfil=usuario.perfil.value)
        return usuario, token
