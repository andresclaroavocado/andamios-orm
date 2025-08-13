"""
Example 02: Model Definition and Basic Fields

This example demonstrates how to:
- Define models inheriting from Base
- Use various field types and constraints
- Set up table configuration
- Handle model validation with Pydantic integration

Expected behavior:
- Models are properly defined with type hints
- Tables are created with correct schema
- Validation works for model instances
- Relationships are properly configured
"""

import asyncio
import uvloop
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from andamios_orm import Base, create_engine, sessionmaker, AsyncSession
from andamios_orm.fields import (
    Column, Integer, String, Text, DateTime, Date, Boolean, 
    Decimal as DecimalField, UUID as UUIDField, JSON
)
from andamios_orm.validators import validates
from andamios_orm.mixins import TimestampMixin, SoftDeleteMixin


class User(Base, TimestampMixin):
    """
    User model demonstrating basic field types and validation.
    
    Inherits from TimestampMixin to automatically include created_at 
    and updated_at fields.
    """
    __tablename__ = "users"
    
    # Primary key
    id: int = Column(Integer, primary_key=True, index=True)
    
    # Basic string fields with constraints
    username: str = Column(String(50), unique=True, nullable=False, index=True)
    email: str = Column(String(255), unique=True, nullable=False)
    first_name: str = Column(String(100), nullable=False)
    last_name: str = Column(String(100), nullable=False)
    
    # Optional fields
    bio: Optional[str] = Column(Text, nullable=True)
    avatar_url: Optional[str] = Column(String(500), nullable=True)
    
    # Boolean field
    is_active: bool = Column(Boolean, default=True, nullable=False)
    is_verified: bool = Column(Boolean, default=False, nullable=False)
    
    # Date field
    birth_date: Optional[date] = Column(Date, nullable=True)
    
    # UUID field for external references
    external_id: UUID = Column(UUIDField, default=uuid4, unique=True)
    
    # JSON field for flexible data
    preferences: dict = Column(JSON, default=dict)
    
    # Model validation
    @validates('email')
    def validate_email(self, key: str, address: str) -> str:
        """Validate email format."""
        if '@' not in address:
            raise ValueError("Invalid email address")
        return address.lower()
    
    @validates('username')
    def validate_username(self, key: str, username: str) -> str:
        """Validate username format."""
        if len(username) < 3:
            raise ValueError("Username must be at least 3 characters")
        if not username.isalnum():
            raise ValueError("Username must be alphanumeric")
        return username.lower()
    
    @property
    def full_name(self) -> str:
        """Computed property for full name."""
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}')>"


class Product(Base, TimestampMixin, SoftDeleteMixin):
    """
    Product model demonstrating decimal fields and soft delete.
    
    Includes both timestamp and soft delete mixins.
    """
    __tablename__ = "products"
    
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(200), nullable=False, index=True)
    description: str = Column(Text, nullable=True)
    
    # Decimal fields for precise monetary calculations
    price: Decimal = Column(DecimalField(10, 2), nullable=False)
    cost: Optional[Decimal] = Column(DecimalField(10, 2), nullable=True)
    
    # Inventory tracking
    stock_quantity: int = Column(Integer, default=0, nullable=False)
    min_stock_level: int = Column(Integer, default=0, nullable=False)
    
    # Product attributes
    sku: str = Column(String(50), unique=True, nullable=False)
    barcode: Optional[str] = Column(String(100), unique=True, nullable=True)
    
    # Category (simple string for this example)
    category: str = Column(String(100), nullable=False, index=True)
    
    # Product metadata
    attributes: dict = Column(JSON, default=dict)
    
    @validates('price')
    def validate_price(self, key: str, price: Decimal) -> Decimal:
        """Validate price is positive."""
        if price <= 0:
            raise ValueError("Price must be positive")
        return price
    
    @validates('stock_quantity')
    def validate_stock(self, key: str, quantity: int) -> int:
        """Validate stock quantity is non-negative."""
        if quantity < 0:
            raise ValueError("Stock quantity cannot be negative")
        return quantity
    
    @property
    def is_low_stock(self) -> bool:
        """Check if product is low on stock."""
        return self.stock_quantity <= self.min_stock_level
    
    @property
    def profit_margin(self) -> Optional[Decimal]:
        """Calculate profit margin if cost is available."""
        if self.cost is None or self.cost == 0:
            return None
        return ((self.price - self.cost) / self.price) * 100


class Order(Base, TimestampMixin):
    """
    Order model demonstrating relationships and order states.
    """
    __tablename__ = "orders"
    
    id: int = Column(Integer, primary_key=True)
    order_number: str = Column(String(50), unique=True, nullable=False)
    
    # Foreign key to user (simplified - no relationship defined yet)
    user_id: int = Column(Integer, nullable=False, index=True)
    
    # Order details
    total_amount: Decimal = Column(DecimalField(12, 2), nullable=False)
    tax_amount: Decimal = Column(DecimalField(10, 2), default=Decimal('0.00'))
    shipping_amount: Decimal = Column(DecimalField(10, 2), default=Decimal('0.00'))
    
    # Order status
    status: str = Column(String(50), default="pending", nullable=False, index=True)
    
    # Important dates
    order_date: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    shipped_date: Optional[datetime] = Column(DateTime, nullable=True)
    delivered_date: Optional[datetime] = Column(DateTime, nullable=True)
    
    # Shipping information
    shipping_address: dict = Column(JSON, nullable=False)
    billing_address: dict = Column(JSON, nullable=False)
    
    # Order metadata
    notes: Optional[str] = Column(Text, nullable=True)
    tracking_number: Optional[str] = Column(String(100), nullable=True)
    
    @validates('status')
    def validate_status(self, key: str, status: str) -> str:
        """Validate order status."""
        valid_statuses = {
            'pending', 'confirmed', 'processing', 'shipped', 
            'delivered', 'cancelled', 'returned'
        }
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
        return status
    
    @property
    def is_completed(self) -> bool:
        """Check if order is completed."""
        return self.status in ('delivered', 'cancelled', 'returned')


