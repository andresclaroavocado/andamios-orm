"""
Unit tests for models module
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from sqlalchemy import Column, Integer, String, Text, select, func
from sqlalchemy.exc import SQLAlchemyError

from src.andamios_orm.models.base import Model, Base
from src.andamios_orm.models.project import Project
from src.andamios_orm.models.conversation import Conversation
from src.andamios_orm.models.document import Document
from src.andamios_orm.models.repository import Repository
from src.andamios_orm.exceptions import (
    DatabaseOperationError, 
    NotFoundError, 
    ValidationError
)


class TestModel:
    """Test Model base class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create a test model class
        class TestModelClass(Model):
            __tablename__ = "test_table"
            id = Column(Integer, primary_key=True)
            name = Column(String(255), nullable=False)
        
        self.TestModelClass = TestModelClass
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.models.base.get_session')
    async def test_create_success(self, mock_get_session):
        """Test successful model creation."""
        mock_session = AsyncMock()
        mock_session.add = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        mock_session.close = AsyncMock()
        mock_get_session.return_value = mock_session
        
        # Mock ID generation
        mock_result = Mock()
        mock_result.scalar = Mock(return_value=1)
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.side_effect = [mock_result, 1]  # First for execute, second for scalar
            
            instance = await self.TestModelClass.create(name="Test Name")
            
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once()
            mock_session.close.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.models.base.get_session')
    async def test_create_with_provided_id(self, mock_get_session):
        """Test model creation with provided ID."""
        mock_session = AsyncMock()
        mock_session.add = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        mock_session.close = AsyncMock()
        mock_get_session.return_value = mock_session
        
        instance = await self.TestModelClass.create(id=5, name="Test Name")
        
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()
        mock_session.close.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.models.base.get_session')
    async def test_create_with_validation(self, mock_get_session):
        """Test model creation with validation method."""
        mock_session = AsyncMock()
        mock_get_session.return_value = mock_session
        
        # Add validation method to test class
        self.TestModelClass._validate_create = Mock()
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_result = Mock()
            mock_result.scalar = Mock(return_value=1)
            mock_to_thread.side_effect = [mock_result, 1]
            
            await self.TestModelClass.create(name="Test Name")
            
            self.TestModelClass._validate_create.assert_called_once_with(name="Test Name")
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.models.base.get_session')
    async def test_create_id_generation_error(self, mock_get_session):
        """Test model creation with ID generation error."""
        mock_session = AsyncMock()
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()
        mock_get_session.return_value = mock_session
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.side_effect = SQLAlchemyError("ID generation failed")
            
            with pytest.raises(DatabaseOperationError, match="Failed to generate ID"):
                await self.TestModelClass.create(name="Test Name")
            
            mock_session.close.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.models.base.get_session')
    async def test_create_commit_error(self, mock_get_session):
        """Test model creation with commit error."""
        mock_session = AsyncMock()
        mock_session.add = AsyncMock()
        mock_session.commit = AsyncMock(side_effect=SQLAlchemyError("Commit failed"))
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()
        mock_get_session.return_value = mock_session
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_result = Mock()
            mock_result.scalar = Mock(return_value=1)
            mock_to_thread.side_effect = [mock_result, 1]
            
            with pytest.raises(DatabaseOperationError, match="Failed to create"):
                await self.TestModelClass.create(name="Test Name")
            
            mock_session.rollback.assert_called_once()
            mock_session.close.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.models.base.get_session')
    async def test_read_success(self, mock_get_session):
        """Test successful model reading."""
        mock_session = AsyncMock()
        mock_instance = Mock()
        mock_session.get = AsyncMock(return_value=mock_instance)
        mock_session.close = AsyncMock()
        mock_get_session.return_value = mock_session
        
        result = await self.TestModelClass.read(1)
        
        mock_session.get.assert_called_once_with(self.TestModelClass, 1)
        mock_session.close.assert_called_once()
        assert result == mock_instance
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.models.base.get_session')
    async def test_read_not_found(self, mock_get_session):
        """Test model reading when not found."""
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=None)
        mock_session.close = AsyncMock()
        mock_get_session.return_value = mock_session
        
        result = await self.TestModelClass.read(999)
        
        mock_session.get.assert_called_once_with(self.TestModelClass, 999)
        mock_session.close.assert_called_once()
        assert result is None
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.models.base.get_session')
    async def test_read_error(self, mock_get_session):
        """Test model reading with error."""
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(side_effect=SQLAlchemyError("Read failed"))
        mock_session.close = AsyncMock()
        mock_get_session.return_value = mock_session
        
        with pytest.raises(DatabaseOperationError, match="Failed to read"):
            await self.TestModelClass.read(1)
        
        mock_session.close.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.models.base.get_session')
    async def test_update_success(self, mock_get_session):
        """Test successful model update."""
        mock_session = AsyncMock()
        mock_instance = Mock()
        mock_instance.name = "Old Name"
        mock_session.get = AsyncMock(return_value=mock_instance)
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        mock_session.close = AsyncMock()
        mock_get_session.return_value = mock_session
        
        result = await self.TestModelClass.update(1, name="New Name")
        
        mock_session.get.assert_called_once_with(self.TestModelClass, 1)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()
        mock_session.close.assert_called_once()
        assert mock_instance.name == "New Name"
        assert result == mock_instance
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.models.base.get_session')
    async def test_update_not_found(self, mock_get_session):
        """Test model update when instance not found."""
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=None)
        mock_session.close = AsyncMock()
        mock_get_session.return_value = mock_session
        
        result = await self.TestModelClass.update(999, name="New Name")
        
        mock_session.get.assert_called_once_with(self.TestModelClass, 999)
        mock_session.close.assert_called_once()
        assert result is None
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.models.base.get_session')
    async def test_update_with_validation(self, mock_get_session):
        """Test model update with validation method."""
        mock_session = AsyncMock()
        mock_instance = Mock()
        mock_session.get = AsyncMock(return_value=mock_instance)
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        mock_session.close = AsyncMock()
        mock_get_session.return_value = mock_session
        
        # Add validation method to test class
        self.TestModelClass._validate_update = Mock()
        
        await self.TestModelClass.update(1, name="New Name")
        
        self.TestModelClass._validate_update.assert_called_once_with(name="New Name")
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.models.base.get_session')
    async def test_update_invalid_attribute(self, mock_get_session):
        """Test model update with invalid attribute."""
        mock_session = AsyncMock()
        mock_instance = Mock()
        mock_instance.name = "Old Name"
        # Remove hasattr for invalid_field
        def custom_hasattr(obj, attr):
            return attr == "name"
        
        mock_session.get = AsyncMock(return_value=mock_instance)
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        mock_session.close = AsyncMock()
        mock_get_session.return_value = mock_session
        
        with patch('builtins.hasattr', side_effect=custom_hasattr):
            result = await self.TestModelClass.update(1, name="New Name", invalid_field="value")
            
            assert mock_instance.name == "New Name"
            assert not hasattr(mock_instance, "invalid_field")
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.models.base.get_session')
    async def test_update_commit_error(self, mock_get_session):
        """Test model update with commit error."""
        mock_session = AsyncMock()
        mock_instance = Mock()
        mock_session.get = AsyncMock(return_value=mock_instance)
        mock_session.commit = AsyncMock(side_effect=SQLAlchemyError("Update failed"))
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()
        mock_get_session.return_value = mock_session
        
        with pytest.raises(DatabaseOperationError, match="Failed to update"):
            await self.TestModelClass.update(1, name="New Name")
        
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.models.base.get_session')
    async def test_delete_success(self, mock_get_session):
        """Test successful model deletion."""
        mock_session = AsyncMock()
        mock_instance = Mock()
        mock_session.get = AsyncMock(return_value=mock_instance)
        mock_session.delete = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.close = AsyncMock()
        mock_get_session.return_value = mock_session
        
        result = await self.TestModelClass.delete(1)
        
        mock_session.get.assert_called_once_with(self.TestModelClass, 1)
        mock_session.delete.assert_called_once_with(mock_instance)
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
        assert result is True
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.models.base.get_session')
    async def test_delete_not_found(self, mock_get_session):
        """Test model deletion when instance not found."""
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=None)
        mock_session.close = AsyncMock()
        mock_get_session.return_value = mock_session
        
        result = await self.TestModelClass.delete(999)
        
        mock_session.get.assert_called_once_with(self.TestModelClass, 999)
        mock_session.close.assert_called_once()
        assert result is False
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.models.base.get_session')
    async def test_delete_error(self, mock_get_session):
        """Test model deletion with error."""
        mock_session = AsyncMock()
        mock_instance = Mock()
        mock_session.get = AsyncMock(return_value=mock_instance)
        mock_session.delete = AsyncMock(side_effect=SQLAlchemyError("Delete failed"))
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()
        mock_get_session.return_value = mock_session
        
        with pytest.raises(DatabaseOperationError, match="Failed to delete"):
            await self.TestModelClass.delete(1)
        
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.models.base.get_session')
    async def test_list_success(self, mock_get_session):
        """Test successful model listing."""
        mock_session = AsyncMock()
        mock_instances = [Mock(), Mock(), Mock()]
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_instances
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.close = AsyncMock()
        mock_get_session.return_value = mock_session
        
        result = await self.TestModelClass.list(limit=10, offset=5)
        
        mock_session.execute.assert_called_once()
        mock_session.close.assert_called_once()
        assert result == mock_instances
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.models.base.get_session')
    async def test_list_no_pagination(self, mock_get_session):
        """Test model listing without pagination."""
        mock_session = AsyncMock()
        mock_instances = [Mock(), Mock()]
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_instances
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.close = AsyncMock()
        mock_get_session.return_value = mock_session
        
        result = await self.TestModelClass.list()
        
        mock_session.execute.assert_called_once()
        mock_session.close.assert_called_once()
        assert result == mock_instances
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.models.base.get_session')
    async def test_list_error(self, mock_get_session):
        """Test model listing with error."""
        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(side_effect=SQLAlchemyError("List failed"))
        mock_session.close = AsyncMock()
        mock_get_session.return_value = mock_session
        
        with pytest.raises(DatabaseOperationError, match="Failed to list"):
            await self.TestModelClass.list()
        
        mock_session.close.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.models.base.get_session')
    async def test_count_success(self, mock_get_session):
        """Test successful model counting."""
        mock_session = AsyncMock()
        mock_result = Mock()
        mock_result.scalar.return_value = 42
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.close = AsyncMock()
        mock_get_session.return_value = mock_session
        
        result = await self.TestModelClass.count()
        
        mock_session.execute.assert_called_once()
        mock_session.close.assert_called_once()
        assert result == 42
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.models.base.get_session')
    async def test_count_none_result(self, mock_get_session):
        """Test model counting with None result."""
        mock_session = AsyncMock()
        mock_result = Mock()
        mock_result.scalar.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.close = AsyncMock()
        mock_get_session.return_value = mock_session
        
        result = await self.TestModelClass.count()
        
        assert result == 0
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.models.base.get_session')
    async def test_count_error(self, mock_get_session):
        """Test model counting with error."""
        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(side_effect=SQLAlchemyError("Count failed"))
        mock_session.close = AsyncMock()
        mock_get_session.return_value = mock_session
        
        with pytest.raises(DatabaseOperationError, match="Failed to count"):
            await self.TestModelClass.count()
        
        mock_session.close.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.models.base.get_session')
    async def test_exists_true(self, mock_get_session):
        """Test model exists returns True."""
        mock_session = AsyncMock()
        mock_result = Mock()
        mock_result.scalar.return_value = 1
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.close = AsyncMock()
        mock_get_session.return_value = mock_session
        
        result = await self.TestModelClass.exists(1)
        
        mock_session.execute.assert_called_once()
        mock_session.close.assert_called_once()
        assert result is True
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.models.base.get_session')
    async def test_exists_false(self, mock_get_session):
        """Test model exists returns False."""
        mock_session = AsyncMock()
        mock_result = Mock()
        mock_result.scalar.return_value = 0
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.close = AsyncMock()
        mock_get_session.return_value = mock_session
        
        result = await self.TestModelClass.exists(999)
        
        mock_session.execute.assert_called_once()
        mock_session.close.assert_called_once()
        assert result is False
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.models.base.get_session')
    async def test_exists_error(self, mock_get_session):
        """Test model exists with error."""
        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(side_effect=SQLAlchemyError("Exists check failed"))
        mock_session.close = AsyncMock()
        mock_get_session.return_value = mock_session
        
        with pytest.raises(DatabaseOperationError, match="Failed to check existence"):
            await self.TestModelClass.exists(1)
        
        mock_session.close.assert_called_once()
    
    def test_to_dict(self):
        """Test to_dict method."""
        instance = self.TestModelClass()
        instance.id = 1
        instance.name = "Test Name"
        
        # Mock the table columns
        mock_column1 = Mock()
        mock_column1.name = "id"
        mock_column2 = Mock()
        mock_column2.name = "name"
        instance.__table__ = Mock()
        instance.__table__.columns = [mock_column1, mock_column2]
        
        result = instance.to_dict()
        
        assert result == {"id": 1, "name": "Test Name"}


