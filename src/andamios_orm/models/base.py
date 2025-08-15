"""
Base model classes for Andamios ORM

This module contains the base model class with Active Record pattern for simple usage.
"""

from typing import Optional, Any, Dict, ClassVar, Type, List
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession

from ..core import get_session


Base = declarative_base()


class Model(Base):
    """Active Record base model for simple ORM usage.
    
    Provides simple methods like save(), delete(), get() that hide
    all SQLAlchemy complexity from the client.
    """
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    async def save(self) -> "Model":
        """Save this model instance to the database."""
        session = await get_session()
        try:
            session.add(self)
            await session.commit()
            await session.refresh(self)
            return self
        finally:
            await session.close()
    
    async def delete(self) -> None:
        """Delete this model instance from the database."""
        session = await get_session()
        try:
            await session.delete(self)
            await session.commit()
        finally:
            await session.close()
    
    @classmethod
    async def get(cls, id: int) -> Optional["Model"]:
        """Get a model instance by ID."""
        session = await get_session()
        try:
            return await session.get(cls, id)
        finally:
            await session.close()
    
    @classmethod
    async def get_all(cls) -> List["Model"]:
        """Get all instances of this model."""
        from sqlalchemy import select
        session = await get_session()
        try:
            result = await session.execute(select(cls))
            return result.scalars().all()
        finally:
            await session.close()
    
    @classmethod
    async def create(cls, **kwargs: Any) -> "Model":
        """Create and save a new model instance."""
        instance = cls(**kwargs)
        return await instance.save()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}