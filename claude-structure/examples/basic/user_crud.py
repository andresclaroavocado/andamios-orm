"""
Example: Basic User CRUD Operations

Description: Demonstrates basic Create, Read, Update, Delete operations
using the Andamios ORM with a simple User model.

Key Concepts:
- Model definition with BaseModel
- Repository pattern for data access
- Async database operations
- Transaction management
- Error handling

Prerequisites:
- PostgreSQL test database running
- Andamios ORM installed
"""

import asyncio
import uvloop
from datetime import datetime, timezone
from typing import Optional

# These imports will be available once the library is implemented
from andamios_orm.core.engine import create_async_engine
from andamios_orm.core.session import AsyncSession
from andamios_orm.models.base import BaseModel, TimestampedModel
from andamios_orm.repositories.generic import GenericRepository

# Database configuration
DATABASE_URL = "postgresql+asyncpg://test_user:test_password@localhost:5432/test_andamios_orm"

# Model definition
class User(TimestampedModel):
    """User model with basic fields."""
    
    __tablename__ = "users"
    
    id: int  # Primary key (auto-generated)
    email: str  # Unique email address
    username: str  # Unique username
    first_name: str
    last_name: str
    is_active: bool = True
    is_verified: bool = False
    
    class Meta:
        constraints = [
            UniqueConstraint("email"),
            UniqueConstraint("username"),
            CheckConstraint("length(email) > 0"),
            CheckConstraint("length(username) > 0"),
        ]

# Repository definition
class UserRepository(GenericRepository[User]):
    """User-specific repository with custom methods."""
    
    async def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email address."""
        return await self.find_one({"email": email})
    
    async def find_by_username(self, username: str) -> Optional[User]:
        """Find user by username.""" 
        return await self.find_one({"username": username})
    
    async def get_active_users(self) -> list[User]:
        """Get all active users."""
        return await self.find_many({"is_active": True})
    
    async def update_last_login(self, user_id: int) -> None:
        """Update user's last login timestamp."""
        await self.update_by_id(user_id, {
            "last_login": datetime.now(timezone.utc)
        })

async def demonstrate_user_crud():
    """Demonstrate basic CRUD operations with User model."""
    
    # Set uvloop as the event loop for better performance
    if hasattr(uvloop, 'install'):
        uvloop.install()
    
    # Create database engine
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    try:
        # Create database session
        async with AsyncSession(engine) as session:
            # Initialize repository
            user_repo = UserRepository(session)
            
            print("🚀 Andamios ORM - Basic User CRUD Example")
            print("=" * 50)
            
            # 1. CREATE - Create a new user
            print("\n1. Creating a new user...")
            new_user = User(
                email="john.doe@example.com",
                username="johndoe",
                first_name="John",
                last_name="Doe",
                is_active=True,
                is_verified=False
            )
            
            created_user = await user_repo.create(new_user)
            print(f"✅ Created user: {created_user.username} (ID: {created_user.id})")
            print(f"   Email: {created_user.email}")
            print(f"   Created at: {created_user.created_at}")
            
            # 2. READ - Get user by ID
            print(f"\n2. Reading user by ID ({created_user.id})...")
            user_by_id = await user_repo.get_by_id(created_user.id)
            if user_by_id:
                print(f"✅ Found user: {user_by_id.username}")
                print(f"   Full name: {user_by_id.first_name} {user_by_id.last_name}")
            
            # 3. READ - Get user by email (custom method)
            print(f"\n3. Reading user by email ({created_user.email})...")
            user_by_email = await user_repo.find_by_email(created_user.email)
            if user_by_email:
                print(f"✅ Found user by email: {user_by_email.username}")
            
            # 4. UPDATE - Update user information
            print(f"\n4. Updating user information...")
            updated_data = {
                "first_name": "Johnny",
                "is_verified": True,
                "updated_at": datetime.now(timezone.utc)
            }
            
            updated_user = await user_repo.update_by_id(created_user.id, updated_data)
            print(f"✅ Updated user: {updated_user.first_name} {updated_user.last_name}")
            print(f"   Verified: {updated_user.is_verified}")
            print(f"   Updated at: {updated_user.updated_at}")
            
            # 5. LIST - Get all active users
            print("\n5. Listing all active users...")
            active_users = await user_repo.get_active_users()
            print(f"✅ Found {len(active_users)} active user(s):")
            for user in active_users:
                print(f"   - {user.username} ({user.email})")
            
            # 6. BULK CREATE - Create multiple users
            print("\n6. Creating multiple users...")
            new_users = [
                User(
                    email=f"user{i}@example.com",
                    username=f"user{i}",
                    first_name=f"User{i}",
                    last_name="Test",
                    is_active=True
                ) for i in range(1, 4)
            ]
            
            created_users = await user_repo.create_many(new_users)
            print(f"✅ Created {len(created_users)} users in bulk")
            
            # 7. QUERY - Complex filtering
            print("\n7. Complex query with filters...")
            from andamios_orm.queries.filters import FilterBuilder
            
            filters = (
                FilterBuilder(User)
                .eq("is_active", True)
                .eq("is_verified", True)
                .build()
            )
            
            verified_users = await user_repo.find_many(filters)
            print(f"✅ Found {len(verified_users)} verified users")
            
            # 8. DELETE - Delete a user
            print(f"\n8. Deleting user {created_users[0].username}...")
            deleted = await user_repo.delete_by_id(created_users[0].id)
            if deleted:
                print("✅ User deleted successfully")
            
            # 9. COUNT - Count total users
            print("\n9. Counting total users...")
            user_count = await user_repo.count()
            print(f"✅ Total users in database: {user_count}")
            
            # Commit all changes
            await session.commit()
            print("\n✅ All operations completed successfully!")
            
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        raise
        
    finally:
        # Clean up database engine
        await engine.dispose()
        print("\n🔧 Database connection closed")

