"""
Ponto de entrada da API "Raízes do Nordeste" — Trilha Back-End.

Consulte ANALISE_TECNICA.md para o mapeamento completo requisito → código.
"""
from fastapi import FastAPI

from app.core.config import settings
from app.database.connection import init_db
from app.exceptions.handlers import register_exception_handlers
from app.routers import auth, catalogo, estoque, fidelidade, pagamentos, pedidos

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "API de referência para o estudo de caso **Rede Raízes do Nordeste** "
        "(UNINTER, Projeto Multidisciplinar — Trilha Back-End, 2026).\n\n"
        "Consulte `ANALISE_TECNICA.md` no repositório para o mapeamento "
        "completo entre requisitos do PDF (RF/RNF/RN) e o código."
    ),
)

register_exception_handlers(app)

app.include_router(auth.router)
app.include_router(catalogo.router)
app.include_router(estoque.router)
app.include_router(pedidos.router)
app.include_router(pagamentos.router)
app.include_router(fidelidade.router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health", tags=["Infra"], summary="Verificação de saúde da API")
def health():
    return {"status": "ok", "app": settings.app_name, "version": settings.app_version}
