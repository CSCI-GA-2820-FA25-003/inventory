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
Test cases for Inventory Model
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
#  I N V E N T O R Y   M O D E L   T E S T   C A S E S
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
        """It should create an Inventory and verify all fields"""
        inventory = InventoryFactory()
        inventory.create()

        self.assertIsNotNone(inventory.id)

        found = Inventory.all()
        self.assertEqual(len(found), 1)

        data = Inventory.find(inventory.id)
        self.assertIsNotNone(data)

        self.assertEqual(data.name, inventory.name)
        self.assertEqual(data.quantity, inventory.quantity)
        self.assertEqual(data.category, inventory.category)
        self.assertEqual(data.available, inventory.available)
        self.assertEqual(data.sku, inventory.sku)  # new core field

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
        self.assertIn("sku", data)  # new core field
        self.assertEqual(data["sku"], inventory.sku)
        self.assertIn("description", data)
        self.assertEqual(data["description"], inventory.description)
        self.assertIn("price", data)
        self.assertEqual(
            data["price"], float(inventory.price) if inventory.price else None
        )
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
        self.assertEqual(inventory.sku, data["sku"])  # new core field
        self.assertEqual(inventory.description, data["description"])
        self.assertEqual(inventory.price, data["price"])
        # created_at/last_updated are not set via deserialize

    def test_update_a_inventory(self):
        """It should Update an Inventory"""
        inventory = InventoryFactory()
        logging.debug(inventory)
        inventory.id = None
        inventory.create()
        logging.debug(inventory)
        self.assertIsNotNone(inventory.id)
        inventory.category = "k9"
        original_id = inventory.id
        inventory.update()
        self.assertEqual(inventory.id, original_id)
        self.assertEqual(inventory.category, "k9")
        inventory = Inventory.all()
        self.assertEqual(len(inventory), 1)
        self.assertEqual(inventory[0].id, original_id)
        self.assertEqual(inventory[0].category, "k9")

    def test_update_no_id(self):
        """It should not Update an Inventory with no id"""
        inventory = InventoryFactory()
        logging.debug(inventory)
        inventory.id = None
        self.assertRaises(DataValidationError, inventory.update)
