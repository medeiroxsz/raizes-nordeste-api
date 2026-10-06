"""
Exceções de domínio. Cada uma é mapeada para um status HTTP em
app/exceptions/handlers.py, mantendo o padrão de erro único descrito em
ANALISE_TECNICA.md, seção 16.
"""


class DomainError(Exception):
    """Classe-base para todas as exceções de domínio da aplicação."""

    status_code: int = 400
    error_code: str = "ERRO_DOMINIO"

    def __init__(self, message: str, details: list | None = None):
        self.message = message
        self.details = details or []
        super().__init__(message)


class NotFoundError(DomainError):
    status_code = 404
    error_code = "RECURSO_NAO_ENCONTRADO"


class ConflictError(DomainError):
    status_code = 409
    error_code = "CONFLITO"


class UnauthorizedError(DomainError):
    status_code = 401
    error_code = "NAO_AUTENTICADO"


class ForbiddenError(DomainError):
    status_code = 403
    error_code = "SEM_PERMISSAO"


class ValidationDomainError(DomainError):
    status_code = 422
    error_code = "ERRO_VALIDACAO"


class EstoqueInsuficienteError(ConflictError):
    """RN05, RN08 — estoque insuficiente para concluir a operação."""

    error_code = "ESTOQUE_INSUFICIENTE"


class TransicaoStatusInvalidaError(ConflictError):
    """RN06 — transição de status do pedido não permitida."""

    error_code = "TRANSICAO_STATUS_INVALIDA"


class EmailDuplicadoError(ConflictError):
    """RN01 — e-mail já cadastrado."""

    error_code = "EMAIL_DUPLICADO"


class ConsentimentoLgpdAusenteError(ConflictError):
    """RN09 — pontos de fidelidade exigem consentimento LGPD."""

    error_code = "CONSENTIMENTO_LGPD_AUSENTE"


class SaldoPontosInsuficienteError(ConflictError):
    """RN10 — resgate maior que o saldo disponível."""

    error_code = "SALDO_PONTOS_INSUFICIENTE"
