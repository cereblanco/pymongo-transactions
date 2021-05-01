import os

import pymongo
import pytest
from bson.objectid import ObjectId
from pymongo_transactions.main import get_client, init_database, sample_transaction

import tests

TEST_MONGODB_URL = "mongodb://mongodb:27017/test"

assert os.getenv("MONGODB_URL") == TEST_MONGODB_URL


@pytest.fixture(autouse=True)
def test_db(monkeypatch):
    monkeypatch.setenv("MONGODB_URL", TEST_MONGODB_URL)


def test_sample_transaction_success():

    inventory = get_client().get_database().inventory
    orders = get_client().get_database().orders

    sample_transaction(sku="abc123", qty=100)

    assert list(inventory.find({}, {"sku": 1, "qty": 1, "_id": 0})) == [
        {"sku": "abc123", "qty": 100}
    ]
    assert list(orders.find({}, {"sku": 1, "qty": 1, "_id": 0})) == [{"sku": "abc123", "qty": 100}]


def test_sample_transaction_failed():

    inventory = get_client().get_database().inventory
    orders = get_client().get_database().orders

    # try to order more than 200 qty, it will make {"sku":"abc123", "qty": -100}
    # which is not permitted since minimum value for `qty` is 0
    # the transaction will be aborted
    with pytest.raises(pymongo.errors.WriteError):
        sample_transaction(sku="abc123", qty=300)

    assert list(orders.find({}, {"sku": 1, "qty": 1, "_id": 0})) == [{"sku": "abc123", "qty": 0}]
    assert list(inventory.find({}, {"sku": 1, "qty": 1, "_id": 0})) == [
        {"sku": "abc123", "qty": 200}
    ]
