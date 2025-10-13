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
from service.models import Inventory, DataValidationError, db
from .factories import InventoryFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestInventory(TestCase):
    """Test Cases for Inventory Model"""

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
        db.session.query(Inventory).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_inventory(self):
        """It should create a Inventory and verify all fields"""
        # Arrange: create a fake inventory using the factory
        inventory = InventoryFactory()

        # Act: save it to the database
        inventory.create()

        # Assert: verify inventory was created and retrievable
        self.assertIsNotNone(inventory.id)

        found = Inventory.all()
        self.assertEqual(len(found), 1)

        data = Inventory.find(inventory.id)
        self.assertIsNotNone(data)

        # Check each field matches
        self.assertEqual(data.name, inventory.name)
        self.assertEqual(data.quantity, inventory.quantity)
        self.assertEqual(data.category, inventory.category)
        self.assertEqual(data.available, inventory.available)

        # Timestamps should exist and be datetime objects
        self.assertIsNotNone(data.created_at)
        self.assertIsNotNone(data.last_updated)
        self.assertLessEqual(data.created_at, data.last_updated)

    def test_serialize_an_inventory(self):
        """It should serialize an Inventory"""
        inventory = InventoryFactory()
        data = inventory.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], inventory.id)
        self.assertIn("name", data)
        self.assertEqual(data["name"], inventory.name)
        self.assertIn("quantity", data)
        self.assertEqual(data["quantity"], inventory.quantity)
        self.assertIn("category", data)
        self.assertEqual(data["category"], inventory.category)
        self.assertIn("available", data)
        self.assertEqual(data["available"], inventory.available)
        self.assertIn("created_at", data)
        self.assertEqual(data["created_at"], inventory.created_at)
        self.assertIn("last_updated", data)
        self.assertEqual(data["last_updated"], inventory.last_updated)

    def test_deserialize_an_inventory(self):
        """It should de-serialize an Inventory"""
        data = InventoryFactory().serialize()
        inventory = Inventory()
        inventory.deserialize(data)
        self.assertNotEqual(inventory, None)
        self.assertEqual(inventory.id, None)
        self.assertEqual(inventory.name, data["name"])
        self.assertEqual(inventory.quantity, data["quantity"])
        self.assertEqual(inventory.category, data["category"])
        self.assertEqual(inventory.available, data["available"])
        self.assertEqual(inventory.created_at, data["created_at"])
        self.assertEqual(inventory.last_updated, data["last_updated"])
