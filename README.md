# Inventory Services

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

## Overview

This project is designed to monitor the inventory, which stores information such as name, category, quantity, price, description, and sku. The project can check the inventory is available or not as well. For users, the project supports operations such as create, read, update, list, and delete an inventory.

## Setup

Clone the code using the web URL via git bash:
```
https://github.com/CSCI-GA-2820-FA25-003/inventory.git
```
or SSH key:
```
git@github.com:CSCI-GA-2820-FA25-003/inventory.git
```
## To Use REST API Client

Use the URL:
```
http://localhost:8080/inventory
```

## To Edit an Inventory

The REST API Client has GET(read/list the inventory), POST(create), PUT(update), and DELETE functions.

### 1. Create an Inventory

Select POST function and make sure you have the inventory's name, category, available, quantity, price, description and sku. Using JSON and send the information.

e.g.:
```
{
  "name": "Nike Air jordan",
  "category": "Shoes",
  "available": true,
  "quantity": 10,
  "price": 200.99,
  "description": "Lightweight running shoes with.",
  "sku": "1210"
}
```

### 2. Read/List an Inventory

Select GET function and put the "id" behind the URL, then you can get the inventory's information.

```
http://localhost:8080/inventory/id
```
e.g.:
```
http://localhost:8080/inventory/75

and we get:
{
  "available": true,
  "category": "Shoes",
  "created_at": "Wed, 15 Oct 2025 16:48:44 GMT",
  "description": "Lightweight running shoes with.",
  "id": 75,
  "last_updated": "Wed, 15 Oct 2025 16:48:44 GMT",
  "name": "Nike Air jordan",
  "price": 200.99,
  "quantity": 10,
  "sku": "1210"
}
```

### 3. Update an Inventory

Select PUT function and update the information of the inventory, also need "id".

e.g.:
```
http://localhost:8080/inventory/75

{
  "name": "Nike Air jordan",
  "category": "Shoes",
  "available": true,
  "quantity": 20,              # update the quantity from 10 to 20
  "price": 200.99,
  "description": "Lightweight running shoes with.",
  "sku": "1210"
}

and we get:
{
  "available": true,
  "category": "Shoes",
  "created_at": "Wed, 15 Oct 2025 16:48:44 GMT",
  "description": "Lightweight running shoes with.",
  "id": 75,
  "last_updated": "Wed, 15 Oct 2025 17:48:13 GMT",
  "name": "Nike Air jordan",
  "price": 200.99,
  "quantity": 20,             # notice that the quantity has been updated
  "sku": "1210"
}
```
warning: sku number is unique, can not change one inventory's sku number to an already existed another inventory's sku number, that will be an error.


### 4. Delete an Inventory

Select DELETE function and delete the inventory of no need, also need "id".

e.g.:
```
http://localhost:8080/inventory/75

then the inventory "75" has been deleted.

when we GET "75" again, we will get:
{
  "error": "Not Found",
  "message": "404 Not Found: Inventory with id '75' was not found.",
  "status": 404
}
```

## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
pyproject.toml      - Poetry list of Python libraries required by your code

service/                   - service python package
├── __init__.py            - package initializer
├── config.py              - configuration parameters
├── models.py              - module with business models
├── routes.py              - module with service routes
└── common                 - common code package
    ├── cli_commands.py    - Flask command to recreate all tables
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/                     - test cases package
├── __init__.py            - package initializer
├── factories.py           - Factory for testing with fake objects
├── test_cli_commands.py   - test suite for the CLI
├── test_models.py         - test suite for business models
└── test_routes.py         - test suite for service routes
```

## License

Copyright (c) 2016, 2025 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
