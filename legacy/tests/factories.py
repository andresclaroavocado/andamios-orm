"""
Test data factories for Andamios ORM.

This module provides factory classes for generating test data
using factory_boy. Factories create realistic test data that
can be used across different test scenarios.
"""

import factory
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, Any
from uuid import uuid4

# Import models - these will be available once implemented
# from andamios_orm.models import User, Product, Order


class UserFactory(factory.Factory):
    """Factory for creating test User instances."""
    
    # Will be set to actual User model once implemented
    # class Meta:
    #     model = User
    
    # Basic fields
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    
    # Optional fields
    bio = factory.Faker("text", max_nb_chars=200)
    avatar_url = factory.LazyAttribute(
        lambda obj: f"https://example.com/avatars/{obj.username}.jpg"
    )
    
    # Boolean fields
    is_active = True
    is_verified = factory.Faker("boolean", chance_of_getting_true=70)
    
    # Date field
    birth_date = factory.Faker(
        "date_between", 
        start_date=date(1970, 1, 1), 
        end_date=date(2005, 12, 31)
    )
    
    # UUID field
    external_id = factory.LazyFunction(uuid4)
    
    # JSON field
    preferences = factory.LazyFunction(lambda: {
        "theme": factory.Faker("random_element", elements=["light", "dark"]).generate(),
        "notifications": factory.Faker("boolean").generate(),
        "language": factory.Faker("random_element", elements=["en", "es", "fr"]).generate(),
        "timezone": factory.Faker("timezone").generate(),
    })
    
    @classmethod
    def create_admin(cls, **kwargs) -> Dict[str, Any]:
        """Create an admin user with specific permissions."""
        return cls.build(
            username="admin",
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            is_verified=True,
            preferences={
                "theme": "dark",
                "notifications": True,
                "language": "en",
                "admin_panel": True,
                "permissions": ["read", "write", "admin"]
            },
            **kwargs
        )
    
    @classmethod
    def create_inactive(cls, **kwargs) -> Dict[str, Any]:
        """Create an inactive user."""
        return cls.build(
            is_active=False,
            is_verified=False,
            **kwargs
        )


