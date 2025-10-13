"""
Test Factory to make fake objects for testing
"""

import factory

# from faker import Faker
from service.models import Inventory
from datetime import datetime
import random


class InventoryFactory(factory.Factory):
    """Creates fake pets that you don't have to feed"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Inventory

    id = factory.Sequence(lambda n: n + 1 )
    name = factory.Faker("word")  # or "sentence" if you want multi-word names
    quantity = factory.LazyFunction(lambda: random.randint(1, 100))
    category = factory.LazyFunction(
        lambda: random.choice(
            ["Shoes", "Clothing", "Accessories", "Sports", "Electronics"]
        )
    )
    available = factory.LazyFunction(lambda: random.choice([True, False]))
    created_at = factory.LazyFunction(datetime.utcnow)
    last_updated = factory.LazyFunction(datetime.utcnow)
