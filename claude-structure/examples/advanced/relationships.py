"""
Example: Advanced Model Relationships

Description: Demonstrates complex relationships between models including
one-to-many, many-to-many, and one-to-one relationships with eager loading
and relationship-based queries.

Key Concepts:
- Model relationships (Foreign Keys, One-to-Many, Many-to-Many)
- Eager loading and lazy loading
- Relationship-based queries
- Join optimization
- Cascade operations

Prerequisites:
- PostgreSQL test database running
- Basic CRUD example understanding
"""

import asyncio
import uvloop
from datetime import datetime, timezone
from typing import Optional, List
from enum import Enum

from andamios_orm.core.engine import create_async_engine
from andamios_orm.core.session import AsyncSession
from andamios_orm.models.base import BaseModel, TimestampedModel
from andamios_orm.models.relationships import relationship, ForeignKey
from andamios_orm.repositories.generic import GenericRepository
from andamios_orm.queries.builder import QueryBuilder

DATABASE_URL = "postgresql+asyncpg://test_user:test_password@localhost:5432/test_andamios_orm"

# Enums
class PostStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class CommentStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

# Model definitions with relationships
class User(TimestampedModel):
    """User model with relationships."""
    
    __tablename__ = "users"
    
    id: int  # Primary key
    email: str
    username: str
    first_name: str
    last_name: str
    is_active: bool = True
    
    # Relationships
    profile: "UserProfile" = relationship("UserProfile", back_populates="user", uselist=False)
    posts: List["Post"] = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    comments: List["Comment"] = relationship("Comment", back_populates="author")
    followed_tags: List["Tag"] = relationship("Tag", secondary="user_tags", back_populates="followers")

class UserProfile(TimestampedModel):
    """User profile with one-to-one relationship."""
    
    __tablename__ = "user_profiles"
    
    id: int  # Primary key
    user_id: int = ForeignKey("users.id", ondelete="CASCADE")
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    birth_date: Optional[datetime] = None
    location: Optional[str] = None
    website: Optional[str] = None
    
    # Relationships
    user: User = relationship("User", back_populates="profile")

class Tag(BaseModel):
    """Tag model for many-to-many relationships."""
    
    __tablename__ = "tags"
    
    id: int  # Primary key
    name: str
    slug: str
    description: Optional[str] = None
    color: str = "#6B7280"
    
    # Relationships
    posts: List["Post"] = relationship("Post", secondary="post_tags", back_populates="tags")
    followers: List[User] = relationship("User", secondary="user_tags", back_populates="followed_tags")

class Post(TimestampedModel):
    """Post model with multiple relationships."""
    
    __tablename__ = "posts"
    
    id: int  # Primary key
    title: str
    slug: str
    content: str
    excerpt: Optional[str] = None
    status: PostStatus = PostStatus.DRAFT
    published_at: Optional[datetime] = None
    view_count: int = 0
    
    # Foreign keys
    author_id: int = ForeignKey("users.id", ondelete="CASCADE")
    
    # Relationships
    author: User = relationship("User", back_populates="posts")
    comments: List["Comment"] = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    tags: List[Tag] = relationship("Tag", secondary="post_tags", back_populates="posts")

class Comment(TimestampedModel):
    """Comment model with hierarchical relationships."""
    
    __tablename__ = "comments"
    
    id: int  # Primary key
    content: str
    status: CommentStatus = CommentStatus.PENDING
    
    # Foreign keys
    post_id: int = ForeignKey("posts.id", ondelete="CASCADE")
    author_id: int = ForeignKey("users.id", ondelete="CASCADE") 
    parent_id: Optional[int] = ForeignKey("comments.id", ondelete="CASCADE")
    
    # Relationships
    post: Post = relationship("Post", back_populates="comments")
    author: User = relationship("User", back_populates="comments")
    parent: Optional["Comment"] = relationship("Comment", remote_side=[id])
    replies: List["Comment"] = relationship("Comment", back_populates="parent")

