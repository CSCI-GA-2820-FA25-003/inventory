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
