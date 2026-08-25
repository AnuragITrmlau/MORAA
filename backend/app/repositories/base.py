"""Base repository implementing common CRUD operations."""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from sqlalchemy.orm import Session

from app.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository with standard database operations."""

    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def create(self, **kwargs) -> ModelType:
        """Create a new record."""
        obj = self.model(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get(self, id: str) -> Optional[ModelType]:
        """Get record by ID."""
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
        descending: bool = True,
    ) -> List[ModelType]:
        """Get all records with pagination."""
        query = self.db.query(self.model)
        if order_by:
            column = getattr(self.model, order_by, None)
            if column:
                query = query.order_by(column.desc() if descending else column)
        return query.offset(skip).limit(limit).all()

    def count(self, **filters) -> int:
        """Count records with optional filters."""
        query = self.db.query(self.model)
        for field, value in filters.items():
            if value is not None:
                column = getattr(self.model, field, None)
                if column is not None:
                    query = query.filter(column == value)
        return query.count()

    def update(self, id: str, **kwargs) -> Optional[ModelType]:
        """Update a record by ID."""
        obj = self.get(id)
        if not obj:
            return None
        for key, value in kwargs.items():
            if value is not None and hasattr(obj, key):
                setattr(obj, key, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, id: str) -> bool:
        """Delete a record by ID. Returns True if deleted, False if not found."""
        obj = self.get(id)
        if not obj:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True

    def find_by(self, **kwargs) -> List[ModelType]:
        """Find records by field values."""
        query = self.db.query(self.model)
        for field, value in kwargs.items():
            if value is not None:
                column = getattr(self.model, field, None)
                if column is not None:
                    query = query.filter(column == value)
        return query.all()

    def find_first(self, **kwargs) -> Optional[ModelType]:
        """Find first record matching filter."""
        query = self.db.query(self.model)
        for field, value in kwargs.items():
            if value is not None:
                column = getattr(self.model, field, None)
                if column is not None:
                    query = query.filter(column == value)
        return query.first()

    def bulk_create(self, items: List[Dict[str, Any]]) -> List[ModelType]:
        """Create multiple records at once."""
        objs = [self.model(**item) for item in items]
        self.db.add_all(objs)
        self.db.commit()
        for obj in objs:
            self.db.refresh(obj)
        return objs
