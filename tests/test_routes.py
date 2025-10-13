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
Testinventory API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Inventory
from .factories import InventoryFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/inventory"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestYourResourceService(TestCase):
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
    def test_create_Inventory(self):
        """It should Create a new Inventory"""
        test_Inventory = InventoryFactory()
        logging.debug("Test Inventory: %s", test_Inventory.serialize())
        response = self.client.post(BASE_URL, json=test_Inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_inventory = response.get_json()
        self.assertEqual(new_inventory["id"], test_inventory.id)
        self.assertEqual(new_inventory["name"], test_inventory.name)
        self.assertEqual(new_inventory["quantity"], test_inventory.quantity)
        self.assertEqual(new_inventory["category"], test_inventory.gender.category)
        self.assertEqual(new_inventory["available"], test_inventory.gender.available)
        self.assertEqual(new_inventory["created_at"], test_inventory.gender.created_at)
        self.assertEqual(new_inventory["last_updated"], test_inventory.gender.last_updated)

        # Check that the location header was correct
        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_inventory = response.get_json()
        self.assertEqual(new_inventory["id"], test_inventory.id)
        self.assertEqual(new_inventory["name"], test_inventory.name)
        self.assertEqual(new_inventory["quantity"], test_inventory.quantity)
        self.assertEqual(new_inventory["category"], test_inventory.gender.category)
        self.assertEqual(new_inventory["available"], test_inventory.gender.available)
        self.assertEqual(new_inventory["created_at"], test_inventory.gender.created_at)
        self.assertEqual(new_inventory["last_updated"], test_inventory.gender.last_updated)

        
        new_Inventory = response.get_json()
        self.assertEqual(new_Inventory["name"], test_Inventory.name)
        self.assertEqual(new_Inventory["category"], test_Inventory.category)
        self.assertEqual(new_Inventory["available"], test_Inventory.available)
        self.assertEqual(new_Inventory["gender"], test_Inventory.gender.name)

        # Check that the location header was correct
        # todo : umcommment this code when get_inventory is implemented
        # response = self.client.get(location)
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # new_Inventory = response.get_json()
        # self.assertEqual(new_Inventory["name"], test_Inventory.name)
        # self.assertEqual(new_Inventory["category"], test_Inventory.category)
        # self.assertEqual(new_Inventory["available"], test_Inventory.available)
        # self.assertEqual(new_Inventory["gender"], test_Inventory.gender.name)

    # ----------------------------------------------------------
    # TEST UPDATE
    # ----------------------------------------------------------
    def test_update_Inventory(self):
        """It should Update an existing Inventory"""
        # create a Inventory to update
        test_Inventory = InventoryFactory()
        response = self.client.post(BASE_URL, json=test_Inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the Inventory
        new_Inventory = response.get_json()
        logging.debug(new_Inventory)
        new_Inventory["category"] = "unknown"
        response = self.client.put(
            f"{BASE_URL}/{new_Inventory['id']}", json=new_Inventory
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_Inventory = response.get_json()
        self.assertEqual(updated_Inventory["category"], "unknown")

    # ----------------------------------------------------------
    # TEST DELETE
    # ----------------------------------------------------------
    def test_delete_Inventory(self):
        """It should Delete a Inventory"""
        test_Inventory = self._create_Inventorys(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_Inventory.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted
        response = self.client.get(f"{BASE_URL}/{test_Inventory.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_non_existing_Inventory(self):
        """It should Delete a Inventory even if it doesn't exist"""
        response = self.client.delete(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
