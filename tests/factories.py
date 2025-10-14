"""
Test Factory to make fake objects for testing
"""

import factory

# from faker import Faker
from service.models import Inventory
from datetime import datetime
import random


class InventoryFactory(factory.Factory):
    """Creates fake inventory items"""

    class Meta:
        """Maps factory to data model"""

        model = Inventory

    id = factory.Sequence(lambda n: n + 1)
    name = factory.Faker("word")
    category = factory.LazyFunction(
        lambda: random.choice(
            ["Shoes", "Clothing", "Accessories", "Sports", "Electronics"]
        )
    )
    description = factory.Faker("sentence")
    sku = factory.Sequence(lambda n: f"SKU-{n+1000}")
    quantity = factory.LazyFunction(lambda: random.randint(1, 100))
    price = factory.LazyFunction(lambda: round(random.uniform(10, 500), 2))
    available = factory.LazyFunction(lambda: random.choice([True, False]))
    created_at = factory.LazyFunction(datetime.utcnow)
    last_updated = factory.LazyFunction(datetime.utcnow)
