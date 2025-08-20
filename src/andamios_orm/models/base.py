"""
Base model classes for Andamios ORM

This module contains the base model class with Active Record pattern for simple usage.
"""

import asyncio
from typing import Optional, Any, Dict, ClassVar, Type, List
from sqlalchemy import Column, Integer, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from ..core import get_session
from ..exceptions import DatabaseOperationError, NotFoundError, ValidationError
from ..logging import get_logger


Base = declarative_base()

logger = get_logger("models")


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
        logger.debug(f"Creating {cls.__name__} with data: {kwargs}")
        session = await get_session()
        try:
            # Validate required fields
            if hasattr(cls, '_validate_create'):
                cls._validate_create(**kwargs)
            
            # Generate ID if not provided
            if 'id' not in kwargs:
                try:
                    # Simple ID generation for DuckDB compatibility
                    result = await asyncio.to_thread(
                        session._session.execute,
                        text(f"SELECT COALESCE(MAX(id), 0) + 1 FROM {cls.__tablename__}")
                    )
                    next_id = await asyncio.to_thread(result.scalar)
                    kwargs['id'] = next_id
                    logger.debug(f"Generated ID {next_id} for {cls.__name__}")
                except SQLAlchemyError as e:
                    logger.error(f"Failed to generate ID for {cls.__name__}: {e}")
                    raise DatabaseOperationError(f"Failed to generate ID: {e}")
            
            try:
                instance = cls(**kwargs)
                await session.add(instance)
                await session.commit()
                await session.refresh(instance)
                logger.info(f"Created {cls.__name__} with ID {instance.id}")
                return instance
            except SQLAlchemyError as e:
                logger.error(f"Failed to create {cls.__name__}: {e}")
                await session.rollback()
                raise DatabaseOperationError(f"Failed to create {cls.__name__}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error creating {cls.__name__}: {e}")
            raise
        finally:
            await session.close()
    
    @classmethod
    async def read(cls, id: int) -> Optional["Model"]:
        """Read a model instance by ID."""
        logger.debug(f"Reading {cls.__name__} with ID {id}")
        session = await get_session()
        try:
            try:
                instance = await session.get(cls, id)
                if instance:
                    logger.debug(f"Found {cls.__name__} with ID {id}")
                else:
                    logger.debug(f"{cls.__name__} with ID {id} not found")
                return instance
            except SQLAlchemyError as e:
                logger.error(f"Failed to read {cls.__name__} with ID {id}: {e}")
                raise DatabaseOperationError(f"Failed to read {cls.__name__}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error reading {cls.__name__}: {e}")
            raise
        finally:
            await session.close()
    
    @classmethod
    async def update(cls, id: int, **kwargs: Any) -> Optional["Model"]:
        """Update a model instance by ID."""
        logger.debug(f"Updating {cls.__name__} with ID {id}, data: {kwargs}")
        session = await get_session()
        try:
            try:
                instance = await session.get(cls, id)
                if not instance:
                    logger.warning(f"{cls.__name__} with ID {id} not found for update")
                    return None
                
                # Validate update fields
                if hasattr(cls, '_validate_update'):
                    cls._validate_update(**kwargs)
                
                for key, value in kwargs.items():
                    if hasattr(instance, key):
                        setattr(instance, key, value)
                    else:
                        logger.warning(f"Attribute {key} not found on {cls.__name__}")
                
                await session.commit()
                await session.refresh(instance)
                logger.info(f"Updated {cls.__name__} with ID {id}")
                return instance
                
            except SQLAlchemyError as e:
                logger.error(f"Failed to update {cls.__name__} with ID {id}: {e}")
                await session.rollback()
                raise DatabaseOperationError(f"Failed to update {cls.__name__}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error updating {cls.__name__}: {e}")
            raise
        finally:
            await session.close()
    
    @classmethod
    async def delete(cls, id: int) -> bool:
        """Delete a model instance by ID."""
        logger.debug(f"Deleting {cls.__name__} with ID {id}")
        session = await get_session()
        try:
            try:
                instance = await session.get(cls, id)
                if not instance:
                    logger.warning(f"{cls.__name__} with ID {id} not found for deletion")
                    return False
                
                await session.delete(instance)
                await session.commit()
                logger.info(f"Deleted {cls.__name__} with ID {id}")
                return True
                
            except SQLAlchemyError as e:
                logger.error(f"Failed to delete {cls.__name__} with ID {id}: {e}")
                await session.rollback()
                raise DatabaseOperationError(f"Failed to delete {cls.__name__}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error deleting {cls.__name__}: {e}")
            raise
        finally:
            await session.close()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}