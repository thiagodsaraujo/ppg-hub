from sqlalchemy.orm import Session
from app.repositories.instituicao_repo import InstituicaoRepository


class InstituicaoService:

    def __init__(self, db: Session):
        self.repo = InstituicaoRepository(db)

    def create(self, data: dict):
        return self.repo.create(data)

    def list(self, limit: int, offset: int):
        return self.repo.list(limit, offset)

    def get(self, instituicao_id: int):
        return self.repo.get(instituicao_id)

    def update(self, instituicao_id: int, data: dict):
        return self.repo.update(instituicao_id, data)

    def delete(self, instituicao_id: int):
        return self.repo.delete(instituicao_id)
