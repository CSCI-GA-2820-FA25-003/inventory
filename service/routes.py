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
#####################################################################

"""
Inventory Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Inventory
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Inventory
from service.common import status  # HTTP Status Codes
from flask import render_template


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    # return (
    #     "Reminder: return some useful information in json format about the service here",
    #     status.HTTP_200_OK,
    # )

    return (
        jsonify(
            name="Inventory Demo REST API Service",
            version="1.0",
            paths=url_for("list_inventory", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
# CREATE A NEW INVENTORY ITEM
######################################################################
@app.route("/inventory", methods=["POST"])
def create_inventory():
    """
    Create a Inventory
    This endpoint will create a Inventory based the data in the body that is posted
    """
    app.logger.info("Request to Create a Inventory...")
    check_content_type("application/json")

    inventory = Inventory()
    # Get the data from the request and deserialize it
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    inventory.deserialize(data)

    # Save the new Inventory to the database
    inventory.create()
    app.logger.info("Inventory with new id [%s] saved!", inventory.id)

    # Return the location of the new Inventory
    #  To Do : Uncomment when implementing get_inventory
    location_url = url_for("get_inventory", inventory_id=inventory.id, _external=True)
    return (
        jsonify(inventory.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


######################################################################
# READ AN INVENTORY
######################################################################
@app.route("/inventory/<int:inventory_id>", methods=["GET"])
def get_inventory(inventory_id):
    """
    Retrieve a single Inventory
    This endpoint will return a Inventory based on it's id
    """
    app.logger.info("Request to Retrieve a Inventory with id [%s]", inventory_id)

    # Attempt to find the Inventory and abort if not found
    inventory = Inventory.find(inventory_id)
    if not inventory:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Inventory with id '{inventory_id}' was not found.",
        )

    app.logger.info("Returning inventory: %s", inventory.name)
    return jsonify(inventory.serialize()), status.HTTP_200_OK


######################################################################
# Checks the ContentType of a request
######################################################################
def check_content_type(content_type) -> None:
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )


######################################################################
# UPDATE AN EXISTING INVENTORY
######################################################################
@app.route("/inventory/<int:inventory_id>", methods=["PUT"])
def update_inventory(inventory_id):
    """
    Update an Inventory

    This endpoint will update an Inventory based the body that is posted
    """
    app.logger.info("Request to Update an inventory with id [%s]", inventory_id)
    check_content_type("application/json")

    # Attempt to find the Inventory and abort if not found
    inventory = Inventory.find(inventory_id)
    if not inventory:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Inventory with id '{inventory_id}' was not found.",
        )

    # Update the Inventory with the new data
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    inventory.deserialize(data)

    # Save the updates to the database
    inventory.update()

    app.logger.info("Inventory with ID: %d updated.", inventory.id)
    return jsonify(inventory.serialize()), status.HTTP_200_OK


######################################################################
# DELETE AN INVENTORY
######################################################################
@app.route("/inventory/<int:inventory_id>", methods=["DELETE"])
def delete_inventory(inventory_id):
    """
    Delete a Inventory

    This endpoint will delete a Inventory based the id specified in the path
    """
    app.logger.info("Request to Delete a inventory with id [%s]", inventory_id)

    # Delete the Inventory if it exists
    inventory = Inventory.find(inventory_id)
    if inventory:
        app.logger.info("Inventory with ID: %d found.", inventory.id)
        inventory.delete()

    app.logger.info("Inventory with ID: %d delete complete.", inventory_id)
    return {}, status.HTTP_204_NO_CONTENT


######################################################################
# LIST ALL INVENTORY
######################################################################
@app.route("/inventory", methods=["GET"])
def list_inventory():
    """Returns all of the Inventory"""
    app.logger.info("Request for item list")

    inventory = []

    # Parse any arguments from the query string
    category = request.args.get("category")
    name = request.args.get("name")
    available = request.args.get("available")

    if category:
        app.logger.info("Find by category: %s", category)
        inventory = Inventory.find_by_category(category)
    elif name:
        app.logger.info("Find by name: %s", name)
        inventory = Inventory.find_by_name(name)
    elif available:
        app.logger.info("Find by available: %s", available)
        # create bool from string
        available_value = available.lower() in ["true", "yes", "1"]
        inventory = Inventory.find_by_availability(available_value)
    else:
        app.logger.info("Find all")
        inventory = Inventory.all()

    results = [item.serialize() for item in inventory]
    app.logger.info("Returning %d inventory", len(results))
    return jsonify(results), status.HTTP_200_OK


######################################################################
# PURCHASE A Inventory
######################################################################
@app.route("/inventory/<int:pet_id>/purchase", methods=["PUT"])
def purchase_pets(pet_id):
    """Purchasing a Inventory makes it unavailable"""
    app.logger.info("Request to purchase inventory with id: %d", pet_id)

    # Attempt to find the Inventory and abort if not found
    inventory = Inventory.find(pet_id)
    if not inventory:
        abort(status.HTTP_404_NOT_FOUND, f"Inventory with id '{pet_id}' was not found.")

    # you can only purchase inventory that are available
    if not inventory.available:
        abort(
            status.HTTP_409_CONFLICT,
            f"Inventory with id '{pet_id}' is not available.",
        )

    # At this point you would execute code to purchase the inventory
    # For the moment, we will just set them to unavailable

    inventory.available = False
    inventory.update()

    app.logger.info("Inventory with ID: %d has been purchased.", pet_id)
    return inventory.serialize(), status.HTTP_200_OK


######################################################################
# Kubernetes probes health endpoint
######################################################################
@app.route("/health", methods=["GET"])
def health():
    """Kubernetes probes health endpoint"""
    return {"status": "OK"}, 200


######################################################################
# BDD/UI additions
######################################################################
def err(msg):
    """Helper to return uniform 400 responses"""
    return (
        jsonify(
            status=status.HTTP_400_BAD_REQUEST,
            error="Bad Request",
            message=msg,
        ),
        status.HTTP_400_BAD_REQUEST,
    )


@app.route("/inventories", methods=["POST"])
def create_inventory_v2():
    """Create a new inventory item with validation and return it."""
    check_content_type("application/json")
    data = request.get_json() or {}

    name = data.get("name")
    if not name:
        return err("name is required")

    sku = data.get("sku")
    if not sku:
        return err("sku is required")

    # Quantity
    try:
        qty = int(data.get("quantity"))
        if qty < 0:
            return err("quantity must be an integer >= 0")
    except Exception:
        return err("quantity must be an integer")

    # Price (optional)
    price = data.get("price")
    if price is not None:
        try:
            price = float(price)
            if price < 0:
                return err("price must be >= 0")
        except Exception:
            return err("price must be a number")

    # Restock Level (optional)
    restock = data.get("restock_level")
    if restock is not None:
        try:
            restock = int(restock)
            if restock < 0:
                return err("restock_level must be >= 0")
        except Exception:
            return err("restock_level must be an integer")

    # SKU uniqueness
    if Inventory.query.filter(Inventory.sku == sku).first():
        return jsonify(error=f"SKU '{sku}' already exists"), status.HTTP_409_CONFLICT

    # Create item
    inv = Inventory(
        name=name,
        sku=sku,
        quantity=qty,
        price=price,
        category=data.get("category"),
        description=data.get("description"),
        available=bool(data.get("available", True)),
        restock_level=restock,
    )
    inv.create()

    return (
        jsonify(inv.serialize()),
        status.HTTP_201_CREATED,
        {"Location": f"/inventories/{inv.id}"},
    )


@app.route("/inventories/<int:inventory_id>", methods=["GET"])
def get_inventory_v2(inventory_id: int):
    """Fetch a single inventory item by id."""
    inv = Inventory.query.get(inventory_id)
    if not inv:
        return jsonify(error="Not Found"), status.HTTP_404_NOT_FOUND
    return jsonify(inv.serialize()), status.HTTP_200_OK


@app.route("/inventories/new", methods=["GET"])
def new_inventory_page():
    """Render the Create Inventory form page."""
    return render_template("inventory.html")


######################################################################
# GET RESTOCK STATUS FOR AN INVENTORY ITEM
######################################################################
@app.route("/inventory/<int:inventory_id>/restock-status", methods=["GET"])
def get_restock_status(inventory_id):
    """
    Returns the stock status for an inventory item.
    'stock sufficient', 'stock insufficient', or 'undefined'
    """
    app.logger.info("Request to get restock status for inventory [%s]", inventory_id)

    inventory = Inventory.find(inventory_id)
    if not inventory:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Inventory with id '{inventory_id}' was not found.",
        )

    return (
        jsonify(
            {
                "id": inventory.id,
                "stock_status": inventory.stock_status,
                "quantity": inventory.quantity,
                "restock_level": inventory.restock_level,
            }
        ),
        status.HTTP_200_OK,
    )
