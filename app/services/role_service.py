from __future__ import annotations
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session

from app.repositories.role_repo import RoleRepository
from app.schemas.role import RoleCreate, RoleUpdate, RoleOut

class RoleService:
    """
    Camada de serviço responsável pela orquestração de regras de negócio
    relacionadas a papéis (roles) no sistema de autenticação/autorização (RBAC).

    🔹 Funções principais:
        - Validar e repassar dados da API para o repositório.
        - Garantir que os objetos retornados estejam no formato dos schemas Pydantic.
        - Manter a lógica de negócio centralizada, sem poluir os repositórios nem os endpoints.
    """

    def __init__(self, db: Session):
        """
        Inicializa o serviço recebendo uma sessão do SQLAlchemy.

        Args:
            db (Session): Sessão ativa de banco de dados.
        """
        self.repo = RoleRepository(db)

    # ----------------- CREATE -----------------
    def create_role(self, payload: RoleCreate) -> RoleOut:
        """
        Cria uma nova role no sistema.

        Args:
            payload (RoleCreate): Dados de entrada validados pelo schema.

        Returns:
            RoleOut: Representação da Role criada (com ID).
        """
        role = self.repo.create(payload.model_dump())  # cria via repositório
        return RoleOut.model_validate(role)  # converte ORM -> schema de saída

    # ----------------- READ -------------------
    def get_role(self, role_id: int) -> Optional[RoleOut]:
        """
        Recupera uma role pelo seu ID.

        Args:
            role_id (int): Identificador único da role.

        Returns:
            Optional[RoleOut]: Role encontrada ou None se não existir.
        """
        role = self.repo.get_by_id(role_id)
        return RoleOut.model_validate(role) if role else None

    def get_role_by_nome(self, nome: str) -> Optional[RoleOut]:
        """
        Recupera uma role pelo seu nome (único no sistema).

        Args:
            nome (str): Nome da role.

        Returns:
            Optional[RoleOut]: Role encontrada ou None se não existir.
        """
        role = self.repo.get_by_nome(nome)
        return RoleOut.model_validate(role) if role else None

    def list_roles(
        self,
        limit: int = 50,
        offset: int = 0,
        search: Optional[str] = None,
        ativo: Optional[bool] = None,
    ) -> Tuple[List[RoleOut], int]:
        """
        Lista roles de forma paginada com filtros opcionais.

        Args:
            limit (int): Número máximo de registros por página.
            offset (int): Deslocamento inicial (para paginação).
            search (Optional[str]): Texto para buscar no nome da role.
            ativo (Optional[bool]): Se definido, filtra roles ativas/inativas.

        Returns:
            Tuple[List[RoleOut], int]: Lista de roles + total de registros.
        """
        items, total = self.repo.list(limit=limit, offset=offset, search=search, ativo=ativo)
        return [RoleOut.model_validate(i) for i in items], total

    def list_all_roles(self) -> List[RoleOut]:
        """
        Retorna todas as roles do sistema, sem paginação.

        Returns:
            List[RoleOut]: Lista de todas as roles existentes.
        """
        items = self.repo.list_all()
        return [RoleOut.model_validate(i) for i in items]

    # ----------------- UPDATE -----------------
    def update_role(self, role_id: int, payload: RoleUpdate) -> RoleOut:
        """
        Atualiza parcialmente uma role existente.

        Args:
            role_id (int): Identificador único da role a ser atualizada.
            payload (RoleUpdate): Campos opcionais que podem ser alterados.

        Returns:
            RoleOut: Role atualizada.
        """
        role = self.repo.update(role_id, payload.model_dump(exclude_unset=True))
        return RoleOut.model_validate(role)

    # ----------------- DELETE -----------------
    def delete_role(self, role_id: int, hard: bool = False) -> None:
        """
        Remove uma role do sistema.

        Args:
            role_id (int): Identificador único da role.
            hard (bool): Se True, exclui definitivamente do banco (DELETE).
                         Se False, apenas marca como inativa (soft delete).

        Returns:
            None
        """
        self.repo.delete(role_id, hard=hard)
