"""
Infraestrutura de persistência (camada Infrastructure).

[DECISÃO DE IMPLEMENTAÇÃO] SQLite é usado por padrão para permitir execução
local sem dependências externas (ver ANALISE_TECNICA.md, seção 11). Trocar
para PostgreSQL/MySQL exige apenas alterar DATABASE_URL no .env — o restante
do código (models/repositories) não muda, pois usa SQLAlchemy ORM.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependência FastAPI que fornece uma sessão de banco por requisição."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Cria as tabelas a partir dos models.

    [DECISÃO DE IMPLEMENTAÇÃO] O PDF menciona migrations "quando necessárias".
    Para o MVP, `create_all` é suficiente e evita a complexidade de Alembic;
    a evolução para migrations versionadas está listada em
    ANALISE_TECNICA.md, seção 22 (RECOMENDADO/OPCIONAL).
    """
    import app.models  # noqa: F401  garante que todos os models sejam registrados
    Base.metadata.create_all(bind=engine)