# Association tables for many-to-many relationships
class PostTag(BaseModel):
    """Association table for Post-Tag many-to-many relationship."""
    
    __tablename__ = "post_tags"
    
    post_id: int = ForeignKey("posts.id", primary_key=True)
    tag_id: int = ForeignKey("tags.id", primary_key=True)

class UserTag(BaseModel):
    """Association table for User-Tag many-to-many relationship."""
    
    __tablename__ = "user_tags"
    
    user_id: int = ForeignKey("users.id", primary_key=True)
    tag_id: int = ForeignKey("tags.id", primary_key=True)
    created_at: datetime = datetime.now(timezone.utc)

# Repository definitions
class PostRepository(GenericRepository[Post]):
    """Post repository with relationship queries."""
    
    async def get_with_author(self, post_id: int) -> Optional[Post]:
        """Get post with author information."""
        return await self.get_by_id(post_id, include=["author", "author.profile"])
    
    async def get_with_comments(self, post_id: int) -> Optional[Post]:
        """Get post with all comments and their authors."""
        return await self.get_by_id(
            post_id, 
            include=["comments", "comments.author", "comments.replies"]
        )
    
    async def get_published_posts(self) -> List[Post]:
        """Get all published posts with authors."""
        return await self.find_many(
            {"status": PostStatus.PUBLISHED},
            include=["author"],
            order_by=["published_at DESC"]
        )
    
    async def get_posts_by_tag(self, tag_slug: str) -> List[Post]:
        """Get posts by tag slug."""
        return await (
            QueryBuilder(self.session, Post)
            .join(Post.tags)
            .filter(Tag.slug == tag_slug)
            .filter(Post.status == PostStatus.PUBLISHED)
            .include(["author", "tags"])
            .order_by(Post.published_at.desc())
            .all()
        )
    
    async def get_user_posts_with_stats(self, user_id: int) -> List[Post]:
        """Get user's posts with comment counts."""
        return await (
            QueryBuilder(self.session, Post)
            .filter(Post.author_id == user_id)
            .include(["comments", "tags"])
            .order_by(Post.created_at.desc())
            .all()
        )

class UserRepository(GenericRepository[User]):
    """User repository with relationship queries."""
    
    async def get_with_profile(self, user_id: int) -> Optional[User]:
        """Get user with profile information."""
        return await self.get_by_id(user_id, include=["profile"])
    
    async def get_active_authors(self) -> List[User]:
        """Get users who have published posts."""
        return await (
            QueryBuilder(self.session, User)
            .join(User.posts)
            .filter(Post.status == PostStatus.PUBLISHED)
            .filter(User.is_active == True)
            .include(["profile"])
            .distinct()
            .all()
        )
    
    async def get_users_following_tag(self, tag_slug: str) -> List[User]:
        """Get users following a specific tag."""
        return await (
            QueryBuilder(self.session, User)
            .join(User.followed_tags)
            .filter(Tag.slug == tag_slug)
            .include(["profile"])
            .all()
        )

class CommentRepository(GenericRepository[Comment]):
    """Comment repository with hierarchical queries."""
    
    async def get_thread(self, parent_comment_id: int) -> List[Comment]:
        """Get comment thread (parent + all replies)."""
        return await (
            QueryBuilder(self.session, Comment)
            .filter(
                (Comment.id == parent_comment_id) | 
                (Comment.parent_id == parent_comment_id)
            )
            .include(["author", "replies"])
            .order_by(Comment.created_at.asc())
            .all()
        )
    
    async def get_pending_comments(self) -> List[Comment]:
        """Get comments pending approval."""
        return await self.find_many(
            {"status": CommentStatus.PENDING},
            include=["author", "post"],
            order_by=["created_at ASC"]
        )

