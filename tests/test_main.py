import os

import pytest
from bson.objectid import ObjectId
from pymongo_transactions.main import get_client, init_database, sample_transaction

import tests

TEST_MONGODB_URL = "mongodb://mongodb:27017/test"


@pytest.fixture(autouse=True)
def test_db(monkeypatch):
    monkeypatch.setenv("MONGODB_URL", TEST_MONGODB_URL)


def test_sample_transaction():
    assert os.getenv("MONGODB_URL") == TEST_MONGODB_URL

    inventory = get_client().get_database().inventory
    orders = get_client().get_database().orders

    sample_transaction()

    assert list(inventory.find({}, {"sku": 1, "qty": 1, "_id": 0})) == [
        {"sku": "abc123", "qty": 100}
    ]
    assert list(orders.find({}, {"sku": 1, "qty": 1, "_id": 0})) == [{"sku": "abc123", "qty": 100}]
