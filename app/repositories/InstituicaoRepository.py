"""
Repository Pattern para Instituição.

Este módulo implementa o padrão Repository para encapsular
todas as operações de banco de dados da entidade Instituição.
"""

from __future__ import annotations

from typing import Optional, Sequence, Generic, TypeVar, Type, Dict, Any
from datetime import datetime

from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.instituicao import Instituicao
from app.schemas.instituicao import InstituicaoCreate, InstituicaoUpdate

# === GENERIC REPOSITORY BASE ===
ModelType = TypeVar("ModelType")  # Tipo genérico para o modelo SQLAlchemy
CreateSchemaType = TypeVar("CreateSchemaType")  # Tipo para schema de criação
UpdateSchemaType = TypeVar("UpdateSchemaType")  # Tipo para schema de atualização


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Repository base genérico com operações CRUD padrão.

    Este repositório base pode ser reutilizado para outras entidades,
    fornecendo operações comuns como create, read, update, delete.

    Args:
        ModelType: Tipo do modelo SQLAlchemy (ex: Instituicao)
        CreateSchemaType: Schema Pydantic para criação (ex: InstituicaoCreate)
        UpdateSchemaType: Schema Pydantic para atualização (ex: InstituicaoUpdate)
    """

    def __init__(self, model: Type[ModelType]) -> None:
        """
        Inicializa o repositório com o modelo.

        Args:
            model: Classe do modelo SQLAlchemy
        """
        self.model = model

    async def create(
            self,
            session: AsyncSession,
            *,
            obj_in: CreateSchemaType
    ) -> ModelType:
        """
        Cria um novo registro no banco.

        Args:
            session: Sessão do SQLAlchemy
            obj_in: Dados para criação (schema Pydantic)

        Returns:
            ModelType: Objeto criado

        Raises:
            sqlalchemy.exc.IntegrityError: Se violar restrições de integridade
        """
        # Converte schema Pydantic para dict
        obj_data = obj_in.model_dump()

        # Cria instância do modelo SQLAlchemy
        db_obj = self.model(**obj_data)

        # Adiciona à sessão
        session.add(db_obj)

        # Força flush para obter ID sem commit final
        await session.flush()

        # Refresh para carregar campos automáticos (timestamps, etc.)
        await session.refresh(db_obj)

        return db_obj

    async def get_by_id(
            self,
            session: AsyncSession,
            *,
            id: int
    ) -> Optional[ModelType]:
        """
        Busca um registro por ID.

        Args:
            session: Sessão do SQLAlchemy
            id: ID do registro

        Returns:
            Optional[ModelType]: Objeto encontrado ou None
        """
        stmt = select(self.model).where(self.model.id == id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
            self,
            session: AsyncSession,
            *,
            skip: int = 0,
            limit: int = 100
    ) -> Sequence[ModelType]:
        """
        Lista todos os registros com paginação.

        Args:
            session: Sessão do SQLAlchemy
            skip: Número de registros para pular
            limit: Número máximo de registros para retornar

        Returns:
            Sequence[ModelType]: Lista de objetos
        """
        stmt = (
            select(self.model)
            .offset(skip)
            .limit(limit)
            .order_by(self.model.id)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def update(
            self,
            session: AsyncSession,
            *,
            db_obj: ModelType,
            obj_in: UpdateSchemaType | Dict[str, Any]
    ) -> ModelType:
        """
        Atualiza um registro existente.

        Args:
            session: Sessão do SQLAlchemy
            db_obj: Objeto existente do banco
            obj_in: Dados para atualização (schema ou dict)

        Returns:
            ModelType: Objeto atualizado
        """
        # Converte schema Pydantic para dict se necessário
        if hasattr(obj_in, 'model_dump'):
            obj_data = obj_in.model_dump(exclude_unset=True)
        else:
            obj_data = obj_in

        # Atualiza apenas campos fornecidos
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        # Força refresh para carregar campos automáticos
        await session.flush()
        await session.refresh(db_obj)

        return db_obj

    async def delete(
            self,
            session: AsyncSession,
            *,
            id: int
    ) -> Optional[ModelType]:
        """
        Remove um registro por ID.

        Args:
            session: Sessão do SQLAlchemy
            id: ID do registro para remover

        Returns:
            Optional[ModelType]: Objeto removido ou None se não encontrado
        """
        # Busca o objeto primeiro
        db_obj = await self.get_by_id(session, id=id)

        if db_obj:
            await session.delete(db_obj)
            await session.flush()

        return db_obj


# === REPOSITORY ESPECÍFICO DA INSTITUIÇÃO ===
class InstituicaoRepository(BaseRepository[Instituicao, InstituicaoCreate, InstituicaoUpdate]):
    """
    Repository específico para operações com Instituição.

    Herda operações básicas do BaseRepository e adiciona
    consultas específicas do domínio de Instituição.

    Operações disponíveis:
    - CRUD básico (herdado): create, get_by_id, get_all, update, delete
    - Específicas: get_by_codigo, get_by_cnpj, search, get_ativas, etc.
    """

    def __init__(self) -> None:
        """Inicializa o repository com o modelo Instituicao."""
        super().__init__(Instituicao)

    # === CONSULTAS ESPECÍFICAS POR CAMPOS ÚNICOS ===

    async def get_by_codigo(
            self,
            session: AsyncSession,
            *,
            codigo: str
    ) -> Optional[Instituicao]:
        """
        Busca instituição por código único.

        Args:
            session: Sessão do SQLAlchemy
            codigo: Código da instituição (ex: "UEPB")

        Returns:
            Optional[Instituicao]: Instituição encontrada ou None

        Example:
            >>> repo = InstituicaoRepository()
            >>> uepb = await repo.get_by_codigo(session, codigo="UEPB")
        """
        stmt = select(Instituicao).where(Instituicao.codigo == codigo.upper())
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_cnpj(
            self,
            session: AsyncSession,
            *,
            cnpj: str
    ) -> Optional[Instituicao]:
        """
        Busca instituição por CNPJ.

        Args:
            session: Sessão do SQLAlchemy
            cnpj: CNPJ da instituição (com ou sem formatação)

        Returns:
            Optional[Instituicao]: Instituição encontrada ou None

        Note:
            Remove automaticamente formatação do CNPJ antes da busca.
        """
        # Remove formatação do CNPJ
        cnpj_limpo = cnpj.replace(".", "").replace("/", "").replace("-", "")

        stmt = select(Instituicao).where(
            func.replace(
                func.replace(
                    func.replace(Instituicao.cnpj, ".", ""),
                    "/", ""
                ),
                "-", ""
            ) == cnpj_limpo
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    # === CONSULTAS DE BUSCA E FILTRO ===

    async def search(
            self,
            session: AsyncSession,
            *,
            termo: str,
            apenas_ativas: bool = True,
            skip: int = 0,
            limit: int = 20
    ) -> Sequence[Instituicao]:
        """
        Busca instituições por termo livre.

        Procura no código, nome completo, nome abreviado e sigla.

        Args:
            session: Sessão do SQLAlchemy
            termo: Termo para buscar
            apenas_ativas: Se deve filtrar apenas instituições ativas
            skip: Registros para pular (paginação)
            limit: Limite de registros

        Returns:
            Sequence[Instituicao]: Lista de instituições encontradas

        Example:
            >>> resultados = await repo.search(session, termo="paraiba")
        """
        # Prepara termo para busca (case-insensitive)
        termo_busca = f"%{termo.lower()}%"

        # Monta query com OR em múltiplos campos
        stmt = select(Instituicao).where(
            or_(
                func.lower(Instituicao.codigo).like(termo_busca),
                func.lower(Instituicao.nome_completo).like(termo_busca),
                func.lower(Instituicao.nome_abreviado).like(termo_busca),
                func.lower(Instituicao.sigla).like(termo_busca),
            )
        )

        # Filtro de ativas se solicitado
        if apenas_ativas:
            stmt = stmt.where(Instituicao.ativo == True)

        # Ordenação e paginação
        stmt = (
            stmt
            .order_by(Instituicao.nome_abreviado)
            .offset(skip)
            .limit(limit)
        )

        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_ativas(
            self,
            session: AsyncSession,
            *,
            skip: int = 0,
            limit: int = 100
    ) -> Sequence[Instituicao]:
        """
        Lista apenas instituições ativas.

        Args:
            session: Sessão do SQLAlchemy
            skip: Registros para pular
            limit: Limite de registros

        Returns:
            Sequence[Instituicao]: Lista de instituições ativas
        """
        stmt = (
            select(Instituicao)
            .where(Instituicao.ativo == True)
            .order_by(Instituicao.nome_abreviado)
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_por_tipo(
            self,
            session: AsyncSession,
            *,
            tipo: str
    ) -> Sequence[Instituicao]:
        """
        Lista instituições por tipo (Federal, Estadual, etc.).

        Args:
            session: Sessão do SQLAlchemy
            tipo: Tipo da instituição

        Returns:
            Sequence[Instituicao]: Lista de instituições do tipo especificado
        """
        stmt = (
            select(Instituicao)
            .where(
                and_(
                    Instituicao.tipo == tipo,
                    Instituicao.ativo == True
                )
            )
            .order_by(Instituicao.nome_abreviado)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    # === OPERAÇÕES DE CONTAGEM E ESTATÍSTICAS ===

    async def count_total(self, session: AsyncSession) -> int:
        """
        Conta o total de instituições.

        Args:
            session: Sessão do SQLAlchemy

        Returns:
            int: Número total de instituições
        """
        stmt = select(func.count(Instituicao.id))
        result = await session.execute(stmt)
        return result.scalar()

    async def count_ativas(self, session: AsyncSession) -> int:
        """
        Conta instituições ativas.

        Args:
            session: Sessão do SQLAlchemy

        Returns:
            int: Número de instituições ativas
        """
        stmt = select(func.count(Instituicao.id)).where(Instituicao.ativo == True)
        result = await session.execute(stmt)
        return result.scalar()

    async def get_estatisticas_por_tipo(self, session: AsyncSession) -> Dict[str, int]:
        """
        Retorna estatísticas de instituições agrupadas por tipo.

        Args:
            session: Sessão do SQLAlchemy

        Returns:
            Dict[str, int]: Dicionário com tipo -> quantidade

        Example:
            >>> stats = await repo.get_estatisticas_por_tipo(session)
            >>> print(stats)  # {"Federal": 10, "Estadual": 25, "Privada": 45}
        """
        stmt = (
            select(Instituicao.tipo, func.count(Instituicao.id))
            .where(Instituicao.ativo == True)
            .group_by(Instituicao.tipo)
            .order_by(Instituicao.tipo)
        )
        result = await session.execute(stmt)

        # Converte resultado em dicionário
        return {tipo: count for tipo, count in result.all()}

    # === OPERAÇÕES DE RELACIONAMENTO ===

    async def get_with_programas(
            self,
            session: AsyncSession,
            *,
            id: int
    ) -> Optional[Instituicao]:
        """
        Busca instituição com seus programas carregados.

        Args:
            session: Sessão do SQLAlchemy
            id: ID da instituição

        Returns:
            Optional[Instituicao]: Instituição com programas ou None

        Note:
            Será implementado quando tivermos o modelo Programa.
        """
        # TODO: Implementar quando criar modelo Programa
        # stmt = (
        #     select(Instituicao)
        #     .options(selectinload(Instituicao.programas))
        #     .where(Instituicao.id == id)
        # )
        # result = await session.execute(stmt)
        # return result.scalar_one_or_none()

        return await self.get_by_id(session, id=id)

    # === OPERAÇÕES DE VALIDAÇÃO ===

    async def exists_codigo(
            self,
            session: AsyncSession,
            *,
            codigo: str,
            exclude_id: Optional[int] = None
    ) -> bool:
        """
        Verifica se já existe instituição com o código.

        Args:
            session: Sessão do SQLAlchemy
            codigo: Código para verificar
            exclude_id: ID para excluir da verificação (útil em updates)

        Returns:
            bool: True se código já existe

        Example:
            >>> # Na criação
            >>> existe = await repo.exists_codigo(session, codigo="NOVA")
            >>>
            >>> # Na atualização (excluir o próprio registro)
            >>> existe = await repo.exists_codigo(session, codigo="UEPB", exclude_id=1)
        """
        stmt = select(func.count(Instituicao.id)).where(
            Instituicao.codigo == codigo.upper()
        )

        # Exclui ID específico se fornecido (útil para updates)
        if exclude_id:
            stmt = stmt.where(Instituicao.id != exclude_id)

        result = await session.execute(stmt)
        count = result.scalar()
        return count > 0

    async def exists_cnpj(
            self,
            session: AsyncSession,
            *,
            cnpj: str,
            exclude_id: Optional[int] = None
    ) -> bool:
        """
        Verifica se já existe instituição com o CNPJ.

        Args:
            session: Sessão do SQLAlchemy
            cnpj: CNPJ para verificar
            exclude_id: ID para excluir da verificação

        Returns:
            bool: True se CNPJ já existe
        """
        # Remove formatação
        cnpj_limpo = cnpj.replace(".", "").replace("/", "").replace("-", "")

        stmt = select(func.count(Instituicao.id)).where(
            func.replace(
                func.replace(
                    func.replace(Instituicao.cnpj, ".", ""),
                    "/", ""
                ),
                "-", ""
            ) == cnpj_limpo
        )

        if exclude_id:
            stmt = stmt.where(Instituicao.id != exclude_id)

        result = await session.execute(stmt)
        count = result.scalar()
        return count > 0


# === INSTÂNCIA GLOBAL DO REPOSITORY ===
# Singleton para reutilização em toda a aplicação
instituicao_repository = InstituicaoRepository()


# === DEPENDENCY PARA FASTAPI ===
def get_instituicao_repository() -> InstituicaoRepository:
    """
    Dependência do FastAPI para injetar o repository.

    Returns:
        InstituicaoRepository: Instância do repository

    Usage:
        @app.get("/instituicoes/")
        async def list_instituicoes(
            repo: InstituicaoRepository = Depends(get_instituicao_repository)
        ):
            return await repo.get_all(session)
    """
    return instituicao_repository