async def setup_sample_data(session: AsyncSession):
    """Create sample data for relationship demonstrations."""
    
    user_repo = UserRepository(session)
    tag_repo = GenericRepository[Tag](session)
    post_repo = PostRepository(session)
    comment_repo = CommentRepository(session)
    
    print("🔧 Setting up sample data...")
    
    # Create users with profiles
    users_data = [
        {
            "email": "alice@example.com",
            "username": "alice",
            "first_name": "Alice",
            "last_name": "Johnson",
            "profile": {
                "bio": "Tech writer and Python enthusiast",
                "location": "San Francisco, CA",
                "website": "https://alice-codes.dev"
            }
        },
        {
            "email": "bob@example.com", 
            "username": "bob",
            "first_name": "Bob",
            "last_name": "Smith",
            "profile": {
                "bio": "Full-stack developer",
                "location": "New York, NY"
            }
        }
    ]
    
    users = []
    for user_data in users_data:
        profile_data = user_data.pop("profile")
        user = User(**user_data)
        user.profile = UserProfile(**profile_data)
        created_user = await user_repo.create(user)
        users.append(created_user)
    
    # Create tags
    tags_data = [
        {"name": "Python", "slug": "python", "description": "Python programming", "color": "#3776ab"},
        {"name": "Async", "slug": "async", "description": "Asynchronous programming", "color": "#ff6b6b"},
        {"name": "Database", "slug": "database", "description": "Database related", "color": "#4ecdc4"},
        {"name": "ORM", "slug": "orm", "description": "Object-Relational Mapping", "color": "#45b7d1"}
    ]
    
    tags = []
    for tag_data in tags_data:
        tag = Tag(**tag_data)
        created_tag = await tag_repo.create(tag)
        tags.append(created_tag)
    
    # Create posts with tags
    posts_data = [
        {
            "title": "Getting Started with Async Python",
            "slug": "getting-started-async-python",
            "content": "In this post, we'll explore async/await in Python...",
            "excerpt": "Learn the basics of async programming",
            "status": PostStatus.PUBLISHED,
            "published_at": datetime.now(timezone.utc),
            "author_id": users[0].id,
            "tag_slugs": ["python", "async"]
        },
        {
            "title": "Building an ORM with SQLAlchemy",
            "slug": "building-orm-sqlalchemy",
            "content": "ORMs simplify database interactions...",
            "excerpt": "Deep dive into ORM patterns",
            "status": PostStatus.PUBLISHED, 
            "published_at": datetime.now(timezone.utc),
            "author_id": users[1].id,
            "tag_slugs": ["python", "database", "orm"]
        },
        {
            "title": "Advanced Database Patterns",
            "slug": "advanced-database-patterns",
            "content": "This post covers advanced database patterns...",
            "excerpt": "Advanced patterns for database design",
            "status": PostStatus.DRAFT,
            "author_id": users[0].id,
            "tag_slugs": ["database"]
        }
    ]
    
    posts = []
    for post_data in posts_data:
        tag_slugs = post_data.pop("tag_slugs")
        post = Post(**post_data)
        
        # Add tags to post
        post.tags = [tag for tag in tags if tag.slug in tag_slugs]
        
        created_post = await post_repo.create(post)
        posts.append(created_post)
    
    # Create comments with replies
    comments_data = [
        {
            "content": "Great post! Very helpful explanation.",
            "status": CommentStatus.APPROVED,
            "post_id": posts[0].id,
            "author_id": users[1].id
        },
        {
            "content": "Thanks for the feedback!",
            "status": CommentStatus.APPROVED,
            "post_id": posts[0].id,
            "author_id": users[0].id,
            "parent_id": None  # Will be set after first comment is created
        },
        {
            "content": "Could you elaborate on error handling?",
            "status": CommentStatus.PENDING,
            "post_id": posts[1].id,
            "author_id": users[0].id
        }
    ]
    
    comments = []
    for i, comment_data in enumerate(comments_data):
        comment = Comment(**comment_data)
        if i == 1:  # Second comment is a reply to the first
            comment.parent_id = comments[0].id
        created_comment = await comment_repo.create(comment)
        comments.append(created_comment)
    
    # Add user tag followings
    users[0].followed_tags = [tags[0], tags[1]]  # Alice follows Python and Async
    users[1].followed_tags = [tags[2], tags[3]]  # Bob follows Database and ORM
    
    await session.commit()
    print(f"✅ Created {len(users)} users, {len(tags)} tags, {len(posts)} posts, {len(comments)} comments")
    
    return {
        "users": users,
        "tags": tags, 
        "posts": posts,
        "comments": comments
    }

