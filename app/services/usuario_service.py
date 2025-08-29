from __future__ import annotations
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.repositories.usuario_repo import UsuarioRepository
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate, UsuarioRead, UsuarioList
from app.models.usuario import Usuario


# ----------------- CRIPTOGRAFIA DE SENHA -----------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UsuarioService:
    """
    Camada de negócio para Usuários.
    Regras: hashing de senha, validações e transformação ORM → Schema.
    """

    def __init__(self, db: Session):
        """Inicializa o service com uma sessão ativa."""
        self.repo = UsuarioRepository(db)

    # ----------------- UTILITÁRIOS -----------------
    def _hash_password(self, senha: str) -> str:
        """Gera hash seguro (bcrypt) para a senha recebida."""
        return pwd_context.hash(senha)

    def _verify_password(self, senha: str, senha_hash: str) -> bool:
        """Compara senha pura com o hash armazenado no banco."""
        return pwd_context.verify(senha, senha_hash)

    # ----------------- CREATE -----------------
    def create_usuario(self, payload: UsuarioCreate) -> UsuarioRead:
        """
        Cria um novo usuário no sistema.
        - Recebe `UsuarioCreate` (senha pura).
        - Gera o hash da senha e salva no banco.
        - Retorna um `UsuarioRead` (sem senha).
        """
        data = payload.model_dump()
        senha_pura = data.pop("senha")
        data["senha_hash"] = self._hash_password(senha_pura)

        usuario = self.repo.create(data)
        return UsuarioRead.model_validate(usuario)

    # ----------------- READ -----------------
    def get_usuario(self, usuario_id: int) -> Optional[UsuarioRead]:
        """Busca um usuário por ID."""
        usuario = self.repo.get_by_id(usuario_id)
        return UsuarioRead.model_validate(usuario) if usuario else None

    def get_usuario_by_email(self, email: str) -> Optional[UsuarioRead]:
        """Busca usuário pelo e-mail (único)."""
        usuario = self.repo.get_by_email(email)
        return UsuarioRead.model_validate(usuario) if usuario else None

    def list_usuarios(
        self, limit: int = 50, offset: int = 0, ativo: Optional[bool] = None
    ) -> Tuple[List[UsuarioRead], int]:
        """
        Lista usuários com paginação.
        """
        items, total = self.repo.list(limit=limit, offset=offset, ativo=ativo)
        return [UsuarioRead.model_validate(i) for i in items], total

    def list_all_usuarios(self) -> List[UsuarioRead]:
        """Lista todos os usuários (sem paginação)."""
        items = self.repo.list_all()
        return [UsuarioRead.model_validate(i) for i in items]

    # ----------------- UPDATE -----------------
    def update_usuario(self, usuario_id: int, payload: UsuarioUpdate) -> Optional[UsuarioRead]:
        """
        Atualiza um usuário existente.
        - Se `senha` for enviada, gera novo hash antes de salvar.
        """
        data = payload.model_dump(exclude_unset=True)
        if "senha" in data:
            data["senha_hash"] = self._hash_password(data.pop("senha"))

        usuario = self.repo.update(usuario_id, data)
        return UsuarioRead.model_validate(usuario) if usuario else None

    # ----------------- DELETE -----------------
    def delete_usuario(self, usuario_id: int, hard: bool = False) -> bool:
        """
        Remove um usuário.
        - `hard=True` → deleta fisicamente.
        - `hard=False` → soft delete (ativo=False).
        """
        return self.repo.delete(usuario_id, hard=hard)

    # ----------------- AUTENTICAÇÃO -----------------
    def authenticate(self, email: str, senha: str) -> Optional[UsuarioRead]:
        """
        Autentica usuário:
        - Busca por email.
        - Verifica senha.
        - Retorna `UsuarioRead` se credenciais válidas.
        """
        usuario = self.repo.get_by_email(email)
        if not usuario:
            return None
        if not self._verify_password(senha, usuario.senha_hash):
            return None
        return UsuarioRead.model_validate(usuario)
