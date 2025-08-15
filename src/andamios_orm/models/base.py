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
    Note: Models should define their own id, created_at, updated_at fields to match legacy schema exactly.
    """
    __abstract__ = True
    
    @classmethod
    async def create(cls, **kwargs: Any) -> "Model":
        """Create and persist a new model instance."""
        session = await get_session()
        try:
            instance = cls(**kwargs)
            session.add(instance)
            await session.commit()
            await session.refresh(instance)
            return instance
        finally:
            await session.close()
    
    @classmethod
    async def read(cls, id: int) -> Optional["Model"]:
        """Read a model instance by ID."""
        session = await get_session()
        try:
            return await session.get(cls, id)
        finally:
            await session.close()
    
    @classmethod
    async def update(cls, id: int, **kwargs: Any) -> Optional["Model"]:
        """Update a model instance by ID."""
        session = await get_session()
        try:
            instance = await session.get(cls, id)
            if instance:
                for key, value in kwargs.items():
                    setattr(instance, key, value)
                await session.commit()
                await session.refresh(instance)
            return instance
        finally:
            await session.close()
    
    @classmethod
    async def delete(cls, id: int) -> bool:
        """Delete a model instance by ID."""
        session = await get_session()
        try:
            instance = await session.get(cls, id)
            if instance:
                await session.delete(instance)
                await session.commit()
                return True
            return False
        finally:
            await session.close()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}