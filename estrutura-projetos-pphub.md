ppg-hub/
│
├─ app/
│  ├─ main.py                       # instancia FastAPI e inclui routers
│  ├─ deps.py                       # Depends compartilhados (ex.: get_db, get_current_user)
│  │
│  ├─ core/                         # núcleo técnico da aplicação
│  │  ├─ config.py                  # Settings (pydantic-settings)
│  │  ├─ db.py                      # engine, SessionLocal, Base, init_db()
│  │  ├─ security.py                # JWT, hash de senhas, RBAC
│  │  └─ logging.py                 # logger JSON e middleware de request_id
│  │
│  ├─ models/                       # entidades ORM (SQLAlchemy)
│  │  ├─ instituicao.py
│  │  ├─ programa.py
│  │  ├─ docente.py
│  │  ├─ discente.py
│  │  └─ ...
│  │
│  ├─ schemas/                      # contratos Pydantic (entrada/saída)
│  │  ├─ instituicao.py
│  │  ├─ programa.py
│  │  ├─ docente.py
│  │  ├─ discente.py
│  │  └─ ...
│  │
│  ├─ repositories/                 # acesso a dados (consultas SQLAlchemy)
│  │  ├─ instituicao_repo.py
│  │  ├─ programa_repo.py
│  │  └─ ...
│  │
│  ├─ services/                     # regras de negócio / orquestração
│  │  ├─ instituicao_service.py
│  │  ├─ programa_service.py
│  │  └─ ...
│  │
│  └─ routers/                      # endpoints FastAPI
│     ├─ instituicoes.py
│     ├─ programas.py
│     └─ auth.py
│
├─ tests/                           # testes unitários e integração
│  ├─ conftest.py                   # fixtures (TestClient, db em memória)
│  ├─ test_instituicoes.py
│  ├─ test_programas.py
│  └─ ...
│
├─ scripts/
│  └─ init_db.py                    # roda Base.metadata.create_all() no MVP
│
├─ docs/                            # documentação de apoio
│  ├─ overview.md                   # visão geral do projeto
│  ├─ api.md                        # descrição dos endpoints
│  └─ db-schema.md                  # entidades principais
│
├─ .env.example                     # template variáveis de ambiente
├─ pyproject.toml                   # ruff/black/mypy/pytest config (ou requirements.txt)
├─ README.md
└─ docker-compose.yml               # opcional: subir Postgres, Redis, n8n
