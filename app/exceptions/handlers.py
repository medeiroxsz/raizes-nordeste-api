"""
Handlers globais — garantem que TODA falha da API (erro de domínio, erro de
validação do Pydantic ou erro inesperado) siga o mesmo formato JSON,
conforme ANALISE_TECNICA.md, seção 16.
"""
from datetime import datetime, timezone

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.exceptions.custom_exceptions import DomainError


def _erro_payload(error_code: str, message: str, details: list, path: str) -> dict:
    return {
        "error": error_code,
        "message": message,
        "details": details,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "path": path,
    }


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError):
        return JSONResponse(
            status_code=exc.status_code,
            content=_erro_payload(exc.error_code, exc.message, exc.details, str(request.url.path)),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        details = [
            {"field": ".".join(str(p) for p in err["loc"] if p != "body"), "issue": err["msg"]}
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_erro_payload(
                "ERRO_VALIDACAO", "Payload inválido.", details, str(request.url.path)
            ),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_erro_payload(
                "ERRO_INTERNO", "Erro interno inesperado.", [], str(request.url.path)
            ),
        )