async def demonstrate_eager_loading():
    """Demonstrate eager loading of relationships."""
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    try:
        async with AsyncSession(engine) as session:
            post_repo = PostRepository(session)
            
            print("\n🔄 Eager Loading Examples")
            print("=" * 30)
            
            # 1. Load post with author and profile
            print("\n1. Loading post with author and profile...")
            post_with_author = await post_repo.get_with_author(1)
            if post_with_author:
                print(f"✅ Post: {post_with_author.title}")
                print(f"   Author: {post_with_author.author.first_name} {post_with_author.author.last_name}")
                if post_with_author.author.profile:
                    print(f"   Bio: {post_with_author.author.profile.bio}")
                    print(f"   Location: {post_with_author.author.profile.location}")
            
            # 2. Load post with all comments and replies
            print("\n2. Loading post with comments and replies...")
            post_with_comments = await post_repo.get_with_comments(1)
            if post_with_comments:
                print(f"✅ Post: {post_with_comments.title}")
                print(f"   Comments ({len(post_with_comments.comments)}):")
                for comment in post_with_comments.comments:
                    print(f"   - {comment.author.username}: {comment.content[:50]}...")
                    if comment.replies:
                        for reply in comment.replies:
                            print(f"     └─ {reply.author.username}: {reply.content[:50]}...")
            
            # 3. Load posts by tag with authors
            print("\n3. Loading posts by tag with authors...")
            python_posts = await post_repo.get_posts_by_tag("python")
            print(f"✅ Found {len(python_posts)} posts tagged with 'python':")
            for post in python_posts:
                print(f"   - {post.title} by {post.author.username}")
                print(f"     Tags: {', '.join([tag.name for tag in post.tags])}")
    
    finally:
        await engine.dispose()

async def demonstrate_relationship_queries():
    """Demonstrate complex queries involving relationships."""
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    try:
        async with AsyncSession(engine) as session:
            user_repo = UserRepository(session)
            post_repo = PostRepository(session)
            
            print("\n🔍 Relationship Query Examples")
            print("=" * 35)
            
            # 1. Find active authors (users with published posts)
            print("\n1. Finding active authors...")
            active_authors = await user_repo.get_active_authors()
            print(f"✅ Found {len(active_authors)} active authors:")
            for author in active_authors:
                print(f"   - {author.username} ({author.first_name} {author.last_name})")
                if author.profile:
                    print(f"     Bio: {author.profile.bio}")
            
            # 2. Get user's posts with statistics
            print("\n2. Getting user posts with statistics...")
            user_posts = await post_repo.get_user_posts_with_stats(1)
            print(f"✅ User has {len(user_posts)} posts:")
            for post in user_posts:
                comment_count = len(post.comments)
                tag_names = [tag.name for tag in post.tags]
                print(f"   - {post.title}")
                print(f"     Status: {post.status.value}, Comments: {comment_count}")
                print(f"     Tags: {', '.join(tag_names)}")
            
            # 3. Find users following specific tags
            print("\n3. Finding users following 'python' tag...")
            python_followers = await user_repo.get_users_following_tag("python")
            print(f"✅ Found {len(python_followers)} users following 'python':")
            for user in python_followers:
                print(f"   - {user.username}")
    
    finally:
        await engine.dispose()

