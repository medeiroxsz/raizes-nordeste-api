# Raízes do Nordeste API — Trilha Back-End

API de referência em **Python + FastAPI** para o estudo de caso *Rede "Raízes do Nordeste"*
(UNINTER, Projeto Multidisciplinar — Trilha Back-End, 2026).

> Este projeto é uma **implementação de referência técnica**, não um gabarito para entrega
> direta. Consulte `ANALISE_TECNICA.md` para o mapeamento completo entre os requisitos do
> PDF (RF/RNF/RN) e cada parte do código — a rastreabilidade também aparece em docstrings e
> nas descrições dos endpoints no Swagger.

---

## 1. Objetivo

Dar suporte de back-end à operação de uma rede de lanchonetes com múltiplos canais de
atendimento (App, Totem, Balcão, Pickup, Web), padronizando pedidos, estoque por unidade e
fidelização de clientes, com pagamento desacoplado de um provedor externo (mock).

## 2. Tecnologias

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.12 |
| Framework web | FastAPI |
| Validação/contratos | Pydantic v2 (com `pydantic-settings`) |
| ORM / Banco | SQLAlchemy 2.0 + SQLite (ver seção 6) |
| Autenticação | JWT (`python-jose`) |
| Hash de senha | `passlib[bcrypt]` |
| Testes | `pytest` + `httpx`/`TestClient` |
| Documentação | OpenAPI/Swagger (gerado automaticamente pelo FastAPI) |

## 3. Arquitetura

Organização em camadas (Domain / Application / Infrastructure / API), conforme exigido no
roteiro da trilha Back-End:

```
app/
├── main.py                # bootstrap FastAPI, inclui routers e exception handlers
├── core/
│   ├── config.py          # configurações via variáveis de ambiente
│   └── security.py        # hash de senha, JWT, autenticação/autorização por perfil
├── database/
│   └── connection.py      # engine/session SQLAlchemy
├── models/                # Domain — entidades SQLAlchemy (Usuario, Pedido, Estoque...)
├── schemas/                # Contratos Pydantic (request/response), camelCase na borda HTTP
├── repositories/          # Infrastructure — acesso a dados, sem regra de negócio
├── services/              # Application — regras de negócio (RN01–RN12)
├── routers/                # API — endpoints FastAPI, autenticação/autorização, docs
├── exceptions/            # Exceções de domínio + handlers HTTP padronizados
└── tests/                  # pytest, organizados por requisito funcional
```

**Por que essa estrutura:** `models` conhece apenas o banco; `services` conhece regra de
negócio e orquestra `repositories`; `routers` só traduz HTTP ↔ Service. Isso permite testar
regra de negócio sem subir a API (ver `test_auditoria.py`) e trocar o banco sem tocar em
`services`/`routers`.

**Decisão de nomenclatura (importante):** internamente o código Python segue `snake_case`
(PEP 8), mas todo contrato JSON exposto pela API usa `camelCase` (`canalPedido`, `produtoId`,
`clienteId` etc.) através de um `alias_generator` em `app/schemas/base.py::CamelModel` — isso
atende à exigência literal do PDF (seção 5.5: *"inclua explicitamente o campo canalPedido"*).
A API aceita tanto `camelCase` quanto `snake_case` na entrada (`populate_by_name=True`), mas
sempre **responde em camelCase**.

## 4. Requisitos para rodar

- Python 3.11+ (testado com 3.12)
- pip

## 5. Instalação

```bash
# 1. Clonar/entrar no diretório do projeto
cd raizes-nordeste-api

# 2. Criar e ativar um ambiente virtual
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Instalar as dependências
pip install -r requirements.txt
```

> **Nota sobre `passlib`/`bcrypt`:** o `requirements.txt` fixa `bcrypt==4.0.1` porque
> `passlib==1.7.4` tem uma incompatibilidade conhecida com `bcrypt>=4.1` (erro ao ler
> `__about__.__version__` do backend). Se você atualizar uma das duas libs, atualize a outra
> também.

