"""
Example: FastAPI Integration with Andamios ORM

Description: Demonstrates how to integrate Andamios ORM with FastAPI
including dependency injection, request-scoped sessions, automatic
transaction management, and proper error handling.

Key Concepts:
- FastAPI dependency injection
- Request-scoped database sessions
- Automatic transaction management
- Repository pattern with FastAPI
- Error handling and validation
- Pydantic model integration

Prerequisites:
- FastAPI installed
- PostgreSQL test database running
- Understanding of basic CRUD operations
"""

import asyncio
import uvloop
from datetime import datetime, timezone
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel as PydanticModel, Field, EmailStr
import uvicorn

# Andamios ORM imports
from andamios_orm.core.engine import create_async_engine, AsyncEngine
from andamios_orm.core.session import AsyncSession
from andamios_orm.models.base import BaseModel, TimestampedModel
from andamios_orm.repositories.generic import GenericRepository
from andamios_orm.integration.fastapi import FastAPIIntegration

# Database configuration
DATABASE_URL = "postgresql+asyncpg://test_user:test_password@localhost:5432/test_andamios_orm"

# Global engine instance
engine: Optional[AsyncEngine] = None

# ORM Models
class User(TimestampedModel):
    """User ORM model."""
    
    __tablename__ = "users"
    
    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    is_active: bool = True
    is_verified: bool = False

class Post(TimestampedModel):
    """Post ORM model."""
    
    __tablename__ = "posts"
    
    id: int
    title: str
    content: str
    is_published: bool = False
    author_id: int
    view_count: int = 0

# Pydantic Models (API schemas)
class UserBase(PydanticModel):
    """Base user schema."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)

class UserCreate(UserBase):
    """User creation schema."""
    pass

class UserUpdate(PydanticModel):
    """User update schema."""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None

class UserResponse(UserBase):
    """User response schema."""
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PostBase(PydanticModel):
    """Base post schema."""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    is_published: bool = False

class PostCreate(PostBase):
    """Post creation schema."""
    pass

class PostUpdate(PydanticModel):
    """Post update schema."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    is_published: Optional[bool] = None

class PostResponse(PostBase):
    """Post response schema."""
    id: int
    author_id: int
    view_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PostWithAuthor(PostResponse):
    """Post with author information."""
    author: UserResponse

# Repository classes
class UserRepository(GenericRepository[User]):
    """User repository with custom methods."""
    
    async def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email."""
        return await self.find_one({"email": email})
    
    async def find_by_username(self, username: str) -> Optional[User]:
        """Find user by username."""
        return await self.find_one({"username": username})
    
    async def get_active_users(self) -> List[User]:
        """Get all active users."""
        return await self.find_many({"is_active": True})

class PostRepository(GenericRepository[Post]):
    """Post repository with custom methods."""
    
    async def find_by_author(self, author_id: int) -> List[Post]:
        """Find posts by author."""
        return await self.find_many({"author_id": author_id})
    
    async def get_published_posts(self) -> List[Post]:
        """Get all published posts."""
        return await self.find_many(
            {"is_published": True},
            order_by=["created_at DESC"]
        )
    
    async def increment_view_count(self, post_id: int) -> Optional[Post]:
        """Increment post view count."""
        post = await self.get_by_id(post_id)
        if post:
            post.view_count += 1
            return await self.update(post)
        return None

# Database lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage database lifecycle."""
    global engine
    
    # Startup
    print("🚀 Starting up - Initializing database connection...")
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    # Test database connection
    try:
        async with AsyncSession(engine) as session:
            await session.execute("SELECT 1")
        print("✅ Database connection established")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        raise
    
    yield
    
    # Shutdown
    print("🛑 Shutting down - Closing database connection...")
    if engine:
        await engine.dispose()
    print("✅ Database connection closed")

# FastAPI app setup
app = FastAPI(
    title="Andamios ORM FastAPI Example",
    description="Example integration of Andamios ORM with FastAPI",
    version="1.0.0",
    lifespan=lifespan
)

# Dependency injection
async def get_db_session() -> AsyncSession:
    """Get database session for request."""
    if not engine:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database engine not initialized"
        )
    
    async with AsyncSession(engine) as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def get_user_repository(session: AsyncSession = Depends(get_db_session)) -> UserRepository:
    """Get user repository."""
    return UserRepository(session)

async def get_post_repository(session: AsyncSession = Depends(get_db_session)) -> PostRepository:
    """Get post repository."""
    return PostRepository(session)

# Exception handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

# User endpoints
@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Create a new user."""
    
    # Check if email already exists
    existing_user = await user_repo.find_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    existing_username = await user_repo.find_by_username(user_data.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create user
    user = User(**user_data.model_dump())
    created_user = await user_repo.create(user)
    await user_repo.session.commit()
    
    return UserResponse.model_validate(created_user)

@app.get("/users/", response_model=List[UserResponse])
async def list_users(
    active_only: bool = False,
    user_repo: UserRepository = Depends(get_user_repository)
):
    """List all users."""
    if active_only:
        users = await user_repo.get_active_users()
    else:
        users = await user_repo.list()
    
    return [UserResponse.model_validate(user) for user in users]

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Get user by ID."""
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.model_validate(user)

