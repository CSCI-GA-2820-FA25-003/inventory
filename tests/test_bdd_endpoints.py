# tests/test_bdd_endpoints.py
# Cover BDD/UI-only routes (/inventories, /inventories/<id>, /inventories/new)

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
    assert "id" in data
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
    # Template is simple HTML; a 200 is sufficient, but we check for a <form>
    assert resp.status_code == status.HTTP_200_OK
    assert b"<form" in resp.data
    assert b"Create" in resp.data


def test_health_endpoint(client):
    """GET /health returns OK to bump coverage on health probe"""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "OK"}