## 6. Configuração (variáveis de ambiente)

Copie o arquivo de exemplo e ajuste se necessário:

```bash
cp .env.example .env
```

| Variável | Descrição | Padrão |
|---|---|---|
| `DATABASE_URL` | String de conexão SQLAlchemy | `sqlite:///./raizes_nordeste.db` |
| `JWT_SECRET_KEY` | Chave usada para assinar o JWT — **troque em produção** | — |
| `JWT_ALGORITHM` | Algoritmo do JWT | `HS256` |
| `JWT_EXPIRE_MINUTES` | Expiração do token, em minutos | `60` |
| `APP_NAME` / `APP_VERSION` | Metadados exibidos no Swagger | — |

## 7. Banco de dados

**[DECISÃO DE IMPLEMENTAÇÃO]** O PDF não exige um SGBD específico, então usamos **SQLite**
para permitir execução local sem dependências externas. As tabelas são criadas
automaticamente na inicialização via `Base.metadata.create_all()` (`app/database/connection.py`).

Para trocar de banco (ex.: PostgreSQL), basta alterar `DATABASE_URL` no `.env` — nenhum
código de `models`/`repositories` precisa mudar, pois tudo é feito via SQLAlchemy ORM.

> Migrations versionadas (Alembic) não foram incluídas no MVP — ver `ANALISE_TECNICA.md`,
> seção 22 (RECOMENDADO/OPCIONAL), para o caminho de evolução.

## 8. Execução

```bash
uvicorn app.main:app --reload
```

A API sobe em `http://127.0.0.1:8000`. Endpoint de verificação de saúde: `GET /health`.

## 9. Documentação interativa (Swagger/OpenAPI)

- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc
- **JSON OpenAPI cru:** http://127.0.0.1:8000/openapi.json

Todos os endpoints têm `summary`, `description` (com o requisito do PDF associado, ex. RF03,
RN05) e os `responses` possíveis documentados diretamente no código dos routers.

## 10. Autenticação

1. Cadastre um usuário: `POST /usuarios` (campo `perfil`: `CLIENTE`, `ATENDENTE`, `COZINHA`,
   `GERENTE` ou `ADMIN`).
2. Faça login: `POST /auth/login` → retorna `access_token` (JWT Bearer).
3. Envie o token nas próximas requisições: header `Authorization: Bearer <token>`.

Autorização por perfil é feita via dependência `require_roles(...)` em cada endpoint
protegido (ex.: só `GERENTE`/`ADMIN` podem movimentar estoque).

## 11. Endpoints principais

| Método | Rota | Requisito | Autenticação |
|---|---|---|---|
| POST | `/usuarios` | RF01 | Pública |
| POST | `/auth/login` | RF01 | Pública |
| GET | `/unidades` | RF02 | Pública |
| GET | `/unidades/{id}/produtos` | RF02 / RN03 | Pública |
| POST | `/estoque/movimentacoes` | RF05 / RN08 | GERENTE/ADMIN |
| POST | `/pedidos` | RF03 / RF09 / RN04 / RN05 | CLIENTE/ATENDENTE/ADMIN |
| GET | `/pedidos?canalPedido=` | RF09 | Autenticado |
| PATCH | `/pedidos/{id}/status` | RF04 / RN06 | COZINHA/GERENTE/ADMIN |
| POST | `/pagamentos/{pedidoId}/simular` | RF08 / RN06 / RN07 / RN12 | Autenticado |
| GET | `/fidelidade/{clienteId}` | RF06 | Próprio cliente/GERENTE |
| POST | `/fidelidade/resgate` | RF06 / RN10 | CLIENTE |

Lista completa, exemplos de request/response e a matriz de rastreabilidade estão em
`ANALISE_TECNICA.md`, seções 12 e 13.

## 12. Testes

```bash
pytest app/tests -v
```

