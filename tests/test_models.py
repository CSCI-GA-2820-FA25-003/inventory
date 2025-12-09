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
import logging
import os
from unittest import TestCase
from unittest.mock import patch

from service.models import DataValidationError, Inventory, db
from wsgi import app

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

    def test_list_all_inventory(self):
        """It should List all Inventory in the database"""
        inventory = Inventory.all()
        self.assertEqual(inventory, [])
        # Create 5 Inventory
        for _ in range(5):
            inventory1 = InventoryFactory()
            inventory1.create()
        # See if we get back 5 inventory
        inventory = Inventory.all()
        self.assertEqual(len(inventory), 5)

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

    def test_repr(self):
        """It should return a string representation of the inventory"""
        inventory = InventoryFactory()
        expected = f"<Inventory {inventory.name} id=[{inventory.id}]>"
        self.assertEqual(repr(inventory), expected)

    def test_create_inventory_with_error(self):
        """It should raise DataValidationError when create() fails"""
        inventory1 = InventoryFactory(sku="DUPLICATE")
        inventory1.create()
        inventory2 = InventoryFactory(sku="DUPLICATE")  # violates unique constraint
        with self.assertRaises(DataValidationError):
            inventory2.create()

    def test_update_inventory_with_error(self):
        """It should raise DataValidationError when update() fails"""
        inventory = InventoryFactory()
        inventory.create()
        with patch(
            "service.models.db.session.commit", side_effect=Exception("DB error")
        ):
            with self.assertRaises(DataValidationError):
                inventory.update()

    def test_delete_inventory_with_error(self):
        """It should raise DataValidationError when delete() fails"""
        inventory = InventoryFactory()
        inventory.create()
        with patch.object(db.session, "delete", side_effect=Exception("DB error")):
            with self.assertRaises(DataValidationError):
                inventory.delete()

    def test_deserialize_with_exceptions(self):
        """Cover KeyError, AttributeError, and TypeError branches in deserialize()"""
        inventory = Inventory()

        # KeyError: missing required keys (e.g., sku, quantity)
        with self.assertRaises(DataValidationError):
            inventory.deserialize({"name": "item"})

        # AttributeError: object supports indexing (data["name"]) but has no .get()
        class NoGet:  # pylint: disable=too-few-public-methods
            """Simple mapping-like object missing .get()"""

            def __init__(self, d):
                self._d = d

            def __getitem__(self, key):
                return self._d[key]

        bad_mapping = NoGet({"name": "n", "sku": "s", "quantity": 1})
        with self.assertRaises(DataValidationError) as cm:
            inventory.deserialize(bad_mapping)
        self.assertIn("Invalid attribute", str(cm.exception))

        # TypeError: completely invalid type (e.g., None)
        with self.assertRaises(DataValidationError):
            inventory.deserialize(None)

    def test_find_by_availability_with_invalid_type(self):
        """It should raise TypeError when availability is not boolean"""
        with self.assertRaises(TypeError):
            Inventory.find_by_availability("yes")

    def test_read_a_inventory(self):
        """It should Read an Inventory"""
        inventory = InventoryFactory()
        logging.debug(inventory)
        inventory.id = None
        inventory.create()
        self.assertIsNotNone(inventory.id)
        # Fetch it back
        found_inventory = Inventory.find(inventory.id)
        self.assertEqual(found_inventory.id, inventory.id)
        self.assertEqual(found_inventory.name, inventory.name)
        self.assertEqual(found_inventory.category, inventory.category)

    def test_delete_a_inventory(self):
        """It should Delete a Inventory"""
        inventory = InventoryFactory()
        inventory.create()
        self.assertEqual(len(Inventory.all()), 1)
        # delete the inventory and make sure it isn't in the database
        inventory.delete()
        self.assertEqual(len(Inventory.all()), 0)


######################################################################
#  Q U E R Y   T E S T   C A S E S
######################################################################
class TestModelQueries(TestInventory):
    """Inventory Model Query Tests"""

    def test_find_inventory(self):
        """It should Find a Inventory by ID"""
        inventorys = InventoryFactory.create_batch(5)
        for inventory in inventorys:
            inventory.create()
        logging.debug(inventorys)
        # make sure they got saved
        self.assertEqual(len(Inventory.all()), 5)
        # find the 2nd inventory in the list
        inventory = Inventory.find(inventorys[1].id)
        self.assertIsNot(inventory, None)
        self.assertEqual(inventory.id, inventorys[1].id)
        self.assertEqual(inventory.name, inventorys[1].name)
        self.assertEqual(inventory.available, inventorys[1].available)

    def test_find_by_category(self):
        """It should Find Inventory by Category"""
        inventorys = InventoryFactory.create_batch(10)
        for inventory in inventorys:
            inventory.create()
        category = inventorys[0].category
        count = len(
            [inventory for inventory in inventorys if inventory.category == category]
        )
        found = Inventory.find_by_category(category)
        self.assertEqual(found.count(), count)
        for inventory in found:
            self.assertEqual(inventory.category, category)

    def test_find_by_name(self):
        """It should Find a Inventory by Name"""
        inventorys = InventoryFactory.create_batch(10)
        for inventory in inventorys:
            inventory.create()
        name = inventorys[0].name
        count = len([inventory for inventory in inventorys if inventory.name == name])
        found = Inventory.find_by_name(name)
        self.assertEqual(found.count(), count)
        for inventory in found:
            self.assertEqual(inventory.name, name)

    def test_find_by_availability(self):
        """It should Find Inventory by Availability"""
        inventorys = InventoryFactory.create_batch(10)
        for inventory in inventorys:
            inventory.create()
        available = inventorys[0].available
        count = len(
            [inventory for inventory in inventorys if inventory.available == available]
        )
        found = Inventory.find_by_availability(available)
        self.assertEqual(found.count(), count)
        for inventory in found:
            self.assertEqual(inventory.available, available)