async def demonstrate_cascade_operations():
    """Demonstrate cascade operations (create, update, delete)."""
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    try:
        async with AsyncSession(engine) as session:
            user_repo = UserRepository(session)
            post_repo = PostRepository(session)
            
            print("\n⚡ Cascade Operations Examples")
            print("=" * 35)
            
            # 1. Create user with profile in one operation
            print("\n1. Creating user with profile...")
            user_with_profile = User(
                email="cascade@example.com",
                username="cascadeuser",
                first_name="Cascade",
                last_name="User",
                profile=UserProfile(
                    bio="Testing cascade operations",
                    location="Test City"
                )
            )
            
            created_user = await user_repo.create(user_with_profile)
            print(f"✅ Created user with profile: {created_user.username}")
            print(f"   Profile bio: {created_user.profile.bio}")
            
            # 2. Create post with tags and immediate comment
            print("\n2. Creating post with relationships...")
            from andamios_orm.repositories.generic import GenericRepository
            tag_repo = GenericRepository[Tag](session)
            
            # Get existing tags
            python_tag = await tag_repo.find_one({"slug": "python"})
            async_tag = await tag_repo.find_one({"slug": "async"})
            
            post_with_relations = Post(
                title="Cascade Operations Test",
                slug="cascade-operations-test",
                content="Testing cascade operations with relationships...",
                status=PostStatus.PUBLISHED,
                published_at=datetime.now(timezone.utc),
                author_id=created_user.id,
                tags=[python_tag, async_tag],
                comments=[
                    Comment(
                        content="First comment on cascade post",
                        status=CommentStatus.APPROVED,
                        author_id=created_user.id
                    )
                ]
            )
            
            created_post = await post_repo.create(post_with_relations)
            print(f"✅ Created post with tags and comments: {created_post.title}")
            print(f"   Tags: {len(created_post.tags)}")
            print(f"   Comments: {len(created_post.comments)}")
            
            # 3. Update relationships
            print("\n3. Updating relationships...")
            
            # Add another tag to the post
            orm_tag = await tag_repo.find_one({"slug": "orm"})
            created_post.tags.append(orm_tag)
            
            # Add a reply to the comment
            original_comment = created_post.comments[0]
            reply = Comment(
                content="Reply to the first comment",
                status=CommentStatus.APPROVED,
                post_id=created_post.id,
                author_id=created_user.id,
                parent_id=original_comment.id
            )
            created_post.comments.append(reply)
            
            updated_post = await post_repo.update(created_post)
            print(f"✅ Updated post relationships")
            print(f"   New tag count: {len(updated_post.tags)}")
            print(f"   New comment count: {len(updated_post.comments)}")
            
            await session.commit()
            
            # 4. Demonstrate cascade delete
            print("\n4. Testing cascade delete...")
            print(f"   Post has {len(updated_post.comments)} comments before delete")
            
            # Delete the post - comments should be cascade deleted
            deleted = await post_repo.delete_by_id(updated_post.id)
            if deleted:
                print("✅ Post deleted successfully")
                
                # Verify comments were cascade deleted
                comment_repo = GenericRepository[Comment](session)
                remaining_comments = await comment_repo.find_many({"post_id": updated_post.id})
                print(f"   Comments remaining: {len(remaining_comments)} (should be 0)")
            
            await session.commit()
    
    finally:
        await engine.dispose()

async def main():
    """Run all relationship examples."""
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    try:
        # Setup database tables (this would be done via migrations in real app)
        print("🏗️ Setting up database tables...")
        # await create_all_tables(engine)  # Implementation depends on migration system
        
        async with AsyncSession(engine) as session:
            sample_data = await setup_sample_data(session)
        
        await demonstrate_eager_loading()
        await demonstrate_relationship_queries()
        await demonstrate_cascade_operations()
        
        print("\n✅ All relationship examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        raise
    
    finally:
        await engine.dispose()

if __name__ == "__main__":
    # Use uvloop for better async performance
    if hasattr(uvloop, 'install'):
        uvloop.install()
    
    asyncio.run(main())