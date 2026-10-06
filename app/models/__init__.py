"""Garante que todos os models sejam registrados no Base.metadata."""
from app.models.usuario import Usuario  # noqa: F401
from app.models.unidade import Unidade  # noqa: F401
from app.models.produto import Produto  # noqa: F401
from app.models.estoque import Estoque  # noqa: F401
from app.models.pedido import Pedido  # noqa: F401
from app.models.item_pedido import ItemPedido  # noqa: F401
from app.models.pagamento import Pagamento  # noqa: F401
from app.models.fidelidade import Fidelidade  # noqa: F401
from app.models.log_auditoria import LogAuditoria  # noqa: F401
