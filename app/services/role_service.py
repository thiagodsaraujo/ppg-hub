# app/services/role_service.py
from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
from app.models.role import Role
from app.schemas.role import RoleCreate, RoleUpdate

class RoleService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payload: RoleCreate) -> Role:
        obj = Role(**payload.model_dump())
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def list(self, limit: int = 50, offset: int = 0) -> Tuple[List[Role], int]:
        q = self.db.query(Role).offset(offset).limit(limit)
        items = q.all()
        total = self.db.query(Role).count()
        return items, total

    def get(self, role_id: int) -> Optional[Role]:
        return self.db.get(Role, role_id)

    def update(self, role_id: int, payload: RoleUpdate) -> Optional[Role]:
        obj = self.get(role_id)
        if not obj:
            return None
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(obj, field, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, role_id: int) -> bool:
        obj = self.get(role_id)
        if not obj:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True
