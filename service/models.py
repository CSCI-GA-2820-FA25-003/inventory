"""
Models for Inventory

All of the models are stored in this module
"""

import logging
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class Inventory(db.Model):
    """
    Class that represents a Inventory
    """

    ##################################################
    # Table Schema
    ##################################################

    id = db.Column(db.Integer, primary_key=True)

    # core product info
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
    sku = db.Column(db.String(50), nullable=False, unique=True)

    # inventory & pricing
    quantity = db.Column(db.Integer, nullable=False, default=0)
    price = db.Column(db.Numeric(10, 2))

    # availability
    available = db.Column(db.Boolean, nullable=False, default=True)

    # timestamps
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    last_updated = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )

    def __repr__(self):
        return f"<Inventory {self.name} id=[{self.id}]>"

    def create(self):
        """
        Creates a Inventory to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # pylint: disable=invalid-name
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self) -> None:
        """
        Updates a Inventory to the database
        """
        logger.info("Saving %s", self.name)
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes a Inventory from the data store"""
        logger.info("Deleting %s", self.name)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes an Inventory into a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "sku": self.sku,
            "quantity": self.quantity,
            "price": float(self.price) if self.price else None,
            "available": self.available,
            "created_at": self.created_at,
            "last_updated": self.last_updated,
        }

    def deserialize(self, data):
        """
        Deserializes a Inventory from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            self.category = data.get("category")
            self.description = data.get("description")
            self.sku = data["sku"]
            self.quantity = data["quantity"]
            self.price = data.get("price")
            self.available = data.get("available", True)
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Inventory: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Inventory: body of request contained bad or no data "
                + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls) -> list:
        """Returns all of the Inventory in the database"""
        logger.info("Processing all Inventory")
        return cls.query.all()

    @classmethod
    def find(cls, inventory_id: int):
        """Finds a Inventory by it's ID

        :param inventory_id: the id of the Inventory to find
        :type inventory_id: int

        :return: an instance with the inventory_id, or None if not found
        :rtype: Inventory

        """
        logger.info("Processing lookup for id %s ...", inventory_id)
        return cls.query.session.get(cls, inventory_id)

    @classmethod
    def find_by_name(cls, name: str) -> list:
        """Returns all Inventory with the given name

        :param name: the name of the Inventory you want to match
        :type name: str

        :return: a collection of Inventory with that name
        :rtype: list

        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)

    @classmethod
    def find_by_category(cls, category: str) -> list:
        """Returns all of the Inventory in a category

        :param category: the category of the Inventory you want to match
        :type category: str

        :return: a collection of Inventory in that category
        :rtype: list

        """
        logger.info("Processing category query for %s ...", category)
        return cls.query.filter(cls.category == category)

    @classmethod
    def find_by_availability(cls, available: bool = True) -> list:
        """Returns all Inventory by their availability

        :param available: True for inventorys that are available
        :type available: str

        :return: a collection of Inventory that are available
        :rtype: list

        """
        if not isinstance(available, bool):
            raise TypeError("Invalid availability, must be of type boolean")
        logger.info("Processing available query for %s ...", available)
        return cls.query.filter(cls.available == available)
