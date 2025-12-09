######################################################################
# Copyright 2016, 2024 John J. Rofrano
# Licensed under the Apache License, Version 2.0
######################################################################

"""
Inventory Service using Flask-RESTX + Swagger

Refactored from plain Flask routes to RESTX Resource classes.
"""

from flask import current_app as app
from flask_restx import Api, Resource, fields, reqparse, inputs
from flask import request


from service.models import Inventory
from service.common import status

######################################################################
# RESTX API Setup (Professor-style)
######################################################################

api = Api(
    app,
    version="1.0.0",
    title="Inventory REST API Service",
    description="Inventory service with Swagger documentation.",
    doc="/apidocs",
    prefix="/api",
)


######################################################################
# Index (UI)
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return app.send_static_file("index.html")


@app.route("/inventory/new")
def new_inventory_form():
    """Render the HTML form for BDD tests"""
    return app.send_static_file("index.html")


######################################################################
# Health Check
######################################################################


@app.route("/health", methods=["GET"])
def health():
    return {"status": "OK"}, 200


######################################################################
# Swagger Models
######################################################################

inventory_create_model = api.model(
    "InventoryCreate",
    {
        "name": fields.String(required=True, description="Inventory item name"),
        "sku": fields.String(required=True, description="Unique SKU"),
        "quantity": fields.Integer(required=True, description="Quantity on hand"),
        "category": fields.String(description="Category of item"),
        "description": fields.String(description="Description"),
        "price": fields.Float(description="Price in USD"),
        "available": fields.Boolean(description="Item available?"),
        "restock_level": fields.Integer(description="Restock threshold"),
    },
)

inventory_model = api.inherit(
    "Inventory",
    inventory_create_model,
    {
        "id": fields.Integer(readOnly=True),
        "stock_status": fields.String(),
        "created_at": fields.DateTime(description="Created timestamp"),
        "last_updated": fields.DateTime(description="Last updated timestamp"),
    },
)

######################################################################
# Argument Parser (Query Filters)
######################################################################

inventory_args = reqparse.RequestParser()
inventory_args.add_argument("name", type=str, location="args")
inventory_args.add_argument("category", type=str, location="args")
inventory_args.add_argument("available", type=inputs.boolean, location="args")

######################################################################
# Helper: JSON Error Handler
######################################################################


def abort(code, message):
    """Return JSON errors in RESTX format"""
    app.logger.error(message)
    api.abort(code, message)


######################################################################
# /api/inventory/<id>
######################################################################


@api.route("/inventory/<int:inventory_id>")
@api.param("inventory_id", "The Inventory identifier")
class InventoryResource(Resource):
    """Handles a single Inventory item"""

    @api.marshal_with(inventory_model)
    @api.response(404, "Inventory not found")
    def get(self, inventory_id):
        """Retrieve a single Inventory"""
        inv = Inventory.find(inventory_id)
        if not inv:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Inventory with id {inventory_id} was not found",
            )
        return inv.serialize(), status.HTTP_200_OK

    @api.expect(inventory_create_model)
    @api.marshal_with(inventory_model)
    @api.response(400, "Invalid request")
    @api.response(404, "Inventory not found")
    def put(self, inventory_id):
        """Update an existing Inventory"""
        inv = Inventory.find(inventory_id)
        if not inv:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Inventory with id {inventory_id} not found.",
            )

        data = api.payload
        inv.deserialize(data)
        inv.update()
        return inv.serialize(), status.HTTP_200_OK

    @api.response(204, "Inventory deleted")
    def delete(self, inventory_id):
        """Delete an Inventory"""
        inv = Inventory.find(inventory_id)
        if inv:
            inv.delete()
        return "", status.HTTP_204_NO_CONTENT


######################################################################
# /api/inventory (collection)
######################################################################


@api.route("/inventory")
class InventoryCollection(Resource):
    """Handles the Inventory collection"""

    @api.expect(inventory_args, validate=True)
    @api.marshal_list_with(inventory_model)
    def get(self):
        """List all Inventory or filter"""
        args = inventory_args.parse_args()

        if args.get("category"):
            items = Inventory.find_by_category(args["category"])
        elif args.get("name"):
            items = Inventory.find_by_name(args["name"])
        elif args.get("available") is not None:
            items = Inventory.find_by_availability(args["available"])
        else:
            items = Inventory.all()

        return [i.serialize() for i in items], status.HTTP_200_OK

    @api.expect(inventory_create_model)
    @api.marshal_with(inventory_model, code=201)
    @api.response(409, "SKU already exists")
    @api.response(400, "Invalid data")
    def post(self):
        """Create a new Inventory item"""
        if request.content_type != "application/json":
            abort(
                status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                "Content-Type must be application/json",
            )
        data = api.payload

        if Inventory.query.filter(Inventory.sku == data.get("sku")).first():
            abort(status.HTTP_409_CONFLICT, f"SKU '{data.get('sku')}' already exists")

        # Validate quantity (must be int and >= 0)
        if data.get("quantity") is not None:
            if not isinstance(data["quantity"], int):
                abort(status.HTTP_400_BAD_REQUEST, "quantity must be an integer")
            if data["quantity"] < 0:
                abort(status.HTTP_400_BAD_REQUEST, "quantity must be non-negative")

        # Validate price (must be int/float and >= 0)
        if data.get("price") is not None:
            if not isinstance(data["price"], (int, float)):
                abort(status.HTTP_400_BAD_REQUEST, "price must be numeric")
            if data["price"] < 0:
                abort(status.HTTP_400_BAD_REQUEST, "price must be non-negative")

        inv = Inventory()
        inv.deserialize(data)
        inv.create()

        location_url = api.url_for(
            InventoryResource, inventory_id=inv.id, _external=True
        )
        return inv.serialize(), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# /api/inventory/<id>/purchase
######################################################################


@api.route("/inventory/<int:inventory_id>/purchase")
class InventoryPurchase(Resource):
    """Purchase inventory"""

    @api.marshal_with(inventory_model)
    @api.response(404, "Inventory not found")
    @api.response(409, "Inventory not available")
    def put(self, inventory_id):
        inv = Inventory.find(inventory_id)
        if not inv:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Inventory with id {inventory_id} not found.",
            )

        if not inv.available:
            abort(
                status.HTTP_409_CONFLICT,
                f"Inventory with id {inventory_id} is not available.",
            )

        inv.available = False
        inv.update()
        return inv.serialize(), status.HTTP_200_OK


######################################################################
# /api/inventory/<id>/restock-status
######################################################################


@api.route("/inventory/<int:inventory_id>/restock-status")
class InventoryRestockStatus(Resource):
    """Restock status endpoint"""

    @api.response(404, "Inventory not found")
    def get(self, inventory_id):
        inv = Inventory.find(inventory_id)
        if not inv:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Inventory with id {inventory_id} was not found",
            )

        return {
            "id": inv.id,
            "quantity": inv.quantity,
            "restock_level": inv.restock_level,
            "stock_status": inv.stock_status,
        }, status.HTTP_200_OK


######################################################################
# Helper: Content Type Check
######################################################################
def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Unsupported media type: {content_type}. Must be {media_type}",
    )