async def demonstrate_error_handling():
    """Demonstrate proper error handling patterns."""
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    try:
        async with AsyncSession(engine) as session:
            user_repo = UserRepository(session)
            
            print("\n🛡️ Error Handling Examples")
            print("=" * 30)
            
            # 1. Duplicate email error
            print("\n1. Testing duplicate email constraint...")
            try:
                user1 = User(
                    email="duplicate@example.com",
                    username="user1",
                    first_name="User",
                    last_name="One"
                )
                await user_repo.create(user1)
                
                # This should fail due to unique constraint
                user2 = User(
                    email="duplicate@example.com",  # Same email
                    username="user2",
                    first_name="User", 
                    last_name="Two"
                )
                await user_repo.create(user2)
                
            except Exception as e:
                print(f"✅ Caught expected error: {type(e).__name__}")
                print(f"   Message: {str(e)}")
            
            # 2. Not found error
            print("\n2. Testing not found scenario...")
            non_existent_user = await user_repo.get_by_id(99999)
            if non_existent_user is None:
                print("✅ Properly handled non-existent user (returned None)")
            
            # 3. Invalid data error
            print("\n3. Testing validation errors...")
            try:
                invalid_user = User(
                    email="",  # Empty email should fail validation
                    username="testuser",
                    first_name="Test",
                    last_name="User"
                )
                await user_repo.create(invalid_user)
                
            except Exception as e:
                print(f"✅ Caught validation error: {type(e).__name__}")
                print(f"   Message: {str(e)}")
    
    finally:
        await engine.dispose()

async def demonstrate_transactions():
    """Demonstrate transaction management."""
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    try:
        print("\n💾 Transaction Management Examples") 
        print("=" * 35)
        
        # 1. Successful transaction
        print("\n1. Successful transaction...")
        async with AsyncSession(engine) as session:
            user_repo = UserRepository(session)
            
            async with session.begin():  # Start transaction
                user1 = User(
                    email="trans1@example.com",
                    username="transuser1",
                    first_name="Trans",
                    last_name="User1"
                )
                
                user2 = User(
                    email="trans2@example.com",
                    username="transuser2", 
                    first_name="Trans",
                    last_name="User2"
                )
                
                await user_repo.create(user1)
                await user_repo.create(user2)
                
                # Transaction commits automatically
                print("✅ Transaction committed successfully")
        
        # 2. Failed transaction with rollback
        print("\n2. Failed transaction with rollback...")
        try:
            async with AsyncSession(engine) as session:
                user_repo = UserRepository(session)
                
                async with session.begin():  # Start transaction
                    user3 = User(
                        email="trans3@example.com",
                        username="transuser3",
                        first_name="Trans",
                        last_name="User3"
                    )
                    
                    await user_repo.create(user3)
                    print("   First user created...")
                    
                    # This should fail due to duplicate email
                    user4 = User(
                        email="trans3@example.com",  # Duplicate email
                        username="transuser4",
                        first_name="Trans",
                        last_name="User4"
                    )
                    
                    await user_repo.create(user4)  # This will raise an error
                    
        except Exception as e:
            print(f"✅ Transaction rolled back due to error: {type(e).__name__}")
            
            # Verify that user3 was not saved due to rollback
            async with AsyncSession(engine) as session:
                user_repo = UserRepository(session)
                user3_check = await user_repo.find_by_email("trans3@example.com")
                if user3_check is None:
                    print("✅ Rollback successful - user3 was not saved")
                
    finally:
        await engine.dispose()

async def main():
    """Run all examples."""
    await demonstrate_user_crud()
    await demonstrate_error_handling()
    await demonstrate_transactions()

if __name__ == "__main__":
    # Use uvloop for better async performance
    if hasattr(uvloop, 'install'):
        uvloop.install()
    
    asyncio.run(main())