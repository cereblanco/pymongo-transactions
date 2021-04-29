# MongoDB Transactions

```

def transaction_callback(session):
    orders = session.client.get_database().orders
    inventory = session.client.get_database().inventory

    # increment 100 items to orders
    orders.update_one({"sku": "abc123"}, {"$inc": {"qty": 100}}, session=session)

    # decrement 100 items to inventory
    inventory.update_one(
        {"sku": "abc123", "qty": {"$gte": 0}},
        {"$inc": {"qty": -100}},
        session=session,
    )


def sample_transaction():
    init_database()
    # https://pymongo.readthedocs.io/en/stable/api/pymongo/client_session.html
    with get_client().start_session() as session:
        session.with_transaction(transaction_callback)

    print("Successful transaction!")

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
- make sure the correct date were created/updated in the database collections

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