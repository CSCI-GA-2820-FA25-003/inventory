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
YourResourceModel Service

This service implements a REST API that allows you to Create, Read, Update
and Delete YourResourceModel
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Inventory
from service.common import status  # HTTP Status Codes


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
# Inventory Service Routes
######################################################################


######################################################################
# CREATE A NEW Inventory #need to rewrite
######################################################################
@app.route("/inventory", methods=["POST"])
def create_inventory():
    """
    Create an Inventory
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
    # location_url = url_for("get_inventory", inventory_id=inventory.id, _external=True)
    location_url = "unknown"

    return (
        jsonify(inventory.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


######################################################################
# UPDATE AN EXISTING PET #need to rewrite
######################################################################
@app.route("/inventory/<int:inventory_id>", methods=["PUT"])
def update_inventory(inventory_id):
    """
    Update a Inventory

    This endpoint will update a Inventory based the body that is posted
    """
    app.logger.info("Request to Update a inventory with id [%s]", inventory_id)
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
# DELETE A PET #need to rewrite
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
