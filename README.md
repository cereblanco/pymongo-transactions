# MongoDB Transactions

```python
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


def sample_transaction(sku: str, qty: int):
    init_database()
    # https://pymongo.readthedocs.io/en/stable/api/pymongo/client_session.html
    # 1. Increments orders by 100
    # 2. Decrements inventory by 100
    # 3. If either 1 of 2 fails, then the transaction should be aborted
    with get_client().start_session() as session:
        session.with_transaction(lambda session: increment_orders_decrement_inventory_callback(session, sku=sku, qty=qty))

    print("Successful transaction!")


def increment_orders_decrement_inventory_callback(session, sku=sku, qty=qty):
    orders = session.client.get_database().orders
    inventory = session.client.get_database().inventory

    # decrements 100 items from inventory
    inventory.update_one(
        {"sku": "abc123", "qty": {"$gte": qty}},
        {"$inc": {"qty": -qty}},
        session=session,
    )
    # increments 100 items to orders
    orders.update_one({"sku": sku, {"$inc": {"qty": 100}}, session=session)

```

## Run example
```bash
make sample_transaction
```
- executes sample transaction


## Test
```bash
make test
```
- executes sample transaction
- make sure the correct data were created/updated in the database collections

## Others
```bash
make up_database
```
- spins up the mongodb replica set container

```bash
make up
```
- spins up the mongodb replica set and opens pymongo-app's bash

```bash
make down
```
- stops the mongodb and pymongo-app containers