@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Update user by ID."""
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update only provided fields
    update_data = user_data.model_dump(exclude_unset=True)
    
    # Check email uniqueness if email is being updated
    if "email" in update_data:
        existing_user = await user_repo.find_by_email(update_data["email"])
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Check username uniqueness if username is being updated
    if "username" in update_data:
        existing_username = await user_repo.find_by_username(update_data["username"])
        if existing_username and existing_username.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    updated_user = await user_repo.update_by_id(user_id, update_data)
    await user_repo.session.commit()
    
    return UserResponse.model_validate(updated_user)

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Delete user by ID."""
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    await user_repo.delete_by_id(user_id)
    await user_repo.session.commit()

# Post endpoints
@app.post("/posts/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    author_id: int,
    post_repo: PostRepository = Depends(get_post_repository),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Create a new post."""
    
    # Verify author exists
    author = await user_repo.get_by_id(author_id)
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found"
        )
    
    # Create post
    post = Post(**post_data.model_dump(), author_id=author_id)
    created_post = await post_repo.create(post)
    await post_repo.session.commit()
    
    return PostResponse.model_validate(created_post)

@app.get("/posts/", response_model=List[PostResponse])
async def list_posts(
    published_only: bool = False,
    author_id: Optional[int] = None,
    post_repo: PostRepository = Depends(get_post_repository)
):
    """List posts with optional filters."""
    if published_only:
        posts = await post_repo.get_published_posts()
    elif author_id:
        posts = await post_repo.find_by_author(author_id)
    else:
        posts = await post_repo.list()
    
    return [PostResponse.model_validate(post) for post in posts]

@app.get("/posts/{post_id}", response_model=PostWithAuthor)
async def get_post(
    post_id: int,
    increment_views: bool = False,
    post_repo: PostRepository = Depends(get_post_repository),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Get post by ID with optional view count increment."""
    
    if increment_views:
        post = await post_repo.increment_view_count(post_id)
        if post:
            await post_repo.session.commit()
    else:
        post = await post_repo.get_by_id(post_id)
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Get author information
    author = await user_repo.get_by_id(post.author_id)
    
    post_dict = PostResponse.model_validate(post).model_dump()
    author_dict = UserResponse.model_validate(author).model_dump()
    
    return PostWithAuthor(**post_dict, author=author_dict)

@app.put("/posts/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post_data: PostUpdate,
    post_repo: PostRepository = Depends(get_post_repository)
):
    """Update post by ID."""
    post = await post_repo.get_by_id(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    update_data = post_data.model_dump(exclude_unset=True)
    updated_post = await post_repo.update_by_id(post_id, update_data)
    await post_repo.session.commit()
    
    return PostResponse.model_validate(updated_post)

@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    post_repo: PostRepository = Depends(get_post_repository)
):
    """Delete post by ID."""
    post = await post_repo.get_by_id(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    await post_repo.delete_by_id(post_id)
    await post_repo.session.commit()

# Health check endpoint
@app.get("/health")
async def health_check(session: AsyncSession = Depends(get_db_session)):
    """Health check endpoint."""
    try:
        # Test database connection
        result = await session.execute("SELECT 1 as health_check")
        row = result.fetchone()
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now(timezone.utc),
            "check_result": row[0] if row else None
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database health check failed: {str(e)}"
        )

# Middleware for request timing and logging
@app.middleware("http")
async def add_process_time_header(request, call_next):
    """Add request processing time header."""
    import time
    
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

# Example client functions for testing
async def demo_api_usage():
    """Demonstrate API usage programmatically."""
    import httpx
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("🧪 Testing API endpoints...")
        
        # 1. Create a user
        print("\n1. Creating user...")
        user_data = {
            "email": "api@example.com",
            "username": "apiuser",
            "first_name": "API",
            "last_name": "User"
        }
        
        response = await client.post(f"{base_url}/users/", json=user_data)
        if response.status_code == 201:
            created_user = response.json()
            user_id = created_user["id"]
            print(f"✅ Created user: {created_user['username']} (ID: {user_id})")
        else:
            print(f"❌ Failed to create user: {response.text}")
            return
        
        # 2. Create a post
        print("\n2. Creating post...")
        post_data = {
            "title": "API Integration Test",
            "content": "This post was created via the API",
            "is_published": True
        }
        
        response = await client.post(f"{base_url}/posts/?author_id={user_id}", json=post_data)
        if response.status_code == 201:
            created_post = response.json()
            post_id = created_post["id"]
            print(f"✅ Created post: {created_post['title']} (ID: {post_id})")
        else:
            print(f"❌ Failed to create post: {response.text}")
            return
        
        # 3. Get post with author
        print("\n3. Getting post with author...")
        response = await client.get(f"{base_url}/posts/{post_id}?increment_views=true")
        if response.status_code == 200:
            post_with_author = response.json()
            print(f"✅ Retrieved post: {post_with_author['title']}")
            print(f"   Author: {post_with_author['author']['first_name']} {post_with_author['author']['last_name']}")
            print(f"   Views: {post_with_author['view_count']}")
        
        # 4. List users
        print("\n4. Listing users...")
        response = await client.get(f"{base_url}/users/?active_only=true")
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Found {len(users)} active users")
        
        # 5. Health check
        print("\n5. Checking API health...")
        response = await client.get(f"{base_url}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ API is healthy: {health['status']}")

def run_server():
    """Run the FastAPI server."""
    if hasattr(uvloop, 'install'):
        uvloop.install()
    
    uvicorn.run(
        "fastapi_integration:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        # Run demo client
        if hasattr(uvloop, 'install'):
            uvloop.install()
        asyncio.run(demo_api_usage())
    else:
        # Run server
        run_server()