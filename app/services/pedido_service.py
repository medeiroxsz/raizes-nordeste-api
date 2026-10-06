"""
Implementa:
- RF03: realização de pedidos (itens, valores, status).
- RF09 (multicanalidade): canalPedido obrigatório e filtrável.
- RF04: atualização de status do pedido.
- RN04: canalPedido obrigatório/válido (garantido pelo Schema + reforçado aqui).
- RN05: pedido não pode ser criado sem estoque suficiente.
- RN06: máquina de estados do pedido.
"""
from sqlalchemy.orm import Session

from app.exceptions.custom_exceptions import NotFoundError, TransicaoStatusInvalidaError
from app.models.enums import CanalPedidoEnum, StatusPedidoEnum
from app.models.item_pedido import ItemPedido
from app.models.log_auditoria import LogAuditoria
from app.models.pedido import Pedido
from app.repositories.catalogo_repository import ProdutoRepository, UnidadeRepository
from app.repositories.fidelidade_repository import LogAuditoriaRepository
from app.repositories.pedido_repository import PedidoRepository
from app.schemas.pedido import PedidoCreate
from app.services.estoque_service import EstoqueService

# RN06 — transições válidas da máquina de estados do pedido.
TRANSICOES_VALIDAS: dict[StatusPedidoEnum, set[StatusPedidoEnum]] = {
    StatusPedidoEnum.AGUARDANDO_PAGAMENTO: {
        StatusPedidoEnum.EM_PREPARO,
        StatusPedidoEnum.PAGAMENTO_RECUSADO,
        StatusPedidoEnum.CANCELADO,
    },
    StatusPedidoEnum.PAGAMENTO_RECUSADO: {StatusPedidoEnum.CANCELADO},
    StatusPedidoEnum.EM_PREPARO: {StatusPedidoEnum.PRONTO, StatusPedidoEnum.CANCELADO},
    StatusPedidoEnum.PRONTO: {StatusPedidoEnum.ENTREGUE, StatusPedidoEnum.CANCELADO},
    StatusPedidoEnum.ENTREGUE: set(),
    StatusPedidoEnum.CANCELADO: set(),
}


class PedidoService:
    def __init__(self, db: Session):
        self.db = db
        self.pedido_repo = PedidoRepository(db)
        self.unidade_repo = UnidadeRepository(db)
        self.produto_repo = ProdutoRepository(db)
        self.estoque_service = EstoqueService(db)
        self.log_repo = LogAuditoriaRepository(db)

    def criar_pedido(self, dados: PedidoCreate, cliente_id: int) -> Pedido:
        """RF03 + RF09 + RN04 + RN05."""
        if self.unidade_repo.get_by_id(dados.unidade_id) is None:
            raise NotFoundError(f"Unidade {dados.unidade_id} não encontrada.")

        # 1ª passada: valida TODOS os itens (produto existe + estoque suficiente)
        # antes de debitar qualquer coisa. Evita debitar o item 1 e só depois
        # descobrir que o item 2 é inválido, o que deixaria estoque debitado
        # sem um pedido correspondente (RN05 precisa ser tudo-ou-nada).
        produtos_validados = []
        for item in dados.itens:
            produto = self.produto_repo.get_by_id(item.produto_id)
            if produto is None:
                raise NotFoundError(f"Produto {item.produto_id} não encontrado.")
            self.estoque_service.verificar_disponibilidade(
                dados.unidade_id, item.produto_id, item.quantidade
            )
            produtos_validados.append((item, produto))

        # 2ª passada: agora que todos os itens são válidos, debita o estoque
        # e monta as linhas do pedido.
        itens_para_persistir: list[ItemPedido] = []
        total = 0
        for item, produto in produtos_validados:
            estoque = self.estoque_service.verificar_disponibilidade(
                dados.unidade_id, item.produto_id, item.quantidade
            )
            self.estoque_service.debitar(estoque, item.quantidade)

            preco_unitario = produto.preco
            total += preco_unitario * item.quantidade
            itens_para_persistir.append(
                ItemPedido(
                    produto_id=item.produto_id,
                    quantidade=item.quantidade,
                    preco_unitario=preco_unitario,
                )
            )

        pedido = Pedido(
            unidade_id=dados.unidade_id,
            cliente_id=cliente_id,
            canal_pedido=dados.canal_pedido,  # RF09
            status=StatusPedidoEnum.AGUARDANDO_PAGAMENTO,
            total=total,
            itens=itens_para_persistir,
        )
        pedido = self.pedido_repo.create(pedido)

        self.log_repo.create(
            LogAuditoria(
                usuario_id=cliente_id,
                acao="CRIACAO_PEDIDO",
                entidade="Pedido",
                entidade_id=pedido.id,
                detalhes=f"canal={dados.canal_pedido.value}, total={total}",
            )
        )
        return pedido

    def obter_pedido(self, pedido_id: int) -> Pedido:
        pedido = self.pedido_repo.get_by_id(pedido_id)
        if pedido is None:
            raise NotFoundError(f"Pedido {pedido_id} não encontrado.")
        return pedido

    def listar_pedidos(self, canal_pedido: CanalPedidoEnum | None = None) -> list[Pedido]:
        """RF09 — filtro por canal via query param."""
        return self.pedido_repo.list(canal_pedido)

    def atualizar_status(self, pedido_id: int, novo_status: StatusPedidoEnum, usuario_id: int) -> Pedido:
        """RF04 + RN06 — só permite transições válidas."""
        pedido = self.obter_pedido(pedido_id)
        transicoes_permitidas = TRANSICOES_VALIDAS.get(pedido.status, set())
        if novo_status not in transicoes_permitidas:
            raise TransicaoStatusInvalidaError(
                f"Não é possível mudar de '{pedido.status.value}' para '{novo_status.value}'.",
                details=[
                    {
                        "field": "novo_status",
                        "issue": f"Transições válidas: {[s.value for s in transicoes_permitidas]}",
                    }
                ],
            )
        pedido.status = novo_status
        pedido = self.pedido_repo.save(pedido)

        # RNF02 — auditoria de mudança de status (ação sensível, inclui cancelamento)
        self.log_repo.create(
            LogAuditoria(
                usuario_id=usuario_id,
                acao="ATUALIZACAO_STATUS_PEDIDO",
                entidade="Pedido",
                entidade_id=pedido.id,
                detalhes=f"novo_status={novo_status.value}",
            )
        )
        return pedido

    def _forcar_status_interno(self, pedido: Pedido, novo_status: StatusPedidoEnum) -> Pedido:
        """
        [DECISÃO DE IMPLEMENTAÇÃO] usado apenas pelo PagamentoService, que
        precisa mover o pedido de AGUARDANDO_PAGAMENTO para EM_PREPARO ou
        PAGAMENTO_RECUSADO como efeito colateral direto do resultado do
        gateway mock (RN06/RN07), sem exigir uma segunda chamada de API.
        """
        pedido.status = novo_status
        return self.pedido_repo.save(pedido)
