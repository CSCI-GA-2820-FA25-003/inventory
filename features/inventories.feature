Feature: Admin can create inventory items via the web UI
  As an Admin
  I want to create inventory items using a simple web page
  So that I can manage product availability and support order creation

  Background:
    Given the Create Inventory page is open

  Scenario: Create succeeds with valid data
    When I fill the form with:
      | name     | Demo Item |
      | sku      | DEMO-0001 |
      | quantity | 5         |
      | category | gadgets   |
      | description | small demo |
      | price    | 12.50     |
      | available | true     |
    And I submit the form
    Then I should see a success status 201
    And I should see the response containing "DEMO-0001"

  Scenario: Create fails with duplicate SKU
    When I fill the form with:
      | name     | First Item |
      | sku      | DUP-0001   |
      | quantity | 1          |
      | category | test       |
      | description | first   |
      | price    | 1.00       |
      | available | true      |
    And I submit the form
    Then I should see a success status 201
    # Try creating the same SKU again
    When I fill the form with:
      | name     | Second Item |
      | sku      | DUP-0001    |
      | quantity | 2           |
      | category | test        |
      | description | second   |
      | price    | 2.00        |
      | available | true       |
    And I submit the form
    Then I should see a failure status 409
    And I should see the response containing "already exists"

Scenario: Update an inventory
    When I visit the "Home Page"
    And I set the "Name" to "First Item"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "First Item" in the "Name" field
    And I should see "test" in the "Category" field
    When I change "Name" to "Third Item"
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Third Item" in the "Name" field
    When I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Third Item" in the results
    And I should not see "First Item" in the results

  Scenario: Read an existing inventory item
    When I visit the "Home Page"
    And I enter "First Item" into the "Name" field
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Name" in the results
    And I should see "Category" in the results

  Scenario: Delete an existing inventory item
    When I visit the "Home Page"
    And I set the "Name" to "First Item"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "First Item" in the "Name" field
    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Delete" button
    Then I should see the message "Success"
    When I press the "Clear" button
    And I set the "Name" to "First Item"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should not see "First Item" in the results

  Scenario: List inventory items
    When I visit the "Home Page"
    And I press the "List" button
    Then I should see the message "Success"
    And I should see "First Item" in the results

  Scenario: Query inventory items by category
    When I visit the "Home Page"
    And I set the "Category" to "test"
    And I press the "Query" button
    Then I should see the message "Success"
    And I should see "test" in the results

  Scenario: Perform an action on an inventory item
    When I visit the "Home Page"
    And I set the "Name" to "First Item"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "First Item" in the "Name" field
    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Action" button
    Then I should see the message "Success"
