"""베이스 리포지토리 - 공통 CRUD 작업"""
from typing import Generic, TypeVar, Type, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

ModelType = TypeVar("ModelType")

class BaseRepository(Generic[ModelType]):
    """
    기본 CRUD 작업을 제공하는 베이스 리포지토리
    """
    
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db
    
    def get_by_id(self, id: int) -> Optional[ModelType]:
        """ID로 단일 레코드 조회"""
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """모든 레코드 조회 (페이지네이션)"""
        return self.db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, obj: ModelType) -> ModelType:
        """새 레코드 생성"""
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    def update(self, obj: ModelType) -> ModelType:
        """레코드 업데이트"""
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    def delete(self, id: int) -> bool:
        """레코드 삭제"""
        obj = self.get_by_id(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False
    
    def bulk_insert(self, objects: List[ModelType]) -> int:
        """대량 삽입"""
        self.db.bulk_save_objects(objects)
        self.db.commit()
        return len(objects)
    
    def count(self) -> int:
        """전체 레코드 수"""
        return self.db.query(self.model).count()
