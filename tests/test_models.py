######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Test cases for Pet Model
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.models import Product, DataValidationError, db
from .factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
# I V E N T O R Y   P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProduct(TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    # I V E N T O R Y  T E S T   C A S E S
    ######################################################################

    def test_create_product(self):
        """It should create a Product and verify all fields"""
        # Arrange: create a fake product using the factory
        product = ProductFactory()

        # Act: save it to the database
        product.create()

        # Assert: verify product was created and retrievable
        self.assertIsNotNone(product.id)

        found = Product.all()
        self.assertEqual(len(found), 1)

        data = Product.find(product.id)
        self.assertIsNotNone(data)

        # Check each field matches
        self.assertEqual(data.name, product.name)
        self.assertEqual(data.quantity, product.quantity)
        self.assertEqual(data.category, product.category)
        self.assertEqual(data.available, product.available)

        # Timestamps should exist and be datetime objects
        self.assertIsNotNone(data.created_at)
        self.assertIsNotNone(data.last_updated)
        self.assertLessEqual(data.created_at, data.last_updated)

    def test_update_product(self):
        """It should update a Product and persist changes"""
        # Arrange. create and save old data
        product = ProductFactory()
        product.create()
        self.assertIsNotNone(product.id)
        old_name = product.name
        old_qty = product.quantity
        old_cat = product.category
        old_avail = product.available

        # Act. change and use update to write into db
        product.name = f"Updated {old_name}"
        product.quantity = old_qty + 5
        product.category = f"{old_cat}-UPDATED"
        product.available = not old_avail
        product.update()  # use update to write into db

        # Assert. search in db
        found = Product.find(product.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.name, f"Updated {old_name}")
        self.assertEqual(found.quantity, old_qty + 5)
        self.assertEqual(found.category, f"{old_cat}-UPDATED")
        self.assertEqual(found.available, (not old_avail))

        if hasattr(found, "created_at") and hasattr(found, "last_updated"):
            self.assertGreaterEqual(found.last_updated, found.created_at)

        self.assertEqual(len(Product.all()), 1)

    def test_delete_product(self):
        """It should delete a Product"""
        # Arrange
        product = ProductFactory()
        product.create()
        self.assertEqual(len(Product.all()), 1)

        # Act
        product.delete()

        # Assert
        self.assertEqual(len(Product.all()), 0)  # check if it equals to 0
        self.assertIsNone(Product.find(product.id))

    def test_serialize_and_deserialize_product(
        self,
    ):  # check if the product and the dictionary correctness,make sure when object come back from jason/dict, it wont miss any data and cause chaos
        """It should serialize to a dict and deserialize back"""
        # Arrange
        original = ProductFactory()
        original.create()

        # Act: serialize -> dict
        data = original.serialize()
        self.assertIsInstance(data, dict)

        clone = Product()
        clone.deserialize(data)

        # Assert
        self.assertEqual(clone.name, original.name)
        self.assertEqual(clone.quantity, original.quantity)
        self.assertEqual(clone.category, original.category)
        self.assertEqual(clone.available, original.available)
        self.assertEqual(clone.created_at, original.created_at)
        self.assertEqual(clone.last_updated, original.last_updated)

    def test_deserialize_missing_field_raises(self):
        """It should raise DataValidationError when a required field is missing"""
        from service.models import DataValidationError

        product = Product()

        bad = {
            # "name": missing on purpose
            "quantity": 1,
            "category": "Cat",
            "available": True,
            "created_at": ProductFactory().created_at,
            "last_updated": ProductFactory().last_updated,
        }
        with self.assertRaises(DataValidationError):
            product.deserialize(bad)
