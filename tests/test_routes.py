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
TestInventory API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Inventory
from .factories import InventoryFactory
from urllib.parse import quote_plus
from service.routes import check_content_type

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/inventory"

######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods


class TestInventory(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Inventory).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ############################################################
    # Utility function to bulk create inventorys
    ############################################################
    def _create_inventory(self, count: int = 1) -> list:
        """Factory method to create inventory in bulk"""
        inventory = []
        for _ in range(count):
            test_inventory = InventoryFactory()
            response = self.client.post(BASE_URL, json=test_inventory.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test inventory",
            )
            new_inventory = response.get_json()
            test_inventory.id = new_inventory["id"]
            inventory.append(test_inventory)
        return inventory

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # ----------------------------------------------------------
    # TEST CREATE
    # ----------------------------------------------------------
    # id, name, quantity, category, available, created_at, and last_updated

    def test_create_inventory(self):
        """It should Create a new Inventory"""
        test_inventory = InventoryFactory()
        logging.debug("Test Inventory: %s", test_inventory.serialize())
        response = self.client.post(BASE_URL, json=test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_inventory = response.get_json()
        self.assertEqual(new_inventory["name"], test_inventory.name)
        self.assertEqual(new_inventory["category"], test_inventory.category)
        self.assertEqual(new_inventory["available"], test_inventory.available)
        self.assertEqual(new_inventory["quantity"], test_inventory.quantity)
        self.assertEqual(new_inventory["sku"], test_inventory.sku)  # new core field
        self.assertEqual(new_inventory["description"], test_inventory.description)
        self.assertEqual(
            new_inventory["price"],
            float(test_inventory.price) if test_inventory.price else None,
        )

        # optional checks
        self.assertIn("id", new_inventory)
        self.assertIsInstance(new_inventory["id"], int)
        self.assertGreater(new_inventory["id"], 0)

        self.assertIn("created_at", new_inventory)
        self.assertIn("last_updated", new_inventory)
        self.assertIsInstance(new_inventory["created_at"], str)
        self.assertIsInstance(new_inventory["last_updated"], str)
        self.assertTrue(len(new_inventory["created_at"]) > 0)
        self.assertTrue(len(new_inventory["last_updated"]) > 0)

        # To Do: Uncomment after get_inventory is implemented
        # Check that the location header was correct
        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_inventory = response.get_json()
        self.assertEqual(new_inventory["name"], test_inventory.name)
        self.assertEqual(new_inventory["category"], test_inventory.category)
        self.assertEqual(new_inventory["available"], test_inventory.available)
        self.assertEqual(new_inventory["quantity"], test_inventory.quantity)
        self.assertEqual(new_inventory["sku"], test_inventory.sku)  # new core field
        self.assertEqual(new_inventory["description"], test_inventory.description)
        self.assertEqual(
            new_inventory["price"],
            float(test_inventory.price) if test_inventory.price else None,
        )

        # optional checks
        self.assertIn("id", new_inventory)
        self.assertIsInstance(new_inventory["id"], int)
        self.assertGreater(new_inventory["id"], 0)

    def test_update_inventory(self):
        """It should Update an existing Inventory"""
        # create an inventory to update
        test_inventory = InventoryFactory()
        response = self.client.post(BASE_URL, json=test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the inventory
        new_inventory = response.get_json()
        logging.debug(new_inventory)
        new_inventory["category"] = "unknown"
        new_inventory["sku"] = test_inventory.sku  # ensure SKU present
        response = self.client.put(
            f"{BASE_URL}/{new_inventory['id']}", json=new_inventory
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_inventory = response.get_json()
        self.assertEqual(updated_inventory["category"], "unknown")
        self.assertEqual(updated_inventory["sku"], test_inventory.sku)

    # ----------------------------------------------------------
    # TEST READ
    # ----------------------------------------------------------
    def test_get_inventory(self):
        """It should Get a single Inventory"""
        # get the id of an inventory
        test_inventory = self._create_inventory(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_inventory.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], test_inventory.name)

    def test_get_inventory_not_found(self):
        """It should not Get a inventory thats not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    # ----------------------------------------------------------
    # TEST DELETE
    # ----------------------------------------------------------
    def test_delete_inventory(self):
        """It should Delete an Inventory"""
        test_inventory = self._create_inventory(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_inventory.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted
        response = self.client.get(f"{BASE_URL}/{test_inventory.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_non_existing_inventory(self):
        """It should Delete an Inventory even if it doesn't exist"""
        response = self.client.delete(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)

    # ----------------------------------------------------------
    # TEST LIST
    # ----------------------------------------------------------
    def test_get_inventory_list(self):
        """It should Get a list of Inventory"""
        self._create_inventory(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    # ----------------------------------------------------------
    # TEST QUERY
    # ----------------------------------------------------------
    def test_query_by_name(self):
        """It should Query Pets by name"""
        inventory = self._create_inventory(5)
        test_name = inventory[0].name
        name_count = len(
            [inventory1 for inventory1 in inventory if inventory1.name == test_name]
        )
        response = self.client.get(
            BASE_URL, query_string=f"name={quote_plus(test_name)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), name_count)
        # check the data just to be sure
        for inventory1 in data:
            self.assertEqual(inventory1["name"], test_name)

    def test_query_inventory1_list_by_category(self):
        """It should Query Pets by Category"""
        inventory = self._create_inventory(10)
        test_category = inventory[0].category
        category_inventory = [
            inventory1
            for inventory1 in inventory
            if inventory1.category == test_category
        ]
        response = self.client.get(
            BASE_URL, query_string=f"category={quote_plus(test_category)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), len(category_inventory))
        # check the data just to be sure
        for inventory1 in data:
            self.assertEqual(inventory1["category"], test_category)

    def test_query_by_availability(self):
        """It should Query Pets by availability"""
        inventory = self._create_inventory(10)
        available_inventory = [
            inventory1 for inventory1 in inventory if inventory1.available is True
        ]
        unavailable_inventory = [
            inventory1 for inventory1 in inventory if inventory1.available is False
        ]
        available_count = len(available_inventory)
        unavailable_count = len(unavailable_inventory)
        logging.debug("Available Pets [%d] %s", available_count, available_inventory)
        logging.debug(
            "Unavailable Pets [%d] %s", unavailable_count, unavailable_inventory
        )

        # test for available
        response = self.client.get(BASE_URL, query_string="available=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), available_count)
        # check the data just to be sure
        for inventory1 in data:
            self.assertEqual(inventory1["available"], True)

        # test for unavailable
        response = self.client.get(BASE_URL, query_string="available=false")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), unavailable_count)
        # check the data just to be sure
        for inventory1 in data:
            self.assertEqual(inventory1["available"], False)

    def test_check_content_type_invalid_and_missing(self):
        """It should abort if Content-Type is missing or invalid"""

        # Missing Content-Type
        with app.test_request_context("/", headers={}):
            with self.assertRaises(Exception) as context:
                check_content_type("application/json")
            self.assertIn(
                str(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE), str(context.exception)
            )

        # Invalid Content-Type
        with app.test_request_context("/", headers={"Content-Type": "text/plain"}):
            with self.assertRaises(Exception) as context:
                check_content_type("application/json")
            self.assertIn(
                str(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE), str(context.exception)
            )

    def test_update_inventory_not_found(self):
        """It should return 404 if inventory is not found"""
        from service.common import status

        with app.test_client() as client:
            response = client.put(
                "/inventory/999",
                json={"name": "Test", "sku": "XYZ123", "quantity": 10},
                headers={"Content-Type": "application/json"},
            )
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
