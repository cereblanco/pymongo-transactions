import os

import pymongo

MONGODB_URL = os.getenv("MONGODB_URL")

_client = None


def get_client() -> pymongo.client_session.ClientSession:
    global _client
    if _client is None:
        _client = pymongo.MongoClient(host=MONGODB_URL)
    return _client


def init_database():
    # TODO: create a migration script for creating db and its collections
    orders = get_client().get_database().orders
    inventory = get_client().get_database().inventory

    orders.delete_many({})
    inventory.delete_many({})

    # suppose inventory has 200 items of abc123
    inventory.insert_one({"sku": "abc123", "qty": 200})
    # suppose orders for abc123 is 0 yet
    orders.insert_one({"sku": "abc123", "qty": 0})


def sample_transaction():
    init_database()
    # https://pymongo.readthedocs.io/en/stable/api/pymongo/client_session.html
    # 1. Increments orders by 100
    # 2. Decrements inventory by 100
    # 3. If either 1 of 2 fails, then the transaction should be aborted
    with get_client().start_session() as session:
        session.with_transaction(increment_orders_decrement_inventory_callback)

    print("Successful transaction!")


def increment_orders_decrement_inventory_callback(session):
    orders = session.client.get_database().orders
    inventory = session.client.get_database().inventory

    # increments 100 items to orders
    orders.update_one({"sku": "abc123"}, {"$inc": {"qty": 100}}, session=session)

    # decrements 100 items from inventory
    inventory.update_one(
        {"sku": "abc123", "qty": {"$gte": 0}},
        {"$inc": {"qty": -100}},
        session=session,
    )
