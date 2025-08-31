from __future__ import annotations
from sqlalchemy.orm import DeclarativeBase

# IMPORTANTE: importe todos os models aqui para registrá-los no registry.
# Não coloque dentro de funções; deixe no nível do módulo.

class Base(DeclarativeBase):
    """Classe base para todos os modelos ORM."""
    pass

# # fmt: off
# from app.models.instituicao import Instituicao     # noqa: F401
# from app.models.programa import Programa           # noqa: F401
# from app.models.usuario import Usuario             # noqa: F401
# from app.models.usuario_programa import UsuarioPrograma  # noqa: F401
# from app.models.role import Role
# # fmt: on