async def create_tables_example():
    """Example showing how to create tables from models."""
    print("🏗️  Creating tables from models...")
    
    engine = create_engine("duckdb:///:memory:", echo=True)
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Tables created successfully")
    await engine.dispose()


async def model_creation_example():
    """Example showing model instance creation and validation."""
    print("\n👤 Creating model instances...")
    
    engine = create_engine("duckdb:///:memory:", echo=False)
    SessionLocal = sessionmaker(engine, class_=AsyncSession)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with SessionLocal() as session:
        # Create a user
        user = User(
            username="johndoe",
            email="john.doe@example.com",
            first_name="John",
            last_name="Doe",
            bio="Software developer and tech enthusiast",
            birth_date=date(1990, 5, 15),
            preferences={
                "theme": "dark",
                "notifications": True,
                "language": "en"
            }
        )
        
        print(f"👤 Created user: {user.full_name}")
        print(f"📧 Email: {user.email}")
        print(f"🆔 External ID: {user.external_id}")
        
        # Create a product
        product = Product(
            name="Premium Coffee Beans",
            description="High-quality arabica coffee beans",
            price=Decimal("24.99"),
            cost=Decimal("12.50"),
            stock_quantity=100,
            min_stock_level=10,
            sku="COFFEE-001",
            category="beverages",
            attributes={
                "origin": "Colombia",
                "roast_level": "medium",
                "weight": "1kg"
            }
        )
        
        print(f"☕ Created product: {product.name}")
        print(f"💰 Price: ${product.price}")
        print(f"📈 Profit margin: {product.profit_margin:.1f}%")
        print(f"📦 Low stock: {product.is_low_stock}")
        
        # Add to session and commit
        session.add(user)
        session.add(product)
        await session.commit()
        
        print("✅ Models saved to database")
    
    await engine.dispose()


async def validation_example():
    """Example showing model validation in action."""
    print("\n🔍 Model validation examples...")
    
    # Test valid user creation
    try:
        user = User(
            username="validuser",
            email="valid@example.com",
            first_name="Valid",
            last_name="User"
        )
        print("✅ Valid user created successfully")
    except ValueError as e:
        print(f"❌ Validation error: {e}")
    
    # Test invalid email
    try:
        user = User(
            username="testuser",
            email="invalid-email",  # No @ symbol
            first_name="Test",
            last_name="User"
        )
    except ValueError as e:
        print(f"✅ Caught expected email validation error: {e}")
    
    # Test invalid username
    try:
        user = User(
            username="ab",  # Too short
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
    except ValueError as e:
        print(f"✅ Caught expected username validation error: {e}")
    
    # Test invalid price
    try:
        product = Product(
            name="Test Product",
            price=Decimal("-10.00"),  # Negative price
            sku="TEST-001",
            category="test"
        )
    except ValueError as e:
        print(f"✅ Caught expected price validation error: {e}")


async def field_types_example():
    """Example demonstrating various field types and their behavior."""
    print("\n🔧 Field types demonstration...")
    
    engine = create_engine("duckdb:///:memory:", echo=False)
    SessionLocal = sessionmaker(engine, class_=AsyncSession)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with SessionLocal() as session:
        # Create instances with various field types
        user = User(
            username="fieldtest",
            email="fields@example.com",
            first_name="Field",
            last_name="Test",
            birth_date=date(1995, 3, 20),
            is_active=True,
            is_verified=False,
            preferences={
                "settings": {"theme": "light"},
                "features": ["feature1", "feature2"]
            }
        )
        
        session.add(user)
        await session.commit()
        
        # Refresh to get auto-generated fields
        await session.refresh(user)
        
        print(f"🆔 ID (Integer): {user.id}")
        print(f"📧 Email (String): {user.email}")
        print(f"📅 Birth Date (Date): {user.birth_date}")
        print(f"✅ Is Active (Boolean): {user.is_active}")
        print(f"🆔 External ID (UUID): {user.external_id}")
        print(f"⏰ Created At (DateTime): {user.created_at}")
        print(f"📋 Preferences (JSON): {user.preferences}")
    
    await engine.dispose()


async def main():
    """Main example runner."""
    print("🏗️  Andamios ORM Model Examples")
    print("=" * 50)
    
    await create_tables_example()
    await model_creation_example()
    await validation_example()
    await field_types_example()
    
    print("\n✨ All model examples completed successfully!")


if __name__ == "__main__":
    uvloop.run(main())