class TestSpecificModels:
    """Test specific model classes."""
    
    def test_project_model_structure(self):
        """Test Project model structure."""
        # Test that Project inherits from Model
        assert issubclass(Project, Model)
        assert hasattr(Project, '__tablename__')
        assert Project.__tablename__ == "projects"
    
    def test_conversation_model_structure(self):
        """Test Conversation model structure."""
        assert issubclass(Conversation, Model)
        assert hasattr(Conversation, '__tablename__')
        assert Conversation.__tablename__ == "conversations"
    
    def test_document_model_structure(self):
        """Test Document model structure."""
        assert issubclass(Document, Model)
        assert hasattr(Document, '__tablename__')
        assert Document.__tablename__ == "documents"
    
    def test_repository_model_structure(self):
        """Test Repository model structure."""
        assert issubclass(Repository, Model)
        assert hasattr(Repository, '__tablename__')
        assert Repository.__tablename__ == "repositories"
    
    @pytest.mark.asyncio
    async def test_project_crud_operations(self, project_data):
        """Test Project CRUD operations."""
        with patch('src.andamios_orm.models.base.get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_get_session.return_value = mock_session
            
            with patch('asyncio.to_thread') as mock_to_thread:
                mock_result = Mock()
                mock_result.scalar = Mock(return_value=1)
                mock_to_thread.side_effect = [mock_result, 1]
                
                # Test create
                project = await Project.create(**project_data)
                mock_session.add.assert_called()
                mock_session.commit.assert_called()
    
    @pytest.mark.asyncio
    async def test_conversation_crud_operations(self, conversation_data):
        """Test Conversation CRUD operations."""
        with patch('src.andamios_orm.models.base.get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_get_session.return_value = mock_session
            
            with patch('asyncio.to_thread') as mock_to_thread:
                mock_result = Mock()
                mock_result.scalar = Mock(return_value=1)
                mock_to_thread.side_effect = [mock_result, 1]
                
                # Test create
                conversation = await Conversation.create(**conversation_data)
                mock_session.add.assert_called()
                mock_session.commit.assert_called()
    
    @pytest.mark.asyncio
    async def test_document_crud_operations(self, document_data):
        """Test Document CRUD operations."""
        with patch('src.andamios_orm.models.base.get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_get_session.return_value = mock_session
            
            with patch('asyncio.to_thread') as mock_to_thread:
                mock_result = Mock()
                mock_result.scalar = Mock(return_value=1)
                mock_to_thread.side_effect = [mock_result, 1]
                
                # Test create
                document = await Document.create(**document_data)
                mock_session.add.assert_called()
                mock_session.commit.assert_called()
    
    @pytest.mark.asyncio
    async def test_repository_crud_operations(self, repository_data):
        """Test Repository CRUD operations."""
        with patch('src.andamios_orm.models.base.get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_get_session.return_value = mock_session
            
            with patch('asyncio.to_thread') as mock_to_thread:
                mock_result = Mock()
                mock_result.scalar = Mock(return_value=1)
                mock_to_thread.side_effect = [mock_result, 1]
                
                # Test create
                repository = await Repository.create(**repository_data)
                mock_session.add.assert_called()
                mock_session.commit.assert_called()


class TestModelExceptions:
    """Test model exception handling."""
    
    def setup_method(self):
        """Set up test fixtures."""
        class TestModelClass(Model):
            __tablename__ = "test_table"
            id = Column(Integer, primary_key=True)
            name = Column(String(255), nullable=False)
        
        self.TestModelClass = TestModelClass
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.models.base.get_session')
    async def test_create_general_exception(self, mock_get_session):
        """Test model creation with general exception."""
        mock_get_session.side_effect = Exception("Unexpected error")
        
        with pytest.raises(Exception, match="Unexpected error"):
            await self.TestModelClass.create(name="Test")
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.models.base.get_session')
    async def test_read_general_exception(self, mock_get_session):
        """Test model reading with general exception."""
        mock_get_session.side_effect = Exception("Unexpected error")
        
        with pytest.raises(Exception, match="Unexpected error"):
            await self.TestModelClass.read(1)
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.models.base.get_session')
    async def test_update_general_exception(self, mock_get_session):
        """Test model update with general exception."""
        mock_get_session.side_effect = Exception("Unexpected error")
        
        with pytest.raises(Exception, match="Unexpected error"):
            await self.TestModelClass.update(1, name="New Name")
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.models.base.get_session')
    async def test_delete_general_exception(self, mock_get_session):
        """Test model deletion with general exception."""
        mock_get_session.side_effect = Exception("Unexpected error")
        
        with pytest.raises(Exception, match="Unexpected error"):
            await self.TestModelClass.delete(1)
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.models.base.get_session')
    async def test_list_general_exception(self, mock_get_session):
        """Test model listing with general exception."""
        mock_get_session.side_effect = Exception("Unexpected error")
        
        with pytest.raises(Exception, match="Unexpected error"):
            await self.TestModelClass.list()
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.models.base.get_session')
    async def test_count_general_exception(self, mock_get_session):
        """Test model counting with general exception."""
        mock_get_session.side_effect = Exception("Unexpected error")
        
        with pytest.raises(Exception, match="Unexpected error"):
            await self.TestModelClass.count()
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.models.base.get_session')
    async def test_exists_general_exception(self, mock_get_session):
        """Test model exists with general exception."""
        mock_get_session.side_effect = Exception("Unexpected error")
        
        with pytest.raises(Exception, match="Unexpected error"):
            await self.TestModelClass.exists(1)


class TestModelIntegration:
    """Integration tests for model functionality."""
    
    @pytest.mark.asyncio
    async def test_model_inheritance(self):
        """Test that all models properly inherit from Model."""
        models = [Project, Conversation, Document, Repository]
        
        for model_class in models:
            assert issubclass(model_class, Model)
            assert hasattr(model_class, '__tablename__')
            assert hasattr(model_class, 'create')
            assert hasattr(model_class, 'read')
            assert hasattr(model_class, 'update')
            assert hasattr(model_class, 'delete')
            assert hasattr(model_class, 'list')
            assert hasattr(model_class, 'count')
            assert hasattr(model_class, 'exists')
    
    def test_base_declarative_base(self):
        """Test that Base is properly configured."""
        from src.andamios_orm.models.base import Base
        
        assert Base is not None
        assert hasattr(Base, 'metadata')
        assert Model.__bases__[0] == Base