Os testes usam um banco SQLite **em memória**, isolado por teste (não tocam no arquivo
`raizes_nordeste.db`). Organização por requisito:

| Arquivo | Cobre |
|---|---|
| `test_usuarios.py` | RF01, autenticação/autorização (401/403) |
| `test_catalogo.py` | RF02, RN03 |
| `test_estoque.py` | RF05, RN08 |
| `test_pedidos.py` | RF03, RF04, RF09, RN04, RN05, RN06 |
| `test_pagamentos.py` | RF08, RN06, RN07 |
| `test_fidelidade.py` | RF06, RN09, RN10 |
| `test_auditoria.py` | RNF02 (log de ações sensíveis) |

> **Importante — ambiente de geração deste projeto:** este código foi escrito e revisado
> (incluindo compilação de todos os arquivos com `python3 -m py_compile`, sem erros de
> sintaxe, e revisão manual de cada regra de negócio) em um sandbox **sem acesso à
> internet**, o que impediu `pip install`/`pytest` de serem executados nesta máquina antes
> da entrega. **Rode `pip install -r requirements.txt && pytest app/tests -v` no seu
> ambiente local antes de considerar o projeto validado.** Se algum teste falhar, o mais
> provável é uma diferença de versão de dependência — os números de versão em
> `requirements.txt` refletem combinações conhecidas por serem compatíveis (FastAPI
> 0.115 + Pydantic 2.9 + SQLAlchemy 2.0), mas não foram confirmados nesta máquina.

## 13. Decisões técnicas e limitações

Ver `ANALISE_TECNICA.md`:
- Seção 20 (Conclusão) — decisões arquiteturais e limitações conhecidas.
- Seção 21 (Checklist) — o que está implementado vs. fora do MVP (ex.: aplicação automática
  de promoções, RF07, foi modelada mas não implementada).
- Seção 22 (Otimização) — melhorias recomendadas (concorrência no débito de estoque,
  paginação completa, Alembic, cache, fila assíncrona para pagamento) separadas em
  OBRIGATÓRIO / RECOMENDADO / OPCIONAL.

## 14. Estrutura completa de pastas

```
raizes-nordeste-api/
├── ANALISE_TECNICA.md
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
└── app/
    ├── main.py
    ├── core/
    │   ├── config.py
    │   └── security.py
    ├── database/
    │   └── connection.py
    ├── models/
    │   ├── enums.py
    │   ├── usuario.py
    │   ├── unidade.py
    │   ├── produto.py
    │   ├── estoque.py
    │   ├── pedido.py
    │   ├── item_pedido.py
    │   ├── pagamento.py
    │   ├── fidelidade.py
    │   └── log_auditoria.py
    ├── schemas/
    │   ├── base.py
    │   ├── common.py
    │   ├── usuario.py
    │   ├── unidade.py
    │   ├── estoque.py
    │   ├── pedido.py
    │   ├── pagamento.py
    │   └── fidelidade.py
    ├── repositories/
    │   ├── usuario_repository.py
    │   ├── catalogo_repository.py
    │   ├── pedido_repository.py
    │   ├── pagamento_repository.py
    │   └── fidelidade_repository.py
    ├── services/
    │   ├── usuario_service.py
    │   ├── catalogo_service.py
    │   ├── estoque_service.py
    │   ├── pedido_service.py
    │   ├── pagamento_mock.py
    │   ├── pagamento_service.py
    │   └── fidelidade_service.py
    ├── routers/
    │   ├── auth.py
    │   ├── catalogo.py
    │   ├── estoque.py
    │   ├── pedidos.py
    │   ├── pagamentos.py
    │   └── fidelidade.py
    ├── exceptions/
    │   ├── custom_exceptions.py
    │   └── handlers.py
    └── tests/
        ├── conftest.py
        ├── test_usuarios.py
        ├── test_catalogo.py
        ├── test_estoque.py
        ├── test_pedidos.py
        ├── test_pagamentos.py
        ├── test_fidelidade.py
        └── test_auditoria.py
```