class ProductFactory(factory.Factory):
    """Factory for creating test Product instances."""
    
    # Will be set to actual Product model once implemented
    # class Meta:
    #     model = Product
    
    # Basic fields
    name = factory.Faker("catch_phrase")
    description = factory.Faker("text", max_nb_chars=500)
    
    # Decimal fields
    price = factory.LazyFunction(
        lambda: Decimal(str(factory.Faker("pydecimal", 
                                        left_digits=3, 
                                        right_digits=2, 
                                        positive=True).generate()))
    )
    cost = factory.LazyAttribute(
        lambda obj: obj.price * Decimal("0.6")  # 60% of price
    )
    
    # Inventory
    stock_quantity = factory.Faker("random_int", min=0, max=1000)
    min_stock_level = factory.LazyAttribute(
        lambda obj: max(1, obj.stock_quantity // 10)  # 10% of stock
    )
    
    # Product identifiers
    sku = factory.Sequence(lambda n: f"PROD-{n:06d}")
    barcode = factory.Sequence(lambda n: f"12345{n:07d}")
    
    # Category
    category = factory.Faker("random_element", elements=[
        "electronics", "clothing", "books", "home", "sports", 
        "toys", "automotive", "health", "beauty", "food"
    ])
    
    # Attributes
    attributes = factory.LazyFunction(lambda: {
        "brand": factory.Faker("company").generate(),
        "color": factory.Faker("color_name").generate(),
        "weight": f"{factory.Faker('random_int', min=1, max=100).generate()}g",
        "dimensions": {
            "length": factory.Faker("random_int", min=1, max=50).generate(),
            "width": factory.Faker("random_int", min=1, max=50).generate(),
            "height": factory.Faker("random_int", min=1, max=50).generate(),
        }
    })
    
    @classmethod
    def create_expensive(cls, **kwargs) -> Dict[str, Any]:
        """Create an expensive product."""
        return cls.build(
            price=Decimal("999.99"),
            cost=Decimal("500.00"),
            category="electronics",
            **kwargs
        )
    
    @classmethod
    def create_out_of_stock(cls, **kwargs) -> Dict[str, Any]:
        """Create an out-of-stock product."""
        return cls.build(
            stock_quantity=0,
            min_stock_level=5,
            **kwargs
        )
    
    @classmethod
    def create_low_stock(cls, **kwargs) -> Dict[str, Any]:
        """Create a low-stock product."""
        return cls.build(
            stock_quantity=2,
            min_stock_level=10,
            **kwargs
        )


class OrderFactory(factory.Factory):
    """Factory for creating test Order instances."""
    
    # Will be set to actual Order model once implemented
    # class Meta:
    #     model = Order
    
    # Basic fields
    order_number = factory.Sequence(lambda n: f"ORD-{n:08d}")
    user_id = factory.Faker("random_int", min=1, max=1000)
    
    # Financial fields
    total_amount = factory.LazyFunction(
        lambda: Decimal(str(factory.Faker("pydecimal",
                                        left_digits=4,
                                        right_digits=2,
                                        positive=True).generate()))
    )
    tax_amount = factory.LazyAttribute(
        lambda obj: obj.total_amount * Decimal("0.08")  # 8% tax
    )
    shipping_amount = factory.Faker("random_element", elements=[
        Decimal("0.00"), Decimal("5.99"), Decimal("9.99"), Decimal("15.99")
    ])
    
    # Status
    status = factory.Faker("random_element", elements=[
        "pending", "confirmed", "processing", "shipped", "delivered"
    ])
    
    # Dates
    order_date = factory.Faker(
        "date_time_between",
        start_date=datetime.now() - timedelta(days=30),
        end_date=datetime.now()
    )
    shipped_date = factory.LazyAttribute(
        lambda obj: obj.order_date + timedelta(days=1) if obj.status in ["shipped", "delivered"] else None
    )
    delivered_date = factory.LazyAttribute(
        lambda obj: obj.shipped_date + timedelta(days=3) if obj.status == "delivered" and obj.shipped_date else None
    )
    
    # Addresses
    shipping_address = factory.LazyFunction(lambda: {
        "name": factory.Faker("name").generate(),
        "street": factory.Faker("street_address").generate(),
        "city": factory.Faker("city").generate(),
        "state": factory.Faker("state_abbr").generate(),
        "zip_code": factory.Faker("zipcode").generate(),
        "country": "US"
    })
    
    billing_address = factory.LazyAttribute(lambda obj: obj.shipping_address.copy())
    
    # Optional fields
    notes = factory.Faker("text", max_nb_chars=100)
    tracking_number = factory.LazyAttribute(
        lambda obj: f"TRK{factory.Faker('random_int', min=1000000000, max=9999999999).generate()}" 
        if obj.status in ["shipped", "delivered"] else None
    )
    
    @classmethod
    def create_pending(cls, **kwargs) -> Dict[str, Any]:
        """Create a pending order."""
        return cls.build(
            status="pending",
            shipped_date=None,
            delivered_date=None,
            tracking_number=None,
            **kwargs
        )
    
    @classmethod
    def create_delivered(cls, **kwargs) -> Dict[str, Any]:
        """Create a delivered order."""
        order_date = datetime.now() - timedelta(days=7)
        shipped_date = order_date + timedelta(days=1)
        delivered_date = shipped_date + timedelta(days=3)
        
        return cls.build(
            status="delivered",
            order_date=order_date,
            shipped_date=shipped_date,
            delivered_date=delivered_date,
            tracking_number=f"TRK{factory.Faker('random_int', min=1000000000, max=9999999999).generate()}",
            **kwargs
        )
    
    @classmethod
    def create_large_order(cls, **kwargs) -> Dict[str, Any]:
        """Create a large order."""
        return cls.build(
            total_amount=Decimal("2500.00"),
            tax_amount=Decimal("200.00"),
            shipping_amount=Decimal("0.00"),  # Free shipping for large orders
            **kwargs
        )


# Batch factories for creating multiple related objects
class TestDataSet:
    """Factory for creating complete test datasets."""
    
    @staticmethod
    def create_ecommerce_scenario() -> Dict[str, Any]:
        """
        Create a complete e-commerce test scenario with:
        - Multiple users (admin, active, inactive)
        - Various products (different categories, stock levels)
        - Orders in different states
        """
        users = [
            UserFactory.create_admin(),
            UserFactory.build(),
            UserFactory.build(),
            UserFactory.create_inactive(),
        ]
        
        products = [
            ProductFactory.build(category="electronics"),
            ProductFactory.build(category="clothing"),
            ProductFactory.create_expensive(),
            ProductFactory.create_out_of_stock(),
            ProductFactory.create_low_stock(),
        ]
        
        orders = [
            OrderFactory.create_pending(),
            OrderFactory.create_delivered(),
            OrderFactory.create_large_order(),
            OrderFactory.build(status="processing"),
        ]
        
        return {
            "users": users,
            "products": products,
            "orders": orders,
        }
    
    @staticmethod
    def create_performance_dataset(count: int = 1000) -> Dict[str, Any]:
        """Create a large dataset for performance testing."""
        users = [UserFactory.build() for _ in range(count // 10)]
        products = [ProductFactory.build() for _ in range(count)]
        orders = [OrderFactory.build() for _ in range(count // 5)]
        
        return {
            "users": users,
            "products": products,
            "orders": orders,
        }


# Utility functions
def build_related_objects(factory_class, count: int = 5, **kwargs) -> list:
    """Build multiple objects from a factory."""
    return [factory_class.build(**kwargs) for _ in range(count)]


def create_test_user_with_orders(order_count: int = 3) -> Dict[str, Any]:
    """Create a user with associated orders."""
    user = UserFactory.build()
    orders = [
        OrderFactory.build(user_id=user.get("id", 1))
        for _ in range(order_count)
    ]
    return {"user": user, "orders": orders}