# tests/test_bdd_endpoints.py
# Cover BDD/UI-only routes

import uuid
import pytest
from wsgi import app  # uses create_app() and registers routes
from service.common import status


@pytest.fixture()
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_bdd_create_inventory_success(client):
    """POST /inventories returns 201 with Location and JSON body"""
    sku = f"BDD-{uuid.uuid4().hex[:8]}"
    payload = {
        "name": "BDD Item",
        "sku": sku,
        "quantity": 3,
        "category": "gadgets",
        "description": "created by pytest",
        "price": 9.99,
        "available": True,
    }
    resp = client.post("/inventories", json=payload)
    assert resp.status_code == status.HTTP_201_CREATED
    assert "Location" in resp.headers

    data = resp.get_json()
    assert data["sku"] == sku
    assert data["name"] == "BDD Item"
    inv_id = data["id"]

    # GET /inventories/<id> returns 200 and the same item
    resp_get = client.get(f"/inventories/{inv_id}")
    assert resp_get.status_code == status.HTTP_200_OK
    got = resp_get.get_json()
    assert got["id"] == inv_id
    assert got["sku"] == sku


def test_bdd_create_inventory_duplicate_sku(client):
    """Second POST with same SKU returns 409"""
    sku = f"DUP-{uuid.uuid4().hex[:8]}"
    payload = {"name": "First", "sku": sku, "quantity": 1, "available": True}
    first = client.post("/inventories", json=payload)
    assert first.status_code == status.HTTP_201_CREATED
    second = client.post("/inventories", json=payload)
    assert second.status_code == status.HTTP_409_CONFLICT


def test_bdd_create_inventory_page(client):
    """GET /inventories/new renders the HTML form"""
    resp = client.get("/inventories/new")
    assert resp.status_code == status.HTTP_200_OK
    assert b"<form" in resp.data
    assert b"Create" in resp.data


def test_health_endpoint(client):
    """GET /health returns OK to bump coverage on health probe"""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "OK"}


# -------- New negative tests to cover validation branches --------


def test_bdd_create_inventory_requires_json(client):
    """Non-JSON Content-Type should return 415 (unsupported media type)."""
    resp = client.post(
        "/inventories", data="{}", headers={"Content-Type": "text/plain"}
    )
    assert resp.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    msg = resp.get_json()
    assert "Content-Type must be application/json" in msg.get("message", "")


def test_bdd_create_inventory_missing_name(client):
    """Missing 'name' should return 400."""
    payload = {
        "sku": f"NO-NAME-{uuid.uuid4().hex[:6]}",
        "quantity": 1,
        "available": True,
    }
    resp = client.post("/inventories", json=payload)
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


def test_bdd_create_inventory_missing_sku(client):
    """Missing 'sku' should return 400."""
    payload = {"name": "No SKU", "quantity": 1, "available": True}
    resp = client.post("/inventories", json=payload)
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


def test_bdd_create_inventory_quantity_negative(client):
    """Negative quantity should return 400."""
    payload = {"name": "Bad Q", "sku": f"NEGQ-{uuid.uuid4().hex[:6]}", "quantity": -1}
    resp = client.post("/inventories", json=payload)
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


def test_bdd_create_inventory_quantity_not_int(client):
    """Non-integer quantity should return 400."""
    payload = {
        "name": "Bad Q",
        "sku": f"NONINT-{uuid.uuid4().hex[:6]}",
        "quantity": "x",
    }
    resp = client.post("/inventories", json=payload)
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


def test_bdd_create_inventory_price_negative(client):
    """Negative price should return 400."""
    payload = {
        "name": "Bad Price",
        "sku": f"NEG-${uuid.uuid4().hex[:6]}",
        "quantity": 1,
        "price": -0.01,
    }
    resp = client.post("/inventories", json=payload)
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


def test_bdd_create_inventory_price_not_number(client):
    """Non-numeric price should return 400."""
    payload = {
        "name": "Bad Price",
        "sku": f"NANNUM-{uuid.uuid4().hex[:6]}",
        "quantity": 1,
        "price": "abc",
    }
    resp = client.post("/inventories", json=payload)
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


def test_bdd_get_inventory_v2_not_found(client):
    """GET /inventories/<id> 404 branch."""
    resp = client.get("/inventories/999999999")
    assert resp.status_code == status.HTTP_404_NOT_FOUND
