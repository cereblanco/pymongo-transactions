import os
from collections import OrderedDict

import pymongo

MONGODB_URL = os.getenv("MONGODB_URL")

_client = None


def get_client() -> pymongo.client_session.ClientSession:
    global _client
    if _client is None:
        _client = pymongo.MongoClient(host=MONGODB_URL)
    return _client


def create_schema_validation_for_inventory():
    """
    ---------------------------------------------
    WARNING: Do not copy! For demo purposes only!
    It is recommended that you create separate module for database migration/setting validation rules.
    ---------------------------------------------
    - For this demo, this schema validation
    - makes sure `sku` and `qty` are required fields
    - makes sure that minimum value for `qty` is 0
    - Thus if we update `inventory` with a negative value, it should trigger validation error in a transaction
    """
    get_client().get_database().inventory.drop()
    get_client().get_database().create_collection("inventory")
    json_schema = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["sku", "qty"],
            "properties": {
                "name": {"bsonType": "string"},
                "qty": {"bsonType": "int", "minimum": 0},
            },
        }
    }
    cmd = OrderedDict(
        [("collMod", "inventory"), ("validator", json_schema), ("validationLevel", "moderate")]
    )
    get_client().get_database().command(cmd)


def init_database():
    create_schema_validation_for_inventory()

    # TODO: create a migration script for creating db and its collections
    orders = get_client().get_database().orders
    inventory = get_client().get_database().inventory

    orders.delete_many({})
    inventory.delete_many({})

    # suppose inventory has 200 items of abc123
    inventory.insert_one({"sku": "abc123", "qty": 200})
    # suppose orders for abc123 is 0 yet
    orders.insert_one({"sku": "abc123", "qty": 0})


def sample_transaction(sku: str, qty: int):
    init_database()
    # https://pymongo.readthedocs.io/en/stable/api/pymongo/client_session.html
    # 1. Increments orders by 100
    # 2. Decrements inventory by 100
    # 3. If either 1 of 2 fails, then the transaction should be aborted
    with get_client().start_session() as session:
        session.with_transaction(
            lambda session: increment_orders_decrement_inventory_callback(
                session, sku=sku, qty=qty
            )
        )
    print("Successful transaction!")


def increment_orders_decrement_inventory_callback(session, sku: str, qty: int):
    orders = get_client().get_database().orders
    inventory = get_client().get_database().inventory

    # increments 100 items to orders
    orders.update_one({"sku": sku}, {"$inc": {"qty": qty}}, session=session)

    # decrements 100 items from inventory
    inventory.update_one(
        {"sku": sku},
        {"$inc": {"qty": -(qty)}},
        session=session,
    )
