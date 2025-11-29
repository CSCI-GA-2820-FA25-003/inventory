# features/steps/inventories_steps.py

import os
import uuid
from typing import Any
from behave import given, when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
ID_PREFIX = "inventory_"


def _open_create_page(context):
    """Navigate to the Create Inventory UI page."""
    context.browser.get(f"{BASE_URL}/inventories/new")


def _js_set_value(context, elem_id, value):
    """Set an input's value using JS and dispatch an input event, then verify."""
    context.browser.execute_script(
        "const el = document.getElementById(arguments[0]);"
        "if (!el) { throw new Error('Element not found: ' + arguments[0]); }"
        "el.value = arguments[1];"
        "el.dispatchEvent(new Event('input', {bubbles:true}));",
        elem_id,
        value or "",
    )
    WebDriverWait(context.browser, 5).until(
        lambda d: d.find_element(By.ID, elem_id).get_attribute("value") == (value or "")
    )


@given("the Create Inventory page is open")
def step_open_create_page(context):
    """Ensure the Create page is open and the submit button is present."""
    _open_create_page(context)
    WebDriverWait(context.browser, 15).until(
        EC.presence_of_element_located((By.ID, "submit"))
    )


@when("I fill the form with:")
def step_fill_form(context):
    """
    Fill the form with a data table having keys:
    name, sku, quantity, category, description, price, available
    Keys are trimmed and lower-cased to avoid whitespace/case issues.
    """
    data = {}
    for row in context.table:
        cells = list(row.cells)
        if len(cells) >= 2:
            key = cells[0].strip().lower()
            value = cells[1].strip()
            data[key] = value

    # Fallback for 'name': ensure it is never empty
    name_value = (data.get("name") or "").strip()
    if not name_value:
        # Deterministic-enough default that won't break duplicate-SKU scenario
        name_value = f"BDD Item {uuid.uuid4().hex[:6]}"

    _js_set_value(context, "name", name_value)
    _js_set_value(context, "sku", data.get("sku", ""))
    _js_set_value(context, "quantity", data.get("quantity", "5"))
    _js_set_value(context, "category", data.get("category", "gadgets"))
    _js_set_value(context, "description", data.get("description", "autofilled by test"))
    _js_set_value(context, "price", data.get("price", "12.50"))

    # Checkbox: available (default true)
    available_str = (data.get("available", "true") or "true").strip().lower()
    available_bool = available_str in ("true", "yes", "1", "on")
    context.browser.execute_script(
        "const el = document.getElementById('available');"
        "if (!!el && el.checked !== arguments[0]) { el.click(); }",
        available_bool,
    )
    WebDriverWait(context.browser, 3).until(
        lambda d: d.find_element(By.ID, "available").is_selected() == available_bool
    )


@when("I submit the form")
def step_submit_form(context):
    """
    Click the button and wait until the result area begins with 'Status '.
    """
    button = context.browser.find_element(By.ID, "submit")
    context.browser.execute_script(
        "arguments[0].scrollIntoView({block:'center'});", button
    )
    button.click()
    WebDriverWait(context.browser, 30).until(
        lambda d: d.find_element(By.ID, "result").text.strip().startswith("Status ")
    )


@then("I should see a success status 201")
def step_see_201(context):
    """Assert that the result area begins with Status 201; print result for diagnostics."""
    text = context.browser.find_element(By.ID, "result").text
    assert text.startswith("Status 201"), f"Expected 201, got:\n{text}"


@then("I should see a failure status 409")
def step_see_409(context):
    """Assert that the result area begins with Status 409; print result for diagnostics."""
    text = context.browser.find_element(By.ID, "result").text
    assert text.startswith("Status 409"), f"Expected 409, got:\n{text}"


@then('I should see the response containing "{snippet}"')
def step_response_contains(context, snippet):
    """Assert that the result area contains a specific substring."""
    text = context.browser.find_element(By.ID, "result").text
    assert snippet in text, f"Did not find '{snippet}' in response:\n{text}"


@when("I return to the Create Inventory page")
def step_return_page(context):
    """Helper step to navigate back to the Create page if needed."""
    _open_create_page(context)


@when('I visit the "Home Page"')
def step_visit_home(context: Any) -> None:
    """Open the application's home page."""
    context.driver.get(context.base_url)


@when('I enter "{text_string}" into the "{element_name}" field')
def step_set_field(context: Any, element_name: str, text_string: str) -> None:
    """Type into a text input field based on its element name."""
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    element.clear()
    element.send_keys(text_string)


@when('I press the "{button}" button')
def step_press_button(context: Any, button: str) -> None:
    """Click a button whose ID is based on its label text."""
    button_id = button.lower().replace(" ", "_") + "-btn"
    context.driver.find_element(By.ID, button_id).click()


@then('I should see the message "{message}"')
def step_see_message(context: Any, message: str) -> None:
    """Wait until a flash message with given text appears."""
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "flash_message"), message
        )
    )
    assert found


@then('I should see "{name}" in the results')
def step_see_results(context: Any, name: str) -> None:
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "search_results"), name
        )
    )
    assert found


@when("I copy the id from the create result")
def step_copy_id_from_create(context):
    """Extract the created inventory ID from the 'result' pre block."""
    text = context.browser.find_element(By.ID, "result").text
    # Find the first occurrence of `"id": <number>` in JSON
    import re

    match = re.search(r'"id"\s*:\s*(\d+)', text)
    assert match, f"Could not find an 'id' in result:\n{text}"
    context.copied_id = match.group(1)


@when('I enter the copied id into the "read-id" field')
def step_enter_copied_id(context):
    """Fill the read-id input field with the previously copied ID."""
    assert hasattr(context, "copied_id"), "No copied_id found. Did you call copy step?"
    elem = context.browser.find_element(By.ID, "read-id")
    elem.clear()
    elem.send_keys(context.copied_id)


@then('I should see "{value}" in the read results')
def step_see_in_read_results(context, value):
    """Assert that the read-result block contains a given value."""
    text = context.browser.find_element(By.ID, "read-result").text
    assert value in text, f"Expected '{value}' in read results, got:\n{text}"


@when('I enter the copied id into the "status-id" field')
def step_enter_copied_id_status(context):
    elem = context.browser.find_element(By.ID, "status-id")
    elem.clear()
    elem.send_keys(context.copied_id)


@then('I should see "{value}" in the status results')
def step_see_status_result(context, value):
    text = context.browser.find_element(By.ID, "status-result").text
    assert value in text, f"Expected '{value}' in restock results, got:\n